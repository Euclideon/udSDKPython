import math
import sys
import threading

import IPython
import numpy
from PIL import Image

import vault
from easyrenderer import VDKEasyRenderer
import pyglet.window.key as keyboard
import pyglet
from camera import *
from os.path import abspath
import numpy as np
from sys import argv
import logging



class VDKViewPort():
  """This class represents the quad that the UDS render is blitted to,
  it handles the camera information associated with the view it controls
  """
  def __init__(self, width, height, x, y, parent):
    self._width = width
    self._height = height
    self._anchorX = x
    self._anchorY = y

    self.parent = parent

    self.udsScaleMode = 'minDim' #determines the way in which the model is scaled
    self._view = parent.renderer.add_view()
    #for openGL to properly deal with our texture the render must be a power of 2:
    tw = 2**(int(np.log2(width)))
    th = 2**(int(np.log2(height)))
    self._view.set_size(tw, th)
    self._camera = Camera(self._view)
    #self._camera = OrthoCamera(self._view)
    self.bindingMap = \
      {
        keyboard.W: self._camera.set_forwardPressed,
        keyboard.S: self._camera.set_backPressed,
        keyboard.D: self._camera.set_rightPressed,
        keyboard.A: self._camera.set_leftPressed,
        keyboard.E: self._camera.set_upPressed,
        keyboard.C: self._camera.set_downPressed,
        keyboard.LSHIFT: self._camera.set_shiftPressed,
        keyboard.LCTRL: self._camera.set_ctrlPressed,
        keyboard.O: self._camera.set_zoomInPressed,
        keyboard.P: self._camera.set_zoomOutPressed,
      }
    self.tex = pyglet.image.Texture.create(width, height)
    self.make_vertex_list()
    self.skyboxTexture = pyglet.image.load("WaterClouds.jpg").get_texture(())

  def set_camera(self, cameraType = OrthoCamera, bindingMap = None):
    self._camera.__class__ = cameraType
    self._camera.reset_projection()
    self._camera.on_cast()
    if bindingMap is None:#reset to default
      self.bindingMap = \
        {
          keyboard.W: self._camera.set_forwardPressed,
          keyboard.S: self._camera.set_backPressed,
          keyboard.D: self._camera.set_rightPressed,
          keyboard.A: self._camera.set_leftPressed,
          keyboard.E: self._camera.set_upPressed,
          keyboard.C: self._camera.set_downPressed,
          keyboard.LSHIFT: self._camera.set_shiftPressed,
          keyboard.LCTRL: self._camera.set_ctrlPressed,
          keyboard.O: self._camera.set_zoomInPressed,
          keyboard.P: self._camera.set_zoomOutPressed,
        }
    else:
      self.bindingMap = bindingMap

  def make_vertex_list(self):
    self._vertex_list = pyglet.graphics.vertex_list\
    (4,
      ('v2f',
        (  # vertices are represented as 2 element floats
          self._anchorX, self._anchorY,
          (self._width + self._anchorX), self._anchorY,
          (self._width + self._anchorX), (self._height + self._anchorY),
          self._anchorX, (self._height + self._anchorY),
        )
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
    vs =\
      (  # vertices are represented as 2 element floats
        self._anchorX, self._anchorY,
        (self._width + self._anchorX), self._anchorY,
        (self._width + self._anchorX), (self._height + self._anchorY),
        self._anchorX, (self._height + self._anchorY),
      )
    #divide the skybox into 360 degrees horizontally and 180 vertically
    #calculate the amount of skybox to display based on FOV:
    hRat = self._camera.FOV/2/360
    vRat = np.arctan(np.tan(hRat*2*np.pi)*self._height/self._width)
    ts =\
      (  # texture coordinates as a float,
        self._camera.theta/2/np.pi+hRat, -self._camera.phi/np.pi-vRat/2,
        self._camera.theta/2/np.pi-hRat, -self._camera.phi/np.pi-vRat/2,
        self._camera.theta/2/np.pi-hRat, -self._camera.phi/np.pi+vRat/2,
        self._camera.theta/2/np.pi+hRat, -self._camera.phi/np.pi+vRat/2,
      )
    vList = pyglet.graphics.vertex_list(4,('v2f', vs), ('t2f',ts))
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex.id)
    vList.draw(pyglet.gl.GL_QUADS)
    gl.glDisable(gl.GL_TEXTURE_2D)


  def render_uds(self, dt):
    import pyglet.gl as gl
    from pyglet.gl import glEnable, glDisable, GL_TEXTURE_2D, glBindTexture
    self._camera.update_position(dt)
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
  Main window class, handles events and contains all views
  """
  def __init__(self, username, password, *args, resolution=(1024+50, 512+100), offset=(50, 25), **kwargs):
    super(AppWindow, self).__init__(*resolution, file_drops=True, resizable=True)
    self.renderer = VDKEasyRenderer(username, password, models=[])
    self.set_caption("Euclideon Vault Python")
    self.VDKViewPorts = []
    self.viewPort = VDKViewPort(1024, 512, offset[0], offset[1], self)
    #viewPort2 = VDKMapPort(256, 256, self._width-300, self._height-200, self.viewPort)
    self.VDKViewPorts.append(self.viewPort)
    #self.VDKViewPorts.append(viewPort2)

    self.cameraTypes = [RecordCamera, OrthoCamera, OrbitCamera]
    self.cameraTypeInd = 0
    self.imageCounter = 0

  def on_file_drop(self, x, y, paths):
    for path in paths:
      self.renderer.add_model(path)

  def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
    for viewport in self.VDKViewPorts:
      viewport._camera.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

  def on_key_press(self, symbol, modifiers):
    if symbol == keyboard.TAB:
      self.cameraTypeInd += 1
      self.cameraTypeInd %= len(self.cameraTypes)
      self.viewPort.set_camera(self.cameraTypes[self.cameraTypeInd])

    for viewport in self.VDKViewPorts:
      if symbol in viewport.bindingMap.keys():
        viewport.bindingMap[symbol](True)
      else:
        viewport._camera.on_key_press(symbol, modifiers)

  def on_key_release(self, symbol, modifiers):
    for viewport in self.VDKViewPorts:
      if symbol in viewport.bindingMap.keys():
        viewport.bindingMap[symbol](False)
      else:
        viewport._camera.on_key_release(symbol, modifiers)

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
    self.clear()
    fpsText = pyglet.text.Label("{} FPS".format((int)(1/dt)))
    fpsText.draw()

    positionTextWidth = 600
    positionText = pyglet.text.Label("x={:10.4f} y={:10.4f} z={:10.4f}\naxis = {}\n tangent ={}".format(*self.viewPort._camera.position, self.viewPort._camera.rotationAxis, self.viewPort._camera.tangentVector), multiline=True, width=positionTextWidth)
    positionText.y = self._height - 20

    positionText.x = 0
    for viewport in self.VDKViewPorts:
      viewport.render_uds(dt)
    positionText.draw()

    controlsText = pyglet.text.Label(self.viewPort._camera.get_controls_string())
    controlsText.width = 200
    controlsText.font_size = 8
    controlsText.x = self.viewPort._anchorX+self.viewPort._width
    controlsText.y = self.VDKViewPorts[1]._anchorY
    controlsText.multiline = True
    controlsText._wrap_lines = False
    controlsText.draw()

  def on_close(self):
      self.__del__()
      pyglet.app.exit()

class VDKViewPort3D(VDKViewPort):
  """
  Viewport quad with 3D faces, used for constructing ViewPrisms
  """
  def __init__(self, width, height, centreX, centreY, parent, horizontalDirection = [1,0,0], verticalDirection = [0,1,0]):
    self._width = width
    self._height = height
    self._centre = [centreX, centreY, 0]
    self.parent = parent
    self.vec1 = horizontalDirection
    self.vec2 = verticalDirection
    #self.vec1 = [0.707, -0.707,0.01]
    #self.vec2 = [0.707, 0.707,0.01]
    super(VDKViewPort3D, self).__init__(width, height, centreX, centreY, parent)

  def orient(self, centre, vec1, vec2):
    #position the plane such that it is parallel to vectors 1 and 2 and centred at centre:
    # these are the vertices at the corners of the quad, each line is the pixel coordinates of the
    self._vertex_list.vertices = \
      [
        # bottom left
        centre[0] - vec1[0] * self._width / 2 - vec2[0] * self._height / 2,
        centre[1] - vec1[1] * self._width / 2 - vec2[1] * self._height / 2,
        centre[2] - vec1[2] * self._width / 2 - vec2[2] * self._height / 2,
        # bottom right
        centre[0] + vec1[0] * self._width / 2 - vec2[0] * self._height / 2,
        centre[1] + vec1[1] * self._width / 2 - vec2[1] * self._height / 2,
        centre[2] + vec1[2] * self._width / 2 - vec2[2] * self._height / 2,
        #top right
        centre[0] + vec1[0] * self._width/2 + vec2[0] * self._height/2,
        centre[1] + vec1[1] * self._width / 2 + vec2[1] * self._height / 2,
        centre[2] + vec1[2] * self._width / 2 + vec2[2] * self._height / 2,
        # top left
        centre[0] - vec1[0] * self._width / 2 + vec2[0] * self._height / 2,
        centre[1] - vec1[1] * self._width / 2 + vec2[1] * self._height / 2,
        centre[2] - vec1[2] * self._width / 2 + vec2[2] * self._height / 2,
      ]
    #position the camera such that it is a fixed distance from the
    import numpy as np
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    normal = np.cross(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2))
    normal = normal.dot(np.array([
      [1, 0, 0],
      [0, 0, 1],
      [0, 1, 0],
    ]))
    self._camera.look_at([0, 0, 0], normal)
    #self._camera.set_view(normal[0], normal[1], normal[2])

  def make_vertex_list(self):
    self._vertex_list = pyglet.graphics.vertex_list(4,'v3f/stream','t2f/static')
    self._vertex_list.tex_coords = \
      [
        0, 1,
        1, 1,
        1, 0,
        0, 0,
      ]
    self.orient(self._centre, self.vec1, self.vec2)


class VDKViewPrism:
  """
  Class representing a sectional view of a model
  it is a rectangular prism with a UD view for each face
  """
  def __init__(self, width, height, depth):
    self.height = height
    self.width = width
    self.depth = depth

    self.viewPorts = []

class VDKMapPort(VDKViewPort):
  """
  view port which acts as a top down map displaying the main camera from above location
  """
  def __init__(self, width, height, x, y, target):
    parent = target.parent

    super().__init__(width, height, x, y, parent)
    self._camera = MapCamera(self._view, target._camera, 0.3)
    self.skyboxTexture = pyglet.image.load("parchment.jpg").get_texture()

  def render_map_marker(self):
    #TODO change this to true 3d representation (requires depth textures)
    triWidth = 30
    centreX = self._width/2 + self._anchorX
    centreY = self._height/2 + self._anchorY
    #mapscale = 30 *numpy.array([[self._width/self._camera.target._view.width, 0],[0, 80*self._height/self._camera.target._view.height]])
    mapscale = numpy.array([[self._width/2,0],[0,self._height/2]])
    import numpy as np
    centre = np.array([[centreX, centreY],
                       [centreX, centreY],
                       [centreX, centreY],])
    r = self._camera.target.rotationMatrix[:2, :2]
    triangle = np.array([
      [-triWidth/4, -triWidth*1/3],
       [triWidth/4, -triWidth*1/3],
       [0, triWidth*2/3]
    ])
    vertices1 = (triangle.dot(r)+centre).flatten().tolist()
    tri_vertices = pyglet.graphics.vertex_list(3,
     ('v2f',
      vertices1
      ),
     ('c3B',(0,0,255,0,0,255,255,0,0))
     )

    #TODO add line clipping, show near and far plane positions
    tri_vertices.draw(pyglet.graphics.GL_TRIANGLES)

    viewConeVertices = np.array(self._camera.target.get_view_vertices())
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
    hRat = self._camera.FOV/2/360
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

def spinInstance(instance):
  rate =0.1
  r1, r2, r3 = instance.rotation
  instance.rotation = (r1+rate,r2+rate,r3+rate)

def spinfcn(instance):
  def ret(dt):
    spinInstance(instance)
  return ret

def print_usage():
  print("usage: {} username password [serverURL]".format(argv[0]))

if __name__ == "__main__":
  if len(argv) < 3:
    logger.error("Euclideon Username and Password must be provided")
    print_usage()
    exit()
  app = AppWindow(username=argv[1], password=argv[2])
  del(argv[2])

  #optional: add models to the scene,
  #this can be done by drag and drop to the window
  #app.renderer.add_model(abspath("../../samplefiles/DirCube.uds"))
  #app.renderer.add_model("https://az.vault.euclideon.com/GoldCoast_20mm.uds")
  pyglet.clock.schedule_interval(app.render_uds, 1/60)
  #consoleThread = threading.Thread(target=consoleLoop)
  consoleThread = threading.Thread(target=IPython.embed, kwargs={"user_ns":sys._getframe().f_locals})

  #the main view port is automatically instantiated, here we make
  #it a RecordCamera
  main = app.VDKViewPorts[0]
  main.set_camera(RecordCamera)

  #add a map view port to the window:
  map = VDKMapPort(256, 256, app._width - 300, app._height - 200, main)
  map._camera.elevation = 1.1
  map._camera.nearPlane = 0.1
  map._camera.farPlane = 2
  map._camera.zoom = 0.1
  app.VDKViewPorts.append(map)

  consoleThread.start()
  pyglet.app.run()
  main.write_to_image()
  print('done')
