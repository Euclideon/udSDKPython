from enum import IntEnum, unique
from ctypes import *
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

class udGeometryDouble2(Structure):
  _fields_=[
    ('x', c_double),
    ('y', c_double)
    ]

class udGeometryDouble3(Structure):
  _fields_=[
    ('x', c_double),
    ('y', c_double)
    ('z', c_double)
  ]

class udGeometryDouble3(Structure):
  _fields_=[
    ('array', c_double*16)
  ]

class udGeometry():

  _pGeom = c_void_p(0)
  def __init__(self):
    self._udGeometry_Create = getattr(udSDK.udSDKlib, "udGeometry_Create")
    self._udGeometry_Destroy = getattr(udSDK.udSDKlib, "udGeometry_Destroy")
    self._udGeometry_Deinit = getattr(udSDK.udSDKlib, "udGeometry_Deinit")
    self._udGeometry_InitOBB = getattr(udSDK.udSDKlib, "udGeometry_InitOBB")
    self._udGeometry_InitAABBFromCentreExtents = getattr(udSDK.udSDKlib, "udGeometry_InitAABBFromCentreExtents")
    self._udGeometry_InitAABBFromMinMax = getattr(udSDK.udSDKlib, "udGeometry_InitAABBFromMinMax")
    self._udGeometry_InitSphere = getattr(udSDK.udSDKlib, "udGeometry_InitSphere")
    self._udGeometry_InitCapsule = getattr(udSDK.udSDKlib, "udGeometry_InitCapsule")
    self._udGeometry_InitCylinderFromCenterAndHeight = getattr(udSDK.udSDKlib, "_udGeometry_InitCylinderFromCenterAndHeight")
    self._udGeometry_InitCylinderFromEndPoints = getattr(udSDK.udSDKlib, "udGeometry_InitCylinderFromEndPoints")
    self._udGeometry_InitHalfSpace = getattr(udSDK.udSDKlib, "udGeometry_InitHalfSpace")
    self._udGeometry_InitCSG = getattr(udSDK.udSDKlib, "udGeometry_InitCSG")
    self._udGeometry_InitPolygonPerspective = getattr(udSDK.udSDKlib, "udGeometry_InitPolygonPerspective")
    self._udGeometry_InitPolygonXY = getattr(udSDK.udSDKlib, "udGeometry_InitPolygonXY")
    self._udGeometry_InitRectangleXY = getattr(udSDK.udSDKlib, "udGeometry_InitRectangleXY")
    self._udGeometry_InitCircleXY = getattr(udSDK.udSDKlib, "udGeometry_InitCircleXY")
    self._udGeometry_InitInverse = getattr(udSDK.udSDKlib, "udGeometry_InitInverse")
    self._udGeometry_Destroy = getattr(udSDK.udSDKlib, "udGeometry_Destroy")

    udSDK._HandleReturnValue(self._udGeometry_Create(byref(self._pGeom)))

  def __del__(self):
    self._udGeometry_Deinit(self._pGeom)
    self._udGeometry_Destroy(byref(self._pGeom))

class udGeometrySphere(udGeometry):
  def __init__(self, centre, radius):
    super(udGeometrySphere, self).__init__()
    centreC = udGeometryDouble3()
    centreC.x = centre[0]
    centreC.y = centre[1]
    centreC.z = centre[2]
    self._udGeometry_InitSphere(self._pGeom, centreC, c_double(radius))

class udGeometryOBB(udGeometry):
  def __init__(self, centre, extents, rotations):
    super(udGeometryOBB, self).__init__()
    centreC = udGeometryDouble3()
    centreC.x = centre[0]
    centreC.y = centre[1]
    centreC.z = centre[2]
    extentsC = udGeometryDouble3()
    extentsC.x = extents[0]
    extentsC.y = extents[1]
    extentsC.z = extents[2]
    rotationsC = udGeometryDouble3()
    rotationsC.x = rotations[0]
    rotationsC.y = rotations[1]
    rotationsC.z = rotations[2]
    self._udGeometry_InitOBB(self._pGeom, centreC, extentsC, rotationsC)




