from os.path import abspath
from PIL import Image
import threading
from logging import getLogger
import logging
from sys import argv

logger = getLogger(__name__)
import vault
SDKPath='udSDK'
vault.LoadUdSDK(SDKPath)

class VDKEasyRenderer():
  def __init__(self,
               userName, password, serverPath="https://earth.vault.euclideon.com",
               width=1280, height=720, clearColour=0,
               models=[]
               ):
    self.vaultContext = vault.udContext()
    self.vaultRenderer = vault.udRenderContext()
    t = threading.Thread(target=self.log_in, args=[userName, password, serverPath])
    t.start()

    self.vaultModels = []
    self.renderInstances = []
    for model in models:
      self.add_model(model)

    self.renderViews = []
    self.renderSettings = {} #list of settings corresponding to the
    t.join()
    self.add_view()

  def add_model(self, fileName):
    """
    Parameters
    ----------
    fileName: the path to UDS file to be added to the render list
    """
    model = vault.udPointCloud()
    try:
      model.Load(self.vaultContext, fileName)
    except vault.UdException as e:
      logger.warning("Load model {} failed: {}".format(fileName, e.args[0]))
      return
    self.vaultModels.append(model)
    self.renderInstances.append(vault.udRenderInstance(model))
    #Here we are setting the default scaling of the model such that the smallest dimension is 1 unit
    self.renderInstances[-1].scaleMode = 'minDim'

  def remove_model(self, ind=-1):
    self.renderInstances.pop(ind)
    self.vaultModels.pop(ind)

  def log_in(self, userName: str, userPass: str, serverPath: str,appName = "Python Sample") -> None:

    logger.info('Logging in to vault server...')
    self.vaultContext.username = userName
    self.vaultContext.url = serverPath
    self.vaultContext.appName = appName

    try:
      logger.log(logging.INFO, "Attempting to resume session")
      self.vaultContext.try_resume(tryDongle=True)
    except vault.UdException as e:
      logger.log(logging.INFO, "Resume failed: ({})\n Attempting to connect new session...".format(str(e.args[0])))
      self.vaultContext.Connect(password=userPass)
    self.vaultRenderer.Create(self.vaultContext)
    logger.log(logging.INFO, 'Logged in')

  def add_view(self, x=0, y=-5, z=0, roll=0, pitch=0, yaw=0):
    view = vault.udRenderTarget(context=self.vaultContext, renderContext=self.vaultRenderer)
    view.set_view(x, y, z, roll, pitch, yaw)
    self.renderViews.append(view)
    self.renderSettings[view] = vault.udRenderSettings()
    return view

  def main_view(self):
    return self.renderViews[0]

  def render_view(self, view):
    try:
      #This converts our python list into an array of vdkRenderInstance pointers that can be understood by VDK:
      renderInstancesCArray = (vault.udRenderInstance * len(self.renderInstances))(*self.renderInstances)
      self.vaultRenderer.Render(view, renderInstancesCArray, renderSettings=self.renderSettings[view])
    except vault.UdException as e:
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
    for model in self.vaultModels:
      model.Unload()

#test code generating different views of the cube:
if __name__ == "__main__":
  modelFile = abspath("../../samplefiles/DirCube.uds")
  if len(argv) < 3:
    logger.error("Euclideon username and password must be provided")

  if len(argv) > 3:
    server = argv[3]
  else:
    server = "https://earth.vault.euclideon.com"

  renderer = VDKEasyRenderer(argv[1], argv[2], serverPath=server, models=[modelFile])
  renderer.add_view(5, 0, 0, 0, 0, -3.14/2)
  renderer.add_view(0, 5, 0, 0, 0, 3.14)
  renderer.add_view(-5, 0, 0, 0, 0, 3.14/2)
  renderer.add_view(0, -5, 5, -3.14/4, 0, 0)
  renderer.add_view(-5, 0, 5, 0, -3.14/4, 3.14/2)
  renderer.add_view(5, 0, 5, 0, -3.14/4, -3.14/2)
  renderer.add_view(0, 5, 5, -3.14/4, 0, 3.14)
  renderer.render_to_file("testIm")
