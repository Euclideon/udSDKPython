import math
import sys
import threading

import IPython
import numpy
from PIL import Image

import udSDK
from easyrenderer import UDEasyRenderer
import pyglet.window.key as keyboard
import pyglet
from camera import *
from os.path import abspath
import numpy as np
from sys import argv
import logging



class UDViewPort():
  """This class represents the quad that the UDS render is blitted to,
  it handles the camera information associated with the view it controls
  """
  def __init__(self, width, height, x, y, parent, skyboxImage="WaterClouds.jpg"):

    self.parent = parent

    self.set_rectangle(width, height, x, y)
    self._view = parent.renderer.add_view(width, height)
    #for openGL to properly deal with our texture the render must be a power of 2:
    tw = 2**(int(np.log2(width)))
    th = 2**(int(np.log2(height)))
#    self.set_rectangle(tw, th , x, y)
    self._view.set_size(tw, th)
    self.camera = Camera(self._view)
    self.bindingMap = \
      {
        keyboard.W: self.camera.set_forwardPressed,
        keyboard.S: self.camera.set_backPressed,
        keyboard.D: self.camera.set_rightPressed,
        keyboard.A: self.camera.set_leftPressed,
        keyboard.E: self.camera.set_upPressed,
        keyboard.C: self.camera.set_downPressed,
        keyboard.LSHIFT: self.camera.set_shiftPressed,
        keyboard.LCTRL: self.camera.set_ctrlPressed,
        keyboard.O: self.camera.set_zoomInPressed,
        keyboard.P: self.camera.set_zoomOutPressed,
      }
    self.tex = pyglet.image.Texture.create(width, height)
    self.make_vertex_list()
    self.skyboxTexture = pyglet.image.load(skyboxImage).get_texture(())
    parent.udViewPorts.append(self)

  def set_rectangle(self, width=None, height=None, bottomLeftX=None, bottomLeftY=None):
    if width is not None:
      self._width = width
    if height is not None:
      self._height = height
    if bottomLeftX is not None:
      self._anchorX = bottomLeftX
    if bottomLeftY is not None:
      self._anchorY = bottomLeftY
    self.corners =\
    (  # vertices are represented as 2 element floats
      self._anchorX, self._anchorY,
      (self._width + self._anchorX), self._anchorY,
      (self._width + self._anchorX), (self._height + self._anchorY),
      self._anchorX, (self._height + self._anchorY),
    )
    self.make_vertex_list()

  def set_camera(self, cameraType = OrthoCamera, bindingMap = None):
    self.camera.__class__ = cameraType
    self.camera.reset_projection()
    self.camera.on_cast()
    if bindingMap is None:#reset to default
      self.bindingMap = \
        {
          keyboard.W: self.camera.set_forwardPressed,
          keyboard.S: self.camera.set_backPressed,
          keyboard.D: self.camera.set_rightPressed,
          keyboard.A: self.camera.set_leftPressed,
          keyboard.E: self.camera.set_upPressed,
          keyboard.C: self.camera.set_downPressed,
          keyboard.LSHIFT: self.camera.set_shiftPressed,
          keyboard.LCTRL: self.camera.set_ctrlPressed,
          keyboard.O: self.camera.set_zoomInPressed,
          keyboard.P: self.camera.set_zoomOutPressed,
        }
    else:
      self.bindingMap = bindingMap

  def make_vertex_list(self):
    self._vertex_list = pyglet.graphics.vertex_list\
    (4,
      ('v2f',
        self.corners
      ),
      ('t2f',
        (  # texture coordinates as a float,
          0.0, 1.0,
          1.0, 1.0,
          1.0, 0.0,
          0.0, 0.0,
        )
      )
    )

  def render_skybox(self):
    import pyglet.gl as gl
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    tex = self.skyboxTexture
    #divide the skybox into 360 degrees horizontally and 180 vertically
    #calculate the amount of skybox to display based on FOV:
    hRat = self.camera.FOV / 2 / 360
    vRat = np.arctan(np.tan(hRat*2*np.pi)*self._height/self._width)
    ts =\
      (  # texture coordinates as a float,
        self.camera.theta / 2 / np.pi + hRat, -self.camera.phi / np.pi - vRat / 2,
        self.camera.theta / 2 / np.pi - hRat, -self.camera.phi / np.pi - vRat / 2,
        self.camera.theta / 2 / np.pi - hRat, -self.camera.phi / np.pi + vRat / 2,
        self.camera.theta / 2 / np.pi + hRat, -self.camera.phi / np.pi + vRat / 2,
      )
    vList = pyglet.graphics.vertex_list(4,('v2f', self.corners), ('t2f',ts))
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex.id)
    vList.draw(pyglet.gl.GL_QUADS)
    gl.glDisable(gl.GL_TEXTURE_2D)


  def render_uds(self, dt):
    import pyglet.gl as gl
    self.parent.switch_to()
    from pyglet.gl import glEnable, glDisable, GL_TEXTURE_2D, glBindTexture
    self.camera.update_position(dt)
    self.parent.renderer.render_view(self._view)
    im = pyglet.image.ImageData(self._view.width, self._view.height, 'BGRA', self._view.colourBuffer)
    tex = im.get_texture()
    #depth = pyglet.image.ImageData(self._view.width,self._view.height,'RGBA',self._view.depthBuffer)
    #TODO: add depth texture to quad
    #deptht = depth.get_texture()
    #gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, deptht.id)
    #gl.glRenderbufferStorage(gl.GL_RENDERBUFFER,gl.GL_DEPTH_COMPONENT32F,self._view.width,self._view.height)
    #gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER,gl.GL_DEPTH_ATTACHMENT,gl.GL_RENDERBUFFER,deptht.id)
    #gl.glFramebufferTexture(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0,tex.id)

    self.render_skybox()
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex.id)
    self._vertex_list.draw(pyglet.gl.GL_QUADS)
    glDisable(GL_TEXTURE_2D)


  def write_to_image(self, name='a.png'):
    arr = []
    #convert colour buffer from BGRA to RGBA
    #i.e. we are switching the B and R channels by bit shifting
    for pix in self._view.colourBuffer:
      pix = numpy.int32(pix)
      pix=(pix>>24 & 0xFF)<<24 |(pix>>16 & 0xFF)<<0 |(pix>>8 & 0xFF)<<8 | (pix&0xFF)<<16
      arr.append(pix)
    #Image.frombuffer("RGBA", (self._view.width, self._view.height), arr, "raw", "RGBA", 0, 1).save(name)
    arr = numpy.array(arr)
    Image.frombuffer("RGBA", (self._view.width, self._view.height), arr.flatten(), "raw", "RGBA", 0, 1).save(name)
    #Image.fromarray(arr.flatten(), "RGBA")


class AppWindow(pyglet.window.Window):
  """
  Main window class, handles events and contains all views as
  well as the UDS easyrenderer
  """
  def __init__(self, username, password, *args, resolution=(1024+50, 512+100), offset=(50, 25), **kwargs):
    super(AppWindow, self).__init__(*resolution, file_drops=True, resizable=True)
    self.renderer = UDEasyRenderer(username, password, models=[], serverPath="https://udstream.euclideon.com")
    self.set_caption("Euclideon udSDK Python")
    self.udViewPorts = []
    self.viewPort = UDViewPort(resolution[0] - 50, resolution[1] - 100, offset[0], offset[1], self)
    self.cameraTypes = [RecordCamera, OrthoCamera, OrbitCamera]
    self.cameraTypeInd = 0
    self.imageCounter = 0
    self.mousePosition = (0, 0)

  def on_file_drop(self, x, y, paths):
    for path in paths:
      self.renderer.add_model(path)

  def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
    for viewport in self.udViewPorts:
      viewport.camera.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

  def on_key_press(self, symbol, modifiers):
    if symbol == keyboard.TAB:
      self.cameraTypeInd += 1
      self.cameraTypeInd %= len(self.cameraTypes)
      self.viewPort.set_camera(self.cameraTypes[self.cameraTypeInd])

    for viewport in self.udViewPorts:
      if symbol in viewport.bindingMap.keys():
        viewport.bindingMap[symbol](True)
      else:
        viewport.camera.on_key_press(symbol, modifiers)

  def on_key_release(self, symbol, modifiers):
    for viewport in self.udViewPorts:
      if symbol in viewport.bindingMap.keys():
        viewport.bindingMap[symbol](False)
      else:
        viewport.camera.on_key_release(symbol, modifiers)

    #This was initially written to test blitting of images in files to textures

  def render_from_file(self, dt):
    from pyglet.gl import glEnable, GL_TEXTURE_2D, glDisable, glBindTexture
    self.im = pyglet.image.load('testIM_' + str(self.imageCounter) + '.png')
    self.tex = self.im.get_texture()
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, self.tex.id)
    self.vertex_list.draw(pyglet.gl.GL_QUADS)
    glDisable(GL_TEXTURE_2D)
    self.imageCounter = (self.imageCounter + 1) % 7

  def on_draw(self):
    pass

    #def on_resize(self, width, height):
      #tw = 2 ** (int(np.log2(width)))
      #th = 2 ** (int(np.log2(height)))

      #self.viewPort._view.set_size(tw, th)
      #self.renderWidth = width - 100
      #renderHeight =(int) (self.renderWidth/self.texAR)
      #self.renderer.renderViews[0].set_size(self.renderWidth, renderHeight)

  def render_uds(self, dt):
    """
    This dispatches a render_uds call to each viewport contained in the window
    """
    self.clear()
    #tell each viewport to draw its contents
    for viewport in self.udViewPorts:
      viewport.render_uds(dt)
    self.render_fps_text(dt)
    self.render_camera_information()
    self.render_controls_text()

  def on_mouse_motion(self, x, y, dx, dy):
    self.mousePosition = (x, y)
    self.renderer.renderSettings[self.viewPort._view].pick.x = x - self.viewPort._anchorX
    self.renderer.renderSettings[self.viewPort._view].pick.y = y - self.viewPort._anchorY



  def render_camera_information(self):
    positionTextWidth = 600
    pick = self.renderer.renderSettings[self.viewPort._view].pick
    projMousePos = tuple([*pick.pointCentre]) if pick.hit else '-'
    positionText = pyglet.text.Label("Camera Position :({:10.4f}, {:10.4f}, {:10.4f})\nMouse Position: {}, {}".format(*self.viewPort.camera.position, self.mousePosition, projMousePos), multiline=True, width=positionTextWidth)
    positionText.y = self._height - 20
    positionText.x = 0
    positionText.draw()

  def render_fps_text(self, dt):
    fpsText = pyglet.text.Label("{} FPS".format((int)(1/dt)))
    fpsText.draw()

  def render_controls_text(self):
    controlsText = pyglet.text.Label(self.viewPort.camera.get_controls_string())
    controlsText.width = 200
    controlsText.font_size = 8
    controlsText.x = self.viewPort._anchorX+self.viewPort._width
    controlsText.y = self.udViewPorts[1]._anchorY
    controlsText.multiline = True
    controlsText._wrap_lines = False
    controlsText.draw()

  def on_close(self):
      self.__del__()
      pyglet.app.exit()

class SlaveWindow(pyglet.window.Window):
  """
  Window for displaying additional views or information
  Shares a renderer with the main window for
  """
  def __init__(self, master):
    """
    takes the master window and links to its renderer instance
    """
    super(SlaveWindow, self).__init__()
    self.renderer = master.renderer
    self.udViewPorts = master.udViewPorts


class UDMapPort(UDViewPort):
  """
  view port which acts as a top down map displaying the main camera from above location
  """
  def __init__(self, width, height, x, y, target):
    parent = target.parent
    super().__init__(width, height, x, y, parent)
    self.camera = MapCamera(self._view, target.camera, 0.3)
    self.skyboxTexture = pyglet.image.load("parchment.jpg").get_texture()

  def render_map_marker(self):
    #TODO change this to true 3d representation (requires depth textures)
    triWidth = 30
    centreX = self._width/2 + self._anchorX
    centreY = self._height/2 + self._anchorY
    mapscale = numpy.array([[self._width/2,0],[0,self._height/2]])
    import numpy as np
    centre = np.array([[centreX, centreY],
                       [centreX, centreY],
                       [centreX, centreY],])
    r = self.camera.target.rotationMatrix[:2, :2]
    triangle = np.array([
      [-triWidth/4, -triWidth*1/3],
      [triWidth/4, -triWidth*1/3],
      [0, triWidth*2/3]
    ])
    vertices1 = (triangle.dot(r)+centre).flatten().tolist()
    tri_vertices = pyglet.graphics.vertex_list(3,
     ('v2f', vertices1),
       ('c3B', (0, 0, 255,
                0, 0, 255,
                255, 0, 0))
     )

    #TODO add line clipping, show near and far plane positions
    tri_vertices.draw(pyglet.graphics.GL_TRIANGLES)

    viewConeVertices = np.array(self.camera.target.get_view_vertices())
    centre = np.array([[centreX, centreY],
                       [centreX, centreY],
                       [centreX, centreY],
                       [centreX, centreY],])
    coneVerts = \
      pyglet.graphics.vertex_list(4,
        ('v2f', (viewConeVertices.dot(r).dot(mapscale)+centre).flatten().tolist())
      )
    coneVerts.draw(pyglet.graphics.GL_LINE_STRIP)

  def render_skybox(self):
    import pyglet.gl as gl
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    tex = self.skyboxTexture
    vs = \
      (  # vertices are represented as 2 element floats
        self._anchorX, self._anchorY,
        (self._width + self._anchorX), self._anchorY,
        (self._width + self._anchorX), (self._height + self._anchorY),
        self._anchorX, (self._height + self._anchorY),
      )
    #divide the skybox into 360 degrees horizontally and 180 vertically
    #calculate the amount of skybox to display based on FOV:
    hRat = self.camera.FOV/2/360
    vRat = np.arctan(np.tan(hRat*2*np.pi)*self._height/self._width)
    ts = \
      (  # texture coordinates as a float,
        0.0, 0.5,
        1.0, 0.5,
        1.0, 0.0,
        0.0, 0.0,
      )
    vList = pyglet.graphics.vertex_list(4,('v2f', vs), ('t2f',ts))
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex.id)
    vList.draw(pyglet.gl.GL_QUADS)
    gl.glDisable(gl.GL_TEXTURE_2D)

  def render_uds(self, dt):
    super().render_uds(dt)
    self.render_map_marker()

def consoleLoop():
  """
  This is an alternative to using IPython.embed, it is
  a simple
  Returns
  -------
  """
  while 1:
    str = input('$ ')
    try:
      exec(str)
    except EOFError:
      return
    except Exception as e:
      print(e)

def print_usage():
  print("usage: {} username password [serverURL]".format(argv[0]))

def run_script(filename):
  with open(filename,'r') as file:
    exec(file.read())


if __name__ == "__main__":
  if len(argv) < 3:
    logger.error("Euclideon Username (account email) and Password must be provided")
    print_usage()
    exit()
  resolution = (pyglet.canvas.get_display().get_default_screen().width,pyglet.canvas.get_display().get_default_screen().height)
  mainWindow = AppWindow(username=argv[1], password=argv[2], resolution=resolution)
  del(argv[2]) #don't really want to be keeping this around after we need it

  #optional: add models to the scene,
  #this can be done by drag and drop to the window
  #app.renderer.add_model(abspath("../../samplefiles/DirCube.uds"))
  pyglet.clock.schedule_interval(mainWindow.render_uds, 1 / 60)
  #consoleThread = threading.Thread(target=consoleLoop)
  consoleThread = threading.Thread(target=IPython.embed, kwargs={"user_ns":sys._getframe().f_locals})

  #the main view port is automatically instantiated, here we make
  #it a RecordCamera
  mainView = mainWindow.udViewPorts[0]
  mainView.set_camera(RecordCamera)

  #add a map view port to the window:
  mapView = UDMapPort(256, 256, mainWindow._width - 300, mainWindow._height - 200, mainView)

  #convenient naming for some commonly accessed properties
  mainCamera = mainView.camera
  mainCamera.farPlane = 20
  mainCamera.zoom = 2

  mapCamera = mapView.camera
  mapCamera.elevation = 1.1 #how far up our camera is compared to teh main camera
  mapCamera.nearPlane = 0.1 #set near plane to be close to the camera position (this may depend on the model)
  mapCamera.farPlane = 2 #far plane of the camera (setting this too high will cause the near plane to mode outwards)
  mapCamera.zoom = 0.1

  #customPort = UDViewPort(512, 512, 60, 60, mainWindow)


  #this is the list of renderInstances, we can modify the trnasformation of any loaded instances using this
  renderInstances = mainWindow.renderer.renderInstances

  renderer = mainWindow.renderer
  #an animator:
  runAnimationDemo = False
  if runAnimationDemo:
    from animator import UDSAnimator, animatorDemo
    renderer.add_model("./samplefiles/DirCube.uds")
    cubeInstance = mainWindow.renderer.renderInstances[-1]
    animator = UDSAnimator()
    animatorDemo(animator, cubeInstance)

  #example of mapping a custom function:
  #this increases the zoom level of the map view
  def zoomMapView(pushed):
    if pushed:
      mapCamera.zoom = mapCamera.zoom + 1
  def unzoomMapView(pushed):
    if pushed:
      mapCamera.zoom = mapCamera.zoom - 1
  mapView.bindingMap[keyboard.T] = zoomMapView
  mapView.bindingMap[keyboard.Y] = unzoomMapView

  pick = renderer.renderSettings[mainView._view].pick
  #setting up a filter
  filter = udSDK.udQueryBoxFilter()
  renderer.renderSettings[mainView._view].pFilter = filter.pFilter

  #slaveWindow = SlaveWindow(mainWindow)
  consoleThread.start()
  pyglet.app.run()
  mainView.write_to_image()
  print('done')
