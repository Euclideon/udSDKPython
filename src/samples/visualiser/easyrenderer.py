import logging
import threading
from logging import getLogger
from os.path import abspath
from sys import argv

from PIL import Image

logger = getLogger(__name__)
import udSDK
import sampleLogin
SDKPath='./udSDK'
udSDK.LoadUdSDK(SDKPath)

class UDEasyRenderer():
  def __init__(self,
               width=1280, height=720, clearColour=0,
               models=[]
               ):
    self.context = udSDK.udContext()
    self.udRenderer = udSDK.udRenderContext()
    t = threading.Thread(target=self.log_in, args=[])
    t.start()

    self.pointclouds = []
    self.renderInstances = []
    for model in models:
      self.add_model(model)

    self.renderViews = []
    self.renderSettings = {} #list of settings corresponding to each
    t.join()
    self.add_view()

  def add_model(self, fileName):
    """
    Parameters
    ----------
    fileName: the path to UDS file to be added to the render list
    """
    model = udSDK.udPointCloud()
    try:
      model.Load(self.context, fileName)
    except udSDK.UdException as e:
      logger.warning("Load model {} failed: {}".format(fileName, e.args[0]))
      return
    self.pointclouds.append(model)
    self.renderInstances.append(udSDK.udRenderInstance(model))
    #Here we are setting the default scaling of the model such that the smallest dimension is 1 unit
    self.renderInstances[-1].scaleMode = 'minDim'

  def remove_model(self, ind=-1):
    self.renderInstances.pop(ind)
    self.pointclouds.pop(ind)

  def log_in(self, serverPath="https://udcloud.euclideon.com",appName = "Python Sample") -> None:

    logger.info('Logging in to udStream server...')
    self.context.url = serverPath
    self.context.appName = appName

    sampleLogin.log_in_sample(self.context)
    self.udRenderer.Create(self.context)
    logger.log(logging.INFO, 'Logged in')

  def add_view(self, width=1028, height=512, x=0, y=-5, z=0, roll=0, pitch=0, yaw=0):
    view = udSDK.udRenderTarget(width=width, height=height, context=self.context, renderContext=self.udRenderer)
    view.set_view(x, y, z, roll, pitch, yaw)
    self.renderViews.append(view)
    self.renderSettings[view] = udSDK.udRenderSettings()
    return view

  def main_view(self):
    return self.renderViews[0]

  def render_view(self, view:udSDK.udRenderTarget):
    try:
      #This converts our python list into an array of udRenderInstance pointers that can be understood by udSDK:
      renderInstancesCArray = (udSDK.udRenderInstance * len(self.renderInstances))(*self.renderInstances)
      self.udRenderer.Render(view, renderInstancesCArray, renderSettings=self.renderSettings[view])
    except udSDK.UdException as e:
      logger.log(logging.INFO, 'Render failed: '+e.args[0])

  def render_all(self):
    for view in self.renderViews:
      self.render_view(view)

  def render_to_file(self, outFile: str):
    for x in range(10):
      self.render_all()
    i=0
    for view in self.renderViews:
      name = outFile + '_'+str(i)+'.png'
      Image.frombuffer("RGBA", (view.width, view.height), view.colourBuffer, "raw", "RGBA", 0, 1).save(name)
      i += 1

  def __del__(self):
    for model in self.pointclouds:
      model.Unload()

#test code generating different views of the cube:
if __name__ == "__main__":
  modelFile = abspath("./samplefiles/DirCube.uds")
  if len(argv) < 3:
    logger.error("Euclideon username and password must be provided")

  if len(argv) > 3:
    server = argv[3]
  else:
    server = "https://udstream.euclideon.com"

  renderer = UDEasyRenderer(argv[1], argv[2], serverPath=server, models=[modelFile])
  renderer.add_view(5, 0, 0, 0, 0, -3.14/2)
  renderer.add_view(0, 5, 0, 0, 0, 3.14)
  renderer.add_view(-5, 0, 0, 0, 0, 3.14/2)
  renderer.add_view(0, -5, 5, -3.14/4, 0, 0)
  renderer.add_view(-5, 0, 5, 0, -3.14/4, 3.14/2)
  renderer.add_view(5, 0, 5, 0, -3.14/4, -3.14/2)
  renderer.add_view(0, 5, 5, -3.14/4, 0, 3.14)
  renderer.render_to_file("testIm")
