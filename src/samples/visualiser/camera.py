import logging
import math

import numpy as np
import pyglet

import udSDK

logger = logging.getLogger(__name__)
class Camera():
  """
  Base camera class for Euclideon udSDK Python Sample
  This sets the default behaviour for a perspective camera
  Stores the state of the camera, and provides functions for modifyting
  that state

  User input is passed from the UDViewport object vio
  the set_{}Pressed functions (for mapped functions)

  Mouse Input is passed through the on_mouse_drag function

  This is intended to be subclassed for custom camera behaviour

  """
  def __init__(self, renderTarget: udSDK.udRenderTarget):
    self.normalSpeed = 0.3
    self.fastSpeed = 1
    self.moveSpeed = self.normalSpeed
    self.moveVelocity = [0, 0, 0]

    self.matrix = np.identity(4)
    self.renderTarget = renderTarget

    self.position = [0, 0, 0]

    self.nearPlane = 0.01
    self.farPlane = 2
    self.FOV = 60

    #booleans indicating button activation
    self.forwardPressed = False
    self.backPressed = False
    self.rightPressed = False
    self.leftPressed = False
    self.upPressed = False
    self.downPressed = False
    self.shiftPressed = False
    self.ctrlPressed = False
    self.zoomInPressed = False
    self.zoomOutPressed = False

    self.theta = 0
    self.phi = 0

    self.zoom = 1
    self.mouseSensitivity = 1 / 100
    self.camRotation = [0, 0, 0]
    self.lookAtTarget = [0, 0, 0]

    self.rotationMatrix = np.array([[1, 0, 0],
                                    [0, 1, 0],
                                    [0, 0, 1]])
    self.facingDirection = [0, 1, 0]
    self.rotationAxis = np.array([0,0,1])
    self.tangentVector = np.array([0,1,0])
    self._projectionMatrix = []

    self.controlString = """
      W,S,A,D: Move\n
      E: Move up\n
      C: Move Down\n
      Click + drag: Look around\n
      Shift (Hold): Increase speed\n
      O: Zoom in\n
      P: Zoom out\n
    """

  def on_cast(self):
    """
    To be called when this class is converted to from another Camera derived class
    ensures that appropriate variables are set in lieu of __init__being called without
    resetting all variables
    Returns
    -------

    """
    pass

  @property
  def position(self):
    return self.__position
  @position.setter
  def position(self, newposition):
    self.__position = tuple(newposition)
    self.matrix[3, :3] = [*newposition]
    self.renderTarget.SetMatrix(udSDK.udRenderTargetMatrix.Camera, self.matrix.flatten())

  def get_controls_string(self):
    return self.controlString

  def get_view_vertices(self):
    """

    Returns
    -------
    the extents of the viewing volume projected onto 2d space
    """
    #TODO make this correctly display the location of near and far plane
    rat = np.tan(self.FOV/2/180*np.pi)/self.farPlane
    nearLeft = [-self.nearPlane * rat, self.nearPlane/self.farPlane]
    farLeft = [-self.farPlane * rat, self.farPlane/self.farPlane]
    nearRight = [self.nearPlane * rat, self.nearPlane/self.farPlane]
    farRight = [self.farPlane * rat, self.farPlane/self.farPlane]
    return [farLeft, nearLeft, nearRight, farRight]

  def set_forwardPressed(self, val:bool):
    self.forwardPressed = val

  def set_backPressed(self, val):
    self.backPressed = val

  def set_rightPressed(self, val):
    self.rightPressed = val

  def set_leftPressed(self, val):
    self.leftPressed = val

  def set_upPressed(self, val):
    self.upPressed = val

  def set_downPressed(self, val):
    self.downPressed = val

  def set_shiftPressed(self, val):
    self.shiftPressed = val

  def set_ctrlPressed(self, val):
    self.ctrlPressed = val

  def set_zoomInPressed(self, val):
    self.zoomInPressed = val

  def set_zoomOutPressed(self, val):
    self.zoomOutPressed = val

  def reset_projection(self):
    self.set_projection_perspective()

  def on_key_press(self, symbol, modifiers):
    """
    Defined for passing key presses not mapped using the key bindings in the view port
    override subclasses
    Parameters
    ----------
    symbol
    modifiers

    Returns
    -------

    """
    pass

  def on_key_release(self, symbol, modifiers):
    pass

  def rotate_polar(self, vec, dtheta, dphi):
    """
    takes change in polar coordiantes and updates the camera rotation
    based on it
    Returns
    -------
    the a copy of vector vec rotated by dtheta in the xy plane and phi
    """
    r = math.sqrt(vec[0]**2+vec[1]**2+vec[2]**2)
    theta = math.atan2(vec[1], vec[0])
    phi = math.acos(vec[2]/r)

    #prevent rotation such that the vector is pointing directly up or down
    thresh = 0.1
    if abs(phi + dphi) < thresh or abs(phi + dphi - math.pi) < thresh:
      dphi = 0

    xprime = r * math.sin(phi+dphi)*math.cos(theta+dtheta)
    yprime = r * math.sin(phi+dphi) * math.sin(theta + dtheta)
    zprime = r * math.cos(phi+dphi)
    self.phi = phi
    self.theta = theta
    return [xprime, yprime, zprime]

  def set_projection_perspective(self, near=None, far=None, FOV=None):
    if near is None:
      near = self.nearPlane
    if far is None:
      far = self.farPlane
    if FOV is None:
      FOV = self.FOV
    else:
      self.FOV = FOV

    FOV = FOV/180*np.pi
    e = 1/np.tan(FOV/2)
    a = self.renderTarget.height / self.renderTarget.width

    self._projectionMatrix = \
      [
        e*a, 0, 0, 0,
        0, 0, (far+near)/(far-near), 1,
        0, e, 0, 0,
        0, 0, -(2*far*near)/(far-near), 0
       ]
    self.renderTarget.SetMatrix(udSDK.udRenderTargetMatrix.Projection, self._projectionMatrix)

  def set_projection_ortho(self, left, right, top, bottom, near, far):
    self._projectionMatrix = \
      [
        2/(right-left), 0, 0, 0,
        0, 0, 2/(far-near), 0,
        0, 2/(top - bottom), 0, 0,
        -(right+left)/(right-left), -(top+bottom)/(top-bottom), -(far+near)/(far-near), 1
      ]
    self.renderTarget.SetMatrix(udSDK.udRenderTargetMatrix.Projection, self._projectionMatrix)

  def set_rotation(self, x=0, y=-5, z=0, roll=0, pitch=0, yaw=0):
    """
    Sets the camera matrix to have a rotation of yaw, pictch roll
    Parameters
    ----------
    x
    y
    z
    roll
    pitch
    yaw

    Returns
    -------

    """
    sy = math.sin(yaw)
    cy = math.cos(yaw)
    sp = math.sin(pitch)
    cp = math.cos(pitch)
    sr = math.sin(roll)
    cr = math.cos(roll)

    self.matrix = np.array([
      [cy*cp, cy*sp*sr-sy*cr, cy*sp*cr+sy*sr, 0],
      [sy*cp, sy*sp*sr+cy*cr, sy*sp*cr-cy*sr, 0],
      [-sp, cp*sr, cp*cr, 0],
      [x, y, z, 1]
    ])
    self.position = [x, y, z]
    self.rotationMatrix = self.matrix[:3, :3]
    self.renderTarget.SetMatrix(udSDK.udRenderTargetMatrix.Camera, self.matrix.flatten())

  def axisAngle(self, axis, theta):
    #cTheta = np.dot(np.array([0,1,0]), dPoint) / np.linalg.norm(dPoint)
    #theta = np.arccos(cTheta)
    cTheta = np.cos(theta)
    sTheta = np.sin(theta)

    self.matrix = np.array(
      [
        [cTheta + axis[0] ** 2 * (1 - cTheta), axis[0] * axis[1] * (1 - cTheta) - axis[2] * sTheta, axis[0] * axis[2] * (1 - cTheta), 0],
        [axis[1] * axis[0] * (1 - cTheta) + axis[2] * sTheta, cTheta + axis[1] ** 2 * (1 - cTheta), axis[1] * axis[2] * (1 - cTheta) - axis[0] * sTheta, 0],
        [axis[2] * axis[0] * (1 - cTheta) - axis[1] * sTheta, axis[2] * axis[1] * (1 - cTheta) + axis[0] * sTheta, cTheta + axis[2] ** 2 * (1 - cTheta), 0],
        [self.position[0], self.position[1], self.position[2], 1]
      ]
    )

  def from_udStream(self):
    """
    Experimental: loads the camera paramters from a version of udStream modified to publish its camera and projection matrices
    to file every 60 frames. This may be changed in the future to use a networking protocol instead
    """
    from array import array
    a = array("d")
    b = array("d")
    with open("C:/testoutputs/cameraparameters", 'rb') as fp:
      a.fromfile(fp, 16)
      b.fromfile(fp, 16)

    print(a)
    print(b)
    self.matrix = np.array([*a]).reshape([4,4])
    self._projectionMatrix = [*b]
    self.renderTarget.SetMatrix(udSDK.udRenderTargetMatrix.Camera,[*a])
    self.renderTarget.SetMatrix(udSDK.udRenderTargetMatrix.Projection,[*b])

  def position_from_udStream(self):
    """
    same as above but only reading position of the camera from udStream
    """
    from array import array
    a = array("d")
    with open("C:/testoutputs/cameraparameters", 'rb') as fp:
      a.fromfile(fp, 16)
      self.position = [*a[12:15]]


  def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
    vec = self.rotate_polar(self.facingDirection,dx/100,dy/100)
    self.look_direction(np.array(vec))

  def look_at(self, lookAtPoint=None, cameraPosition=None):
    """
    faces the camera at point2, positions the camera at point1
    Parameters
    ----------
    cameraPosition: position of the camera
    lookAtPoint: x, y, z tuple to face the camera towards
    """
    if cameraPosition is None:
      cameraPosition = self.position
    else:
      self.position = cameraPosition

    if lookAtPoint is None:
      lookAtPoint = self.lookAtTarget

    if not np.array_equal(lookAtPoint, cameraPosition):
      #calculate our axis of rotation based on the distance between these points
      dPoint = np.array(lookAtPoint) - np.array(cameraPosition)
    else:
      dPoint = np.array([1, 1, 0])
    self.look_direction(dPoint)

  def look_direction(self, dPoint: np.array):
    """
    Points the camera in the direction vector dPoint
    assumes that the tangent vector has a z value of zero (i.e. no roll)
    Parameters
    ----------
    dPoint

    Returns
    -------

    """
    tangent = [0, 0, 0]
    if dPoint[1] != 0:
      tangent[0] = (dPoint[0]-np.sqrt(dPoint[0]**2+4*dPoint[1]**2))/(2*dPoint[1])
    elif dPoint[2]>0:
      tangent[0] = 1
    else:
      tangent[0] = -1
    tangent[1] = 1-tangent[0]**2
    tangent = -np.array(tangent)
    tangent = tangent / np.sqrt(tangent.dot(tangent))

    forward = dPoint/np.sqrt(dPoint.dot(dPoint))
    axis = np.cross(tangent, forward)
    axis = axis / np.sqrt(axis.dot(axis))

    self.matrix = np.array(
      [
        [tangent[0], tangent[1], tangent[2], 0],
        [forward[0], forward[1], forward[2], 0],
        [axis[0], axis[1], axis[2], 0],
        [self.position[0], self.position[1], self.position[2], 1]
      ]
    )
    self.rotationAxis = axis
    self.tangentVector = tangent
    self.rotationMatrix = self.matrix[:3, :3]
    self.facingDirection = np.array([0,1,0]).dot(self.rotationMatrix).tolist()
    self.renderTarget.SetMatrix(udSDK.udRenderTargetMatrix.Camera, self.matrix.flatten())

  def update_move_direction(self):
    """
    updates the velocity and projection based on what keys have been pressed since the last call
    """
    self.moveVelocity = [0, 0, 0]# in local coordinates
    if self.shiftPressed:
      self.moveSpeed = self.fastSpeed
    else:
      self.moveSpeed = self.normalSpeed
    if self.forwardPressed:
      self.moveVelocity[1] += self.moveSpeed
    if self.backPressed:
      self.moveVelocity[1] -= self.moveSpeed
    if self.rightPressed:
      self.moveVelocity[0] += self.moveSpeed
    if self.leftPressed:
      self.moveVelocity[0] -= self.moveSpeed
    if self.upPressed:
      self.moveVelocity[2] += self.moveSpeed
    if self.downPressed:
      self.moveVelocity[2] -= self.moveSpeed
    if self.zoomInPressed:
      self.zoom += 1
    if self.zoomOutPressed and self.zoom>1:
      self.zoom -= 1
    self.mouseSensitivity = 0.1/self.zoom
    self.set_projection_perspective(self.nearPlane, self.farPlane, self.zoom)
    self.moveVelocity = np.array(self.moveVelocity).dot(self.rotationMatrix).tolist()

  def update_position(self, dt):
    self.update_move_direction()
    newposition = [0, 0, 0]
    newposition[0] = self.position[0] + self.moveVelocity[0] * dt
    newposition[1] = self.position[1] + self.moveVelocity[1] * dt
    newposition[2] = self.position[2] + self.moveVelocity[2] * dt
    self.position = newposition


class OrthoCamera(Camera):
  def __init__(self, renderTarget):
    super().__init__(renderTarget)
    self.FOV = 90

  def on_cast(self):
    self.controlString = """
      Ortho Camera (experimental):
      W,S,A,D: Move\n
      E: Move up\n
      C: Move Down\n
      Click + drag: Look around\n
      Shift (Hold): Increase speed\n
      O: Zoom in\n
      P: Zoom out\n
    """
    self.FOV = 90

  def update_move_direction(self):
    super().update_move_direction()
    self.moveVelocity[2] = 0
    v = np.array(self.moveVelocity)
    mag = np.sqrt(v.dot(v))
    if mag != 0:
      self.moveVelocity = (v/mag).tolist()

    if self.upPressed:
      self.moveVelocity[2] += self.moveSpeed
    if self.downPressed:
      self.moveVelocity[2] -= self.moveSpeed


  def update_position(self, dt):
    super().update_position(dt)
    ar = self.renderTarget.width / self.renderTarget.height
    zoom = np.exp(self.zoom)
    viewWidth = 100/self.zoom
    self.mouseSensitivity = 0.1/ zoom
    self.set_projection_ortho(-ar/2*viewWidth, ar/2*viewWidth, 1/ar/2*viewWidth, -1/ar/2*viewWidth, self.nearPlane, self.farPlane)

  def reset_projection(self):
    pass


class MapCamera(OrthoCamera):
  """
  Orthographic camera that follows a target and remains a set height above it
  """

  def __init__(self, renderTarget, target, elevation):
    super().__init__(renderTarget)
    self.target = target
    self.elevation = elevation

  class DefaultTarget(object):
    def __init__(self):
      self.position = [0, 0, 0]
  def on_cast(self):
    pass
  #here we override the default control behaviour of the camera
  def update_move_direction(self):
    pass

  def on_mouse_drag(self, *args, **kwargs):
    pass

  def update_position(self, dt):
    self.position = [self.target.position[0], self.target.position[1], self.target.position[2]+self.elevation]
    self.look_direction(np.array([0, 0, -1]))
    ar = self.renderTarget.width / self.renderTarget.height
    zoom = self.zoom
    self.set_projection_ortho(-ar/2*self.position[2]/zoom, ar/2*self.position[2]/zoom, 1/ar/2*self.position[2]/zoom, -1/ar/2*self.position[2]/zoom,self.nearPlane,self.farPlane)

class OrbitCamera(Camera):
  """
  Movement of this camera is relative to a fixed point in space
  """

  def on_cast(self):
    self.controlString = """
      Orbit Camera (experimental):
      W,S,A,D: Move\n
      E: Move up\n
      C: Move Down\n
      Click + drag: Move rotation Centre\n
      Shift (Hold): Increase speed\n
      O: Zoom in\n
      P: Zoom out\n
    """

  def update_move_direction(self):
    self.look_at()
    super(OrbitCamera, self).update_move_direction()
    #self.moveVelocity = np.array(self.moveVelocity).dot(self.rotationMatrix).tolist()

  def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
    horiz = dx * self.tangentVector * self.mouseSensitivity
    vert = dy * self.rotationAxis * self.mouseSensitivity
    if not self.ctrlPressed:
      self.lookAtTarget = self.lookAtTarget + horiz + vert
    else:
      self.position = self.position - horiz - vert


class PerspectiveCamera(OrbitCamera):
  def update_position(self, dt):
    #self.facingDirection = np.array([0, 1, 0]).dot(self.rotationMatrix).tolist()
    for i in range(3):
      self.lookAtTarget[i] = self.position[i] + self.facingDirection[i]
    super().update_position(dt)


class TrackCamera(Camera):
  def update_position(self, dt):
    self.lookAtTarget[1] += 0.0001
    super().update_position(dt)
    self.look_at()

class RecordCamera(Camera):
  """
  A camera class for manual generation and replay of flythroughs of models
  the user defines a set of waypoints by pressing space when the camera is positioned at
  the desired locations

  Pressing enter will replay the path

  Backspace will delete the most recently added waypoint
  """
  def __init__(self, *args, **kwargs):
    super().__init(*args, **kwargs)
    self.on_cast()

  def on_cast(self):
    self.controlString = """
      Recording Camera:
      W,S,A,D: Move\n
      E: Move up\n
      C: Move Down\n
      Click + drag: Look around\n
      Shift (Hold): Increase speed\n
      O: Zoom in\n
      P: Zoom out\n
      Space: Record Position as Waypoint\n
      Backspace: Remove Last Waypoint\n
      Enter: Play back recorded path\n"""

    try:
      self.waypoints
    except AttributeError:
      self.waypoints = []
      self.replayInd = 0
      self.replaying = False

  def on_key_press(self, symbol, modifiers):
    if symbol == pyglet.window.key.SPACE:
      self.waypoints.append(self.position)

    if symbol == pyglet.window.key.ENTER:
      try:
        self.position = self.waypoints[0]
      except IndexError:
        return
      self.replaying = True
      self.replayInd = 1

    if symbol == pyglet.window.key.BACKSPACE:
      self.waypoints.pop()

  def update_move_direction(self):
    try:
      self.replaying
    except AttributeError:
      self.replaying = False

    if not self.replaying:
      super().update_move_direction()
      return
    #here we linearly interpolate the path and face the camera direction
    #ddir = dir + np.array(self.lookAtTarget)-np.array(self.position)
    #define the facing the one we are going in
    dir = np.array(self.waypoints[self.replayInd]) - np.array(self.position)
    mag = np.linalg.norm(dir) #how far away from the waypoint we are
    ddir = dir/mag - np.array(self.facingDirection)
    dir = dir/mag * self.moveSpeed #dir is now the velocity we want the camera to travel in
    self.look_direction(np.array(self.facingDirection) + ddir / 10)
    self.moveVelocity = (dir).tolist()
    if abs(mag) < self.moveSpeed:
      #we are as close as we can get in a single step to the waypoint
      if self.replayInd+1 < len(self.waypoints):
        #self.position = self.waypoints[self.replayInd]
        #move to the next waypoint
        self.replayInd += 1
      else:
        #end the replay
        self.replaying = False
        self.moveVelocity = [0, 0, 0]
        return

    #self.look_at(self.waypoints[self.replayInd+1])
