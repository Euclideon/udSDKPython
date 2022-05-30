import ctypes
from enum import IntEnum, unique

import numpy as np

import udSDK

@unique
class udGeometryType(IntEnum):
  udGT_Inverse = 0  # //!< An inversion filter; flips the udGeometryTestResult of the child udGeometry node
  udGT_CircleXY = 1  # //!< A 2D Circle with an infinite Z value
  udGT_RectangleXY = 2  # //!< A 2D Rectangle with an infinite Z value
  udGT_PolygonXY = 3  # //!< A 2D Polygon with rotation (quaternion) to define the up of the polygon
  udGT_PolygonPerspective = 4  # //!< A 2D polygon with a perspective projection to the screen plane
  udGT_Cylinder = 5  # //!< @deprecated A radius out of a line which caps immediately at the end of the line
  udGT_Capsule = 6  # //!< A line with a radius from the line; forming hemispherical caps at the end of the line
  udGT_Sphere = 7  # //!< A radius from a point
  udGT_HalfSpace = 8  # //!< A binary space partition allowing 1 side of a plane
  udGT_AABB = 9  # //!< An axis aligned box; Use with caution. OBB while less performant correctly handles transforms
  udGT_OBB = 10  # //!< An oriented bounding box using half size and orientation
  udGT_CSG = 11  # //!< A constructed solid geometry that uses a udGeometryCSGOperation to join to child udGeometry nodes

  udGT_Count = 12  # /!< Count helper value to iterate this enum

@unique
class udGeometryCSGOperation(IntEnum):
  udCSGO_Union = 0
  udCSGO_Difference = 1
  udCSGO_Intersection = 2

class udGeometryDouble2(ctypes.Structure):
  _fields_=[
    ('x', ctypes.c_double),
    ('y', ctypes.c_double)
    ]

class udGeometryDouble3(ctypes.Structure):
  _fields_=[
    ('x', ctypes.c_double),
    ('y', ctypes.c_double),
    ('z', ctypes.c_double)
  ]

class udGeometryDouble4x4(ctypes.Structure):
  _fields_=[
    ('array', ctypes.c_double*16)
  ]

class udGeometryOBBStruct(ctypes.Structure):
  _fields_ = [
    ("center", udGeometryDouble3),
    ("extents", udGeometryDouble3),
    ("rotationMatrix", udGeometryDouble4x4),
  ]

class udGeometry():

  pGeometry = ctypes.c_void_p(0)
  def __init__(self):
    self._udGeometry_Create = getattr(udSDK.udSDKlib, "udGeometry_Create")
    self._udGeometry_Destroy = getattr(udSDK.udSDKlib, "udGeometry_Destroy")
    self._udGeometry_Deinit = getattr(udSDK.udSDKlib, "udGeometry_Deinit")
    self._udGeometry_InitOBB = udSDK.udExceptionDecorator(udSDK.udSDKlib.udGeometry_InitOBB)
    self._udGeometry_InitAABBFromCentreExtents = udSDK.udExceptionDecorator(udSDK.udSDKlib.udGeometry_InitAABBFromCentreExtents) #TODO
    self._udGeometry_InitAABBFromMinMax = udSDK.udExceptionDecorator(udSDK.udSDKlib.udGeometry_InitAABBFromMinMax) #TODO
    self._udGeometry_InitSphere = udSDK.udExceptionDecorator(udSDK.udSDKlib.udGeometry_InitSphere)
    self._udGeometry_InitCapsule = udSDK.udExceptionDecorator(udSDK.udSDKlib.udGeometry_InitCapsule) #TODO

    # Deprecated:
    #self._udGeometry_InitCylinderFromCenterAndHeight = udSDK.udExceptionDecorator(udSDK.udSDKlib._udGeometry_InitCylinderFromCenterAndHeight)
    #self._udGeometry_InitCylinderFromEndPoints = udSDK.udExceptionDecorator(udSDK.udSDKlib.udGeometry_InitCylinderFromEndPoints)

    self._udGeometry_InitHalfSpace = udSDK.udExceptionDecorator(udSDK.udSDKlib.udGeometry_InitHalfSpace)
    self._udGeometry_InitCSG = udSDK.udExceptionDecorator(udSDK.udSDKlib.udGeometry_InitCSG)
    self._udGeometry_InitPolygonPerspective = udSDK.udExceptionDecorator(udSDK.udSDKlib.udGeometry_InitPolygonPerspective)
    self._udGeometry_InitPolygonXY = udSDK.udExceptionDecorator(udSDK.udSDKlib.udGeometry_InitPolygonXY) #TODO
    self._udGeometry_InitRectangleXY = udSDK.udExceptionDecorator(udSDK.udSDKlib.udGeometry_InitRectangleXY) #TODO
    self._udGeometry_InitCircleXY = udSDK.udExceptionDecorator(udSDK.udSDKlib.udGeometry_InitCircleXY) #TODO
    self._udGeometry_InitInverse = udSDK.udExceptionDecorator(udSDK.udSDKlib.udGeometry_InitInverse)

    udSDK._HandleReturnValue(self._udGeometry_Create(ctypes.byref(self.pGeometry)))

  def __del__(self):
    self._udGeometry_Deinit(self.pGeometry)
    self._udGeometry_Destroy(ctypes.byref(self.pGeometry))

  def as_project_node(self, parent=None):
    """
    returns a udProjectNode with the same properties as this filter
    currently this is not synchronized so future changes to the filter will not be reflected in the
    node. TODO: make nodes synchronize
    """

    ret = parent.create_child(type="QFilter", name="queryFilter")
    ret.coordinates = self.position
    if hasattr(self, "radius"):
      ret.set_metadata_double("size.x", self.radius)
    if hasattr(self, "halfHeight"):
      ret.set_metadata_double("size.y", self.halfHeight)
    if hasattr(self, "size"):
      cs = "xyz"
      for i in range(3):
        ret.set_metadata_double(f"size.{cs[i]}", self.size[i])
    if hasattr(self, "yawPitchRoll"):
      cs = "ypr"
      for i in range(3):
        ret.set_metadata_double(f"transform.rotation.{cs[i]}", self.yawPitchRoll[i])
    return ret

  @property
  def inverse(self):
    """
    The inverse of the udGeometry filter
    """
    return udGeometryInverse(self)

  def union(self, other):
    """
    returns the result of a union set operation between this and another udGeometry object
    """
    return udGeometryCSG(self, other, udGeometryCSGOperation.udCSGO_Union)

  def difference(self, other):
    """
    returns the result of a difference set operation between this and another udGeometry object
    """
    return udGeometryCSG(self, other, udGeometryCSGOperation.udCSGO_Difference)

  def intersection(self, other):
    """
    returns the result of an intersection set operation between this and another udGeometry object
    """
    return udGeometryCSG(self, other, udGeometryCSGOperation.udCSGO_Intersection)

  def __add__(self, other):
    return self.union(other)

  def __sub__(self, other):
    return self.difference(other)

class udGeometrySphere(udGeometry):
  """
  Represents a sphere with a radius of radius and a centre at centre
  """
  def __init__(self, centre, radius):
    super(udGeometrySphere, self).__init__()
    self.__position = [*centre]
    self.__radius = radius
    self._set_geometry()

  def _set_geometry(self):
    centreC = udGeometryDouble3()
    centreC.x = self.__position[0]
    centreC.y = self.__position[1]
    centreC.z = self.__position[2]
    self._udGeometry_Deinit(self.pGeometry)
    self._udGeometry_InitSphere(self.pGeometry, centreC, ctypes.c_double(self.radius))

  @property
  def position(self):
    return self.__position

  @position.setter
  def position(self, position):
    self.__position = tuple([*position])
    self._set_geometry()

  @property
  def radius(self):
    return self.__radius

  @radius.setter
  def radius(self, radius):
    self.__radius = float(radius)
    self._set_geometry()


class udGeometryOBB(udGeometry):
  """
  Represents an oriented bounding box with a position, size, and orientation
  """
  def __init__(self, position=(0, 0, 0), size=(1, 1, 1), yawPitchRoll=(0, 0, 0)):
    super(udGeometryOBB, self).__init__()
    self.__position = position
    self.__size = size
    self.__yawPitchRoll = yawPitchRoll
    self._set_geometry()

  def _set_geometry(self):
    centreC = udGeometryDouble3()
    centreC.x = self.__position[0]
    centreC.y = self.__position[1]
    centreC.z = self.__position[2]
    extentsC = udGeometryDouble3()
    extentsC.x = self.__size[0]
    extentsC.y = self.__size[1]
    extentsC.z = self.__size[2]
    rotationsC = udGeometryDouble3()
    rotationsC.x = self.__yawPitchRoll[0]
    rotationsC.y = self.__yawPitchRoll[1]
    rotationsC.z = self.__yawPitchRoll[2]
    self._udGeometry_Deinit(self.pGeometry)
    self._udGeometry_InitOBB(self.pGeometry, centreC, extentsC, rotationsC)

  @property
  def position(self):
    """
    Position of the centre of the box
    """
    return self.__position

  @position.setter
  def position(self, position):
    self.__position = tuple([*position])
    self._set_geometry()

  @property
  def yawPitchRoll(self):
    """
    orientation of the box in yaw-pitch-roll (radians)
    """
    return self.__yawPitchRoll

  @yawPitchRoll.setter
  def yawPitchRoll(self, yawPitchRoll):
    self.__yawPitchRoll = tuple([*yawPitchRoll])
    self._set_geometry()

  @property
  def size(self):
    """
    length of the box sides
    """
    return self.__size

  @size.setter
  def size(self, size):
    assert len(size) == 3
    self.__size = tuple([*size])
    self._set_geometry()



class udGeometryHalfSpace(udGeometry):
  """
  Represents an infinite plane in 3D space defined by a normal and a point it passes through
  """
  def __init__(self, point, normal):
    self._point = point
    self._normal = normal
    super(udGeometryHalfSpace, self).__init__()
    self._set_geometry()

  def _set_geometry(self):
    pointC = udGeometryDouble3()
    pointC.x = self._point[0]
    pointC.y = self._point[1]
    pointC.z = self._point[2]

    normalC = udGeometryDouble3()
    normalC.x = self._normal[0]
    normalC.y = self._normal[1]
    normalC.z = self._normal[2]
    self._udGeometry_Deinit(self.pGeometry)
    self._udGeometry_InitHalfSpace(self.pGeometry, pointC, normalC)

  @property
  def point(self):
    """
    point that the plane passes through
    """
    return self._point

  @point.setter
  def point(self, value):
    self._point = value
    self._set_geometry()

  @property
  def normal(self):
    """
    3D vector normal to the plane
    """
    return self._normal

  @normal.setter
  def normal(self, value):
    self._normal = value
    self._set_geometry()

  def as_project_node(self, parent=None):
    raise NotImplementedError

class udGeometryInverse(udGeometry):
  """
  Inverse of an existing udGeometry object
  """
  def __init__(self, source: udGeometry):
    self._source = source
    super(udGeometryInverse, self).__init__()
    self._udGeometry_InitInverse(self.pGeometry, source.pGeometry)

  def as_project_node(self, parent=None):
    raise NotImplementedError

class udGeometryCSG(udGeometry):
  """
  Constructive Solid Geometry formed by set operations on existing udGeometry objects
  """
  def __init__(self, left: udGeometry, right: udGeometry, operation: udGeometryCSGOperation):
    self._left = left
    self._right = right
    super(udGeometryCSG, self).__init__()
    self._udGeometry_InitCSG(self.pGeometry, left.pGeometry, right.pGeometry, ctypes.c_uint(operation))

  def as_project_node(self, parent=None):
    raise NotImplementedError

class udGeometryPolygonPerspective(udGeometry):
  """
  A geometry filter representing a polygon selection from the perspective of a camera.
  polygonXY: list of 2D vertices of the polygon defined within the camera plane
  cameraMatrix: the camera matrix of the perspective the selection is taken from
  projectionMatrix: the projection matrix of the perspective the selection is taken from
  nearPlane: the distance from the camera position to place the near plane of the selection
  farPlane: the distance from the camera position to place the far plane of the selection
  """
  def __init__(self, polygonXY, projectionMatrix, cameraMatrix, nearPlane, farPlane):
    super(udGeometryPolygonPerspective, self).__init__()
    self._set_camera(cameraMatrix)
    self._set_projection(projectionMatrix)
    self._nearPlaneOffset = nearPlane
    self._farPlaneOffset = farPlane

    self._polygonXY = polygonXY
    self._set_geometry()

  def _set_geometry(self):
    cameraMatrixC = udGeometryDouble4x4()
    for i in range(16):
      cameraMatrixC.array[i] = self._cameraMatrix[i]

    projectionMatrixC = udGeometryDouble4x4()
    for i in range(16):
      projectionMatrixC.array[i] = self._cameraMatrix[i]

    xyArr = (udGeometryDouble2 * len(self._polygonXY))()
    for i, point in enumerate(self._polygonXY):
      xyArr[i].x = point[0]
      xyArr[i].y = point[1]

    self._udGeometry_Deinit(self.pGeometry)
    self._udGeometry_InitPolygonPerspective(self.pGeometry, xyArr, len(self._polygonXY), projectionMatrixC, cameraMatrixC, ctypes.c_double(self._nearPlaneOffset), ctypes.c_double(self._farPlaneOffset))

  def as_project_node(self, parent=None):
    raise NotImplementedError

  @property
  def nearPlane(self):
    return self._nearPlaneOffset

  @nearPlane.setter
  def nearPlane(self, value:float):
    self._nearPlaneOffset = value
    self._set_geometry()

  @property
  def farPlane(self):
    return self._farPlaneOffset

  @farPlane.setter
  def farPlane(self, value: float):
    self._farPlaneOffset = value
    self._set_geometry()

  @property
  def cameraMatrix(self):
    return self._cameraMatrix

  def _set_camera(self, value):
    if type(value) == np.ndarray:
      value = value.flatten()
    assert len(value) == 16
    self._cameraMatrix = value

  @cameraMatrix.setter
  def cameraMatrix(self, value):
    self._set_camera(value)
    self._set_geometry()

  @property
  def projectionMatrix(self):
    return self._projectionMatrix

  def _set_projection(self, value):
    if type(value) == np.ndarray:
      value = value.flatten()
    assert len(value) == 16
    self._projectionMatrix = value

  @projectionMatrix.setter
  def projectionMatrix(self, value):
    self._set_projection(value)
    self._set_geometry()

  @property
  def polygonXY(self):
    return self._polygonXY

  @polygonXY.setter
  def polygonXY(self, value):
    self._polygonXY = value
    self._set_geometry()


