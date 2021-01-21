import math
import numpy as np
from ctypes import *
from enum import IntEnum, unique
import platform
import os
import logging

logger = logging.getLogger(__name__)

class UdException(Exception):
  def printout(this):
    error = this.args[1]
    if (error == udError.ConnectionFailure):
      logger.error("Could not connect to server.")
    elif (error == udError.AuthFailure):
      logger.error("Username or Password incorrect.")
    elif (error == udError.OutOfSync):
      logger.error("Your clock doesn't match the remote server clock.")
    elif (error == udError.SecurityFailure):
      logger.error("Could not open a secure channel to the server.")
    elif (error == udError.ServerFailure):
      logger.error("Unable to negotiate with server, please confirm the server address")
    elif (error != udError.Success):
      logger.error("Error {}: {}; please consult udSDK documentation".format(this.args[1], this.args[0]))


def LoadUdSDK(SDKPath):
  global udSDKlib
  try:
    udSDKlib = CDLL(SDKPath)
  except OSError:
    logger.info(
      "No local udSDK shared object/dll found in current working directory, trying path in UDSDK_HOME environment variable...")
    SDKPath = os.environ.get("UDSDK_HOME")
    if SDKPath == None:
      raise FileNotFoundError("Environment variable UDSDK_HOME not set, please refer to udSDK documentation")

    if platform.system() == 'Windows':
      SDKPath += "/lib/win_x64/udSDK"

    # TODO Add support for these paths:
    elif platform.system() == "Linux":
      SDKPath +="/lib/ubuntu18.04_GCC_x64/libudSDK"

    # elif platform.system() == "Darwin":
    #    print("Platform not supported"
    else:
      logger.error("Platform {} not supported by this sample".format(platform.system()))
      exit()
    logger.info("Using udSDK shared object located at {}".format(SDKPath))
    print("using "+SDKPath)
    udSDKlib = CDLL(SDKPath)

@unique
class udError(IntEnum):
  Success = 0  # Indicates the operation was successful

  Failure = 1  # A catch-all value that is rarely used, internally the below values are favored
  InvalidParameter = 2  # One or more parameters is not of the expected format
  InvalidConfiguration = 3  # Something in the request is not correctly configured or has conflicting settings
  InvalidLicense = 4  # The required license isn't available or has expired
  SessionExpired = 5  # The udSDK Server has terminated your session

  NotAllowed = 6  # The requested operation is not allowed (usually this is because the operation isn't allowed in the current state)
  NotSupported = 7  # This functionality has not yet been implemented (usually some combination of inputs isn't compatible yet)
  NotFound = 8  # The requested item wasn't found or isn't currently available
  NotInitialized = 9  # The request can't be processed because an object hasn't been configured yet

  ConnectionFailure = 10  # There was a connection failure
  MemoryAllocationFailure = 11  # udSDK wasn't able to allocate enough memory for the requested feature
  ServerFailure = 12  # The server reported an error trying to fufil the request
  AuthFailure = 13  # The provided credentials were declined (usually username or password issue)
  SecurityFailure = 14  # There was an issue somewhere in the security system- usually creating or verifying of digital signatures or cryptographic key pairs
  OutOfSync = 15  # There is an inconsistency between the internal udSDK state and something external. This is usually because of a time difference between the local machine and a remote server

  ProxyError = 16  # There was some issue with the provided proxy information (either a proxy is in the way or the provided proxy info wasn't correct)
  ProxyAuthRequired = 17  # A proxy has requested authentication

  OpenFailure = 18  # A requested resource was unable to be opened
  ReadFailure = 19  # A requested resourse was unable to be read
  WriteFailure = 20  # A requested resource was unable to be written
  ParseError = 21  # A requested resource or input was unable to be parsed
  ImageParseError = 22  # An image was unable to be parsed. This is usually an indication of either a corrupt or unsupported image format

  Pending = 23  # A requested operation is pending.
  TooManyRequests = 24  # This functionality is currently being rate limited or has exhausted a shared resource. Trying again later may be successful
  Cancelled = 25  # The requested operation was cancelled (usually by the user)

  Timeout = 26 #!< The requested operation timed out. Trying again later may be successful
  OutstandingReferences = 27 #!< The requested operation failed because there are still references to this object
  ExceededAllowedLimit = 28 #!< The requested operation failed because it would exceed the allowed limits (generally used for exceeding server limits like number of projects)
  Count = 29  # Internally used to verify return values


def _HandleReturnValue(retVal):
  if retVal != udError.Success:
    err = udError(retVal)
    raise UdException(err.name, err.value)

def udExceptionDecorator(nativeFunction):
  def returnFunction(*args, **kwargs):
    _HandleReturnValue(nativeFunction(*args, **kwargs))
  return returnFunction


@unique
class udRenderContextPointMode(IntEnum):
    Rectangles = 0 #!< This is the default, renders the voxels expanded as screen space rectangles
    Cubes = 1 #!< Renders the voxels as cubes
    Points = 2 #!< Renders voxels as a single point (Note: does not accurately reflect the 'size' of voxels)

    Count = 3 #!< Total number of point modes. Used internally but can be used as an iterator max when displaying different point modes.

@unique
class udRenderContextFlags(IntEnum):

    none = 0, #!< Render the points using the default configuration.

    PreserveBuffers = 1 << 0 #!< The colour and depth buffers won't be cleared before drawing and existing depth will be respected
    ComplexIntersections = 1 << 1 #!< This flag is required in some scenes where there is a very large amount of intersecting point clouds
      #!< It will internally batch rendering with the udRCF_PreserveBuffers flag after the first render.
    BlockingStreaming = 1 << 2 #!< This forces the streamer to load as much of the pointcloud as required to give an accurate representation in the current view. A small amount of further refinement may still occur.
    LogarithmicDepth = 1 << 3 #!< Calculate the depth as a logarithmic distribution.
    ManualStreamerUpdate = 1 << 4 #!< The streamer won't be updated internally but a render call without this flag or a manual streamer update will be required


@unique
class udRenderTargetMatrix(IntEnum):
  Camera = 0  # The local to world-space transform of the camera (View is implicitly set as the inverse)
  View = 1  # The view-space transform for the model (does not need to be set explicitly)
  Projection = 2  # The projection matrix (default is 60 degree LH)
  Viewport = 3  # Viewport scaling matrix (default width and height of viewport)
  Count = 4

class udVoxelID(Structure):
  _fields_ = \
    [
      ("index", c_uint64),#internal index info
      ("pTrav", c_uint64),#internal traverse info
      ("pRenderInfo", c_void_p),#internal render info
    ]
class udRenderPicking(Structure):
  _fields_ = \
    [
      #input variables:
      ("x", c_uint),#!< Mouse X position in udRenderTarget space
      ("y", c_uint),#!< Mouse Y position in udRenderTarget space
      #output variables
      ("hit", c_uint32),
      ("isHighestLOD", c_uint32),
      ("modelIndex", c_uint),
      ("pointCentre", c_double * 3),
      ("voxelID", POINTER(udVoxelID))
    ]


class udRenderSettings(Structure):
  _fields_=[
    ("flags", c_int),
    ("pPick", POINTER(udRenderPicking)),
    ("pointMode", c_int),
    ("pFilter", c_void_p),
  ]
  def __init__(self):
    super(udRenderSettings, self).__init__()
    self.pick = udRenderPicking()
    self.pPick = pointer(self.pick)

  def set_pick(self, x, y):
    self.pick.x = x
    self.pick.y = y

class udStdAttribute(IntEnum):
  udSA_GPSTime = 0
  udSA_PrimitiveID = 1
  udSA_ARGB = 2
  udSA_Normal = 3
  udSA_Intensity = 4
  udSA_NIR = 5
  udSA_ScanAngle = 6
  udSA_PointSourceID = 7
  udSA_Classification = 8
  udSA_ReturnNumber = 9
  udSA_NumberOfReturns = 10
  udSA_ClassificationFlags = 11
  udSA_ScannerChannel = 12
  udSA_ScanDirection = 13
  udSA_EdgeOfFlightLine = 14
  udSA_ScanAngleRank = 15
  udSA_LasUserData = 16
  udSA_Count = 17
  udSA_AllAttributes = udSA_Count
  udSA_First = 0

class udStdAttributeContent(IntEnum):
  udSAC_None = 0
  udSAC_GPSTime = (1 << udStdAttribute.udSA_GPSTime)
  udSAC_PrimitiveID = (1 << udStdAttribute.udSA_PrimitiveID)
  udSAC_ARGB = (1 << udStdAttribute.udSA_ARGB)
  udSAC_Normal = (1 << udStdAttribute.udSA_Normal)
  udSAC_Intensity = (1 << udStdAttribute.udSA_Intensity)
  udSAC_NIR = (1 << udStdAttribute.udSA_NIR)
  udSAC_ScanAngle = (1 << udStdAttribute.udSA_ScanAngle)
  udSAC_PointSourceID = (1 << udStdAttribute.udSA_PointSourceID)
  udSAC_Classification = (1 << udStdAttribute.udSA_Classification)
  udSAC_ReturnNumber = (1 << udStdAttribute.udSA_ReturnNumber)
  udSAC_NumberOfReturns = (1 << udStdAttribute.udSA_NumberOfReturns)
  udSAC_ClassificationFlags = (1 << udStdAttribute.udSA_ClassificationFlags)
  udSAC_ScannerChannel = (1 << udStdAttribute.udSA_ScannerChannel)
  udSAC_ScanDirection = (1 << udStdAttribute.udSA_ScanDirection)
  udSAC_EdgeOfFlightLine = (1 << udStdAttribute.udSA_EdgeOfFlightLine)
  udSAC_ScanAngleRank = (1 << udStdAttribute.udSA_ScanAngleRank)
  udSAC_LasUserData = (1 << udStdAttribute.udSA_LasUserData)

  udSAC_AllAttributes = (1 << udStdAttribute.udSA_AllAttributes) - 1
  udSAC_64BitAttributes = udSAC_GPSTime
  udSAC_32BitAttributes = udSAC_PrimitiveID + udSAC_ARGB + udSAC_Normal
  udSAC_16BitAttributes = udSAC_Intensity + udSAC_NIR + udSAC_ScanAngle + udSAC_PointSourceID


class udAttributeSet(Structure):
  _fields_ = [("standardContent", c_int),
              ("count", c_uint32),
              ("allocated", c_uint32),
              ("pDescriptors", c_void_p)
              ]


class udPointCloudHeader(Structure):
  _fields_ = [("scaledRange", c_double),
              ("unitMeterScale", c_double),
              ("totalLODLayers", c_uint32),
              ("convertedResolution", c_double),
              ("storedMatrix", c_double * 16),
              ("attributes", udAttributeSet),
              ("baseOffset", c_double * 3),
              ("pivot", c_double * 3),
              ("boundingBoxCenter", c_double * 3),
              ("boundingBoxExtents", c_double * 3)
              ]


class udRenderInstance(Structure):
  """
  Represents a renderInstance;
  position, rotation and scale can be modified
  directly to update the transformation matrix of the instance

  This object is passed to udRenderContext.Render in order to
  define the properties of the models to be rendered
  """
  _fields_ = [("pPointCloud", c_void_p),
              ("matrix", c_double * 16),
              ("pFilter", c_void_p),
              ("pVoxelShader", c_void_p),
              ("pVoxelUserData", c_void_p)
              ]
  position = [0, 0, 0] #the position of the instance in world space
  rotation = [0, 0, 0] #the rotation about the point pivot
  scale = [1, 1, 1] # x, y and z scaling factors
  pivot = [0, 0, 0] #point to rotate about

  def __init__(self, model):
    super().__init__()
    self.model = model
    self.pivot = [*model.header.pivot]
    self.pPointCloud = model.pPointCloud
    self.position = [0, 0, 0]
    self.rotation = [0, 0, 0]
    self.scale = [1, 1, 1]
    self.skew = [0, 0, 0]
    self.matrix[15] = 1

  @property
  def scaleMode(self):
    return self.__scaleMode

  @scaleMode.setter
  def scaleMode(self, mode):
    if mode == 'modelSpace':
      self.scale = 1 / 2 / np.max(self.model.header.boundingBoxExtents)
    elif mode == 'minDim':
      self.scale = 1 / 2 / np.min(self.model.header.boundingBoxExtents)
    elif mode == 'fsCentreOrigin':
      self.scale = self.model.header.scaledRange
    else:
      raise AttributeError("Invalid scaling mode: "+ mode)
    centrePos = [-self.model.header.pivot[0] * self.scale[0], -self.model.header.pivot[1] * self.scale[1], -self.model.header.pivot[2] * self.scale[2]]
    self.position = centrePos
    self.__scaleMode = mode

  @property
  def position(self):
    return self.__position

  @position.setter
  def position(self, position):
    self.matrix[12:15] = position
    self.__position = tuple(position)

  @property
  def scale(self):
    try:
      return self.__scale
    except AttributeError:
      return (1, 1, 1)

  @scale.setter
  def scale(self, scale):
    #support either scalar of vecor scaling:
    try:
      assert(len(scale) == 3)
    except TypeError:
      scale = [scale, scale, scale]
    self.update_transformation(self.rotation, scale, self.skew)

  @property
  def rotation(self):
    return self.__rotation

  @rotation.setter
  def rotation(self, rotation):
    rotation = [rotation[0] % (2*np.pi), rotation[1] % (2*np.pi), rotation[2] % (2*np.pi)]
    self.update_transformation(rotation, self.scale, self.skew)

  @property
  def skew(self):
    try:
      return self.__skew
    except AttributeError:
      self.__skew = (0, 0, 0)
      return self.__skew

  @skew.setter
  def skew(self, skew):
    self.update_transformation(self.rotation, self.scale, skew)

  def set_transform_default(self):
    #self.skew=[0]*3
    self.scale = self.model.header.scaledRange
    #self.rotation = [self.model.header.storedMatrix[0]/self.scale[0],self.model.header.storedMatrix[5]/self.scale[1],self.model.header.storedMatrix[10]/self.scale[2]]
    self.position = self.model.header.storedMatrix[12:15]

  def update_transformation(self, rotation, scale, skew=(0, 0, 0)):
    """
    sets the rotation and scaling elements of the renderInstance
    We are setting the parameters of the 4x4 homogeneous transformation matrix
    """
    self.__rotation = tuple(rotation)
    self.__scale = tuple(scale)
    self.__skew = tuple(skew)

    sy = math.sin(rotation[2])
    cy = math.cos(rotation[2])
    sp = math.sin(rotation[0])
    cp = math.cos(rotation[0])
    sr = math.sin(rotation[1])
    cr = math.cos(rotation[1])
    trans = np.identity(4)
    piv = np.identity(4)
    piv[3] = -np.array([*self.pivot, -1])

    smat = np.identity(4)
    smat[0, 0] = scale[0]
    smat[1, 1] = scale[1]
    smat[2, 2] = scale[2]
    smat[0, 3] = skew[0]
    smat[1, 3] = skew[1]
    smat[2, 3] = skew[2]

    trans[0] = [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr, 0]
    trans[1] = [sy * cp, (sy * sp * sr + cy * cr), sy * sp * cr - cy * sr, 0]
    trans[2] = [-sp, cp * sr,   cp * cr, 0]

    trans = smat.dot(trans)
    trans[3] = [*self.position, 1]
    self.matrix = (c_double * 16)(*(piv.dot(trans).dot(np.linalg.inv(piv))).flatten())

class udContext:
  def __init__(self):
    self._udContext_Connect = getattr(udSDKlib, "udContext_Connect")
    self._udContext_Disconnect = getattr(udSDKlib, "udContext_Disconnect")
    self._udContext_TryResume = getattr(udSDKlib, "udContext_TryResume")
    self.pContext = c_void_p(0)
    self.isConnected = False
    self.url = ""
    self.username = ""
  def Connect(self, url=None, applicationName=None, username=None, password=None):
    if password is None:
      raise Exception("Password must be set")

    if url is not None:
      self.url = url

    if applicationName is not None:
      self.appName = applicationName

    if username is not None:
      self.username = username

    username = self.username.encode('utf8')
    applicationName = self.appName.encode('utf8')
    url = self.url.encode('utf8')
    password = password.encode('utf8')


    _HandleReturnValue(self._udContext_Connect(byref(self.pContext), url, applicationName,
                                               username, password))
    self.isConnected = True

  def Disconnect(self, endSession=True):
    _HandleReturnValue(self._udContext_Disconnect(byref(self.pContext), c_int32(endSession)))
    self.isConnected = False

  def __del__(self):
    pass
    #self.Disconnect()

  def try_resume(self, url=None, applicationName=None, username=None, tryDongle = False):
    if url is not None:
      self.url = url
    url = self.url.encode('utf8')
    if applicationName is not None:
      self.appName = applicationName
    applicationName = self.appName.encode('utf8')

    if username is not None:
      self.username = username
    username = self.username.encode('utf8')

    _HandleReturnValue(self._udContext_TryResume(byref(self.pContext), url, applicationName, username, tryDongle))
    self.isConnected = True

class udRenderContext:
  def __init__(self,context:udContext =None):
    """Create object without attached context"""
    self.udRenderContext_Create = getattr(udSDKlib, "udRenderContext_Create")
    self.udRenderContext_Destroy = getattr(udSDKlib, "udRenderContext_Destroy")
    self.udRenderContext_Render = getattr(udSDKlib, "udRenderContext_Render")
    self.renderer = c_void_p(0)
    self.context = context

    if context is not None:
      self.Create(context)

  def Create(self, context):
    self.context = context
    _HandleReturnValue(self.udRenderContext_Create(context.pContext, byref(self.renderer)))

  def Destroy(self):
    _HandleReturnValue(self.udRenderContext_Destroy(byref(self.renderer), True))
    #print("Logged out of udSDK")

  def Render(self, renderView, renderInstances, renderSettings=c_void_p(0)):
    if isinstance(renderInstances,list):
      renderInstances = (udRenderInstance*len(renderInstances))(*renderInstances)
    _HandleReturnValue(
      self.udRenderContext_Render(self.renderer, renderView.renderView, renderInstances, len(renderInstances), renderSettings))

  def __del__(self):
    self.Destroy()


class udRenderTarget:
  def __init__(self, width=1280, height=720, clearColour=0, context=None, renderContext=None):
    self.udRenderTarget_Create = getattr(udSDKlib, "udRenderTarget_Create")
    self.udRenderTarget_Destroy = getattr(udSDKlib, "udRenderTarget_Destroy")
    self.udRenderTarget_SetTargets = getattr(udSDKlib, "udRenderTarget_SetTargets")
    self.udRenderTarget_SetTargetsWithPitch = getattr(udSDKlib, "udRenderTarget_SetTargetsWithPitch")
    self.udRenderTarget_SetMatrix = getattr(udSDKlib, "udRenderTarget_SetMatrix")
    self.udRenderTarget_GetMatrix = getattr(udSDKlib, "udRenderTarget_GetMatrix")
    self.renderView = c_void_p(0)
    self.renderSettings = udRenderSettings()
    self.filter = None

    self.width = width
    self.height = height
    self.clearColour = clearColour
    self.context = context
    self.renderContext = renderContext
    # if the contexts are not set we assume the user is setting them manually
    if context is None or renderContext is None:
      return

    # these are initialised when setting the size:
    self.colourBuffer = None
    self.depthBuffer = None
    self.set_size()

    self.cameraMatrix = None
    self.set_view()

  def set_filter(self, queryFilter):
    self.filter = queryFilter
    if queryFilter is not None:
      self.renderSettings.pFilter = queryFilter.pFilter
    else:
      self.renderSettings.pFilter = c_void_p(0)

  def set_view(self, x=0, y=-5, z=0, roll=0, pitch=0, yaw=0):
    """
    Sets the postion and rotation of the matrix to that specified;
    rotations are about the global axes
    """
    sy = math.sin(yaw)
    cy = math.cos(yaw)
    sp = math.sin(pitch)
    cp = math.cos(pitch)
    sr = math.sin(roll)
    cr = math.cos(roll)
    self.cameraMatrix = [
      cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr, 0,
      sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr, 0,
      -sp, cp * sr, cp * cr, 0,
      x, y, z, 1
    ]
    self.SetMatrix(udRenderTargetMatrix.Camera, self.cameraMatrix)

  def set_size(self, width=None, height=None):
    if width is None:
      width = self.width
    if height is None:
      height = self.height

    self.colourBuffer = (c_int32 * (width * height))()
    self.depthBuffer = (c_float * (width * height))()
    if self.context is not None and self.renderContext is not None:
      self.Create(self.context, self.renderContext, width, height)
      self.SetTargets(self.colourBuffer, self.clearColour, self.depthBuffer)
    else:
      raise Exception("Context and renderer must be created before calling set_size")

  def rgb_colour_buffer(self):
    """returns the colour buffer as a """
    out = []
    for colour in self.colourBuffer:
      out.append((colour>>16 & 0xFF, colour>>8&0xFF,colour&0xFF))
    return out

  def plot_view(self):
    """plots the current view as an rgb image in matpotlib"""
    import matplotlib.pyplot as plt
    im = np.array(self.rgb_colour_buffer()).reshape([self.height,self.width,3])
    plt.imshow(im)
    plt.show()

  def Create(self, context, udRenderer, width, height):
    self.context = context
    self.renderContext = udRenderer
    self.width = width
    self.height = height
    if self.renderView is not c_void_p(0):
      self.Destroy()
    _HandleReturnValue(
      self.udRenderTarget_Create(udRenderer.context.pContext, byref(self.renderView), udRenderer.renderer, width,
                                 height))

  def Destroy(self):
    _HandleReturnValue(self.udRenderTarget_Destroy(byref(self.renderView)))

  def SetTargets(self, colorBuffer, clearColor, depthBuffer):
    _HandleReturnValue(
      self.udRenderTarget_SetTargets(self.renderView, byref(colorBuffer), clearColor, byref(depthBuffer)))

  def SetMatrix(self, matrixType:udRenderTargetMatrix, matrix):
    cMatrix = (c_double * 16)(*matrix)
    _HandleReturnValue(self.udRenderTarget_SetMatrix(self.renderView, matrixType, byref(cMatrix)))

  def GetMatrix(self, matrixType):
    cMatrix = (c_double * 16)()
    _HandleReturnValue(self.udRenderTarget_GetMatrix(self.renderView, matrixType, byref(cMatrix)))
    return [*cMatrix]

  def __del__(self):
    self.Destroy()


class udPointCloud:
  def __init__(self, path=None, context=None):
    self.udPointCloud_Load = getattr(udSDKlib, "udPointCloud_Load")
    self.udPointCloud_Unload = getattr(udSDKlib, "udPointCloud_Unload")
    self.udPointCloud_GetMetadata = getattr(udSDKlib, "udPointCloud_GetMetadata")
    self.udPointCloud_GetHeader = getattr(udSDKlib, "udPointCloud_GetHeader")
    self.udPointCloud_Export = getattr(udSDKlib, "udPointCloud_Export")
    self.udPointCloud_GetNodeColour = getattr(udSDKlib, "udPointCloud_GetNodeColour")
    self.udPointCloud_GetNodeColour64 = getattr(udSDKlib, "udPointCloud_GetNodeColour64")
    self.udPointCloud_GetAttributeAddress = getattr(udSDKlib, "udPointCloud_GetAttributeAddress")
    self.udPointCloud_GetStreamingStatus = getattr(udSDKlib, "udPointCloud_GetStreamingStatus")
    self.pPointCloud = c_void_p(0)
    self.header = udPointCloudHeader()

    if context is not None and path is not None:
      assert not (context is None or path is None)
      self.Load(context, path)

  def Load(self, context:udContext, modelLocation:str):
    self.path = modelLocation
    _HandleReturnValue(
      self.udPointCloud_Load(context.pContext, byref(self.pPointCloud), modelLocation.encode('utf8'), byref(self.header)))

  def Unload(self):
    if self.pPointCloud!=0:
      _HandleReturnValue(self.udPointCloud_Unload(byref(self.pPointCloud)))
    self.pPointCloud = 0

  def GetMetadata(self):
    pMetadata = c_char_p(0)
    _HandleReturnValue(self.udPointCloud_GetMetadata(self.pPointCloud, byref(pMetadata)))
    return pMetadata.value.decode('utf8')

  def __eq__(self, other):
    if hasattr(other, "path") and hasattr(self, "path"):
      return other.path == self.path
    else:
      return False

  def __del__(self):
    self.Unload()

class udPointBufferI64(Structure):
  _fields_ = [
    ("pPositions", c_void_p),  # !< Flat array of XYZ positions in the format XYZXYZXYZXYZXYZXYZXYZ...
    ("attributes", udAttributeSet),  # !< Information on the attributes that are available in this point buffer
    ("pAttributes", c_void_p),
    ("positionStride", c_uint32),
    # !< Total bytes between the start of one position and the start of the next (currently always 24 (8 bytes per int64 * 3 int64))
    ("attributeStride", c_uint32),
    # !< Total number of bytes between the start of the attibutes of one point and the first byte of the next attribute
    ("pointCount", c_uint32),  # !< How many points are currently contained in this buffer
    ("pointsAllocated", c_uint32),  # !< Total number of points that can fit in this udPointBufferF64
    ("_reserved", c_uint32)  # !< Reserved for internal use
  ]
  def __init__(self, maxPoints, attributeSet=None):
    if attributeSet is None:
      self.attributeSet = udAttributeSet()
      self.attributeSet.standardContent = udStdAttributeContent.udSAC_ARGB
    else:
      self.attributeSet = attributeSet
    super(udPointBufferI64, self).__init__()
    self.udPointBufferI64_Create = udExceptionDecorator(udSDKlib.udPointBufferI64_Create)
    self.udPointBufferI64_Destroy = udExceptionDecorator(udSDKlib.udPointBufferI64_Destroy)
    self.udPointBufferI64_Create(byref(self), maxPoints, self.attributeSet)

  def __del__(self):
    self.udPointBufferI64_Destroy(pointer(self))

class udPointBufferF64(Structure):
  _fields_ = [
    ("pPositions", c_void_p),  # !< Flat array of XYZ positions in the format XYZXYZXYZXYZXYZXYZXYZ...
    ("pAttributes", c_void_p),
    ("attributes", udAttributeSet),  # !< Information on the attributes that are available in this point buffer
    ("positionStride", c_uint32),
    # !< Total bytes between the start of one position and the start of the next (currently always 24 (8 bytes per int64 * 3 int64))
    ("attributeStride", c_uint32),
    # !< Total number of bytes between the start of the attibutes of one point and the first byte of the next attribute
    ("pointCount", c_uint32),  # !< How many points are currently contained in this buffer
    ("pointsAllocated", c_uint32),  # !< Total number of points that can fit in this udPointBufferF64
    ("_reserved", c_uint32)  # !< Reserved for internal use
  ]
  def __init__(self):
    #super(udPointBufferI64, self).__init__()
    self.udPointBufferF64_Create = getattr(udSDKlib, "udPointBufferF64_Create")
    self.udPointBufferF64_Destroy = getattr(udSDKlib, "udPointBufferF64_Destroy")


class udQueryFilter:
  def __init__(self):
    self.udQueryFilter_Create = getattr(udSDKlib, "udQueryFilter_Create")
    self.udQueryFilter_Destroy = getattr(udSDKlib, "udQueryFilter_Destroy")
    self.udQueryFilter_SetInverted = getattr(udSDKlib, "udQueryFilter_SetInverted")
    self.udQueryFilter_SetAsBox = getattr(udSDKlib, "udQueryFilter_SetAsBox")
    self.udQueryFilter_SetAsCylinder = getattr(udSDKlib, "udQueryFilter_SetAsCylinder")
    self.udQueryFilter_SetAsSphere = getattr(udSDKlib, "udQueryFilter_SetAsSphere")

    self.pFilter = c_void_p(0)
    self.__isActive = True
    self.create()

  @property
  def position(self):
    return self.__position

  @position.setter
  def position(self, position):
    self.__position = tuple([*position])
    self.SetAsCylinder(position,self.radius,self.halfHeight, self.yawPitchRoll)

  def create(self):
    _HandleReturnValue(self.udQueryFilter_Create(byref(self.pFilter)))

  def __del__(self):
    _HandleReturnValue(self.udQueryFilter_Destroy(byref(self.pFilter)))

  def SetInverted(self, inverted: bool):
    _HandleReturnValue(self.udQueryFilter_SetInverted(self.pFilter, inverted))

  def SetAsBox(self, centrePoint, halfSize, yawPitchRoll):
    centrePoint = (c_double *3)(*centrePoint)
    halfSize = (c_double * 3)(*halfSize)
    yawPitchRoll = (c_double*3)(*yawPitchRoll)
    _HandleReturnValue(self.udQueryFilter_SetAsBox(self.pFilter, centrePoint, halfSize, yawPitchRoll))

  def SetAsCylinder(self, centrePoint, radius, halfHeight, yawPitchRoll):
    centrePoint = (c_double *3)(*centrePoint)
    halfHeight = c_double(halfHeight)
    yawPitchRoll = (c_double*3)(*yawPitchRoll)
    _HandleReturnValue(
      self.udQueryFilter_SetAsCylinder(self.pFilter, centrePoint, radius, halfHeight, yawPitchRoll))

  def SetAsSphere(self, centrePoint, radius):
    centrePoint = (c_double *3)(*centrePoint)
    radius = c_double(radius)
    _HandleReturnValue(self.udQueryFilter_SetAsSphere(self.pFilter, centrePoint, radius))

class udQuerySphereFilter(udQueryFilter):
  def __init__(self, position = [0,0,0], radius = 1):
    self.__radius = radius
    self.__position = position

    self.SetAsSphere(position, self.radius, self.yawPitchRoll)

  @property
  def position(self):
    return self.__position

  @position.setter
  def position(self, position):
    self.__position = tuple([*position])
    self.SetAsSphere(position, self.radius, self.yawPitchRoll)
  @property
  def radius(self):
    return self.__radius

  @radius.setter
  def radius(self, radius):
    self.__radius = tuple([*radius])
    self.SetAsSphere(self.position, radius)

class udQueryBoxFilter(udQueryFilter):

  def __init__(self, position=[0,0,0], size=[1,1,1], yawPitchRoll=[0,0,0]):
    super(udQueryBoxFilter, self).__init__()
    self.__size = size
    self.__yawPitchRoll = yawPitchRoll
    self.position = position
    self.size = size
    self.yawPitchRoll = yawPitchRoll

  def SetAsBox(self):
    super().SetAsBox(self.position, [self.__size[0]/2, self.__size[1]/2, self.__size[2]/2], self.yawPitchRoll)

  @property
  def position(self):
    return self.__position

  @position.setter
  def position(self, position):
    self.__position = tuple([*position])
    self.SetAsBox()

  @property
  def yawPitchRoll(self):
    return self.__yawPitchRoll

  @yawPitchRoll.setter
  def yawPitchRoll(self, yawPitchRoll):
    self.__yawPitchRoll = tuple([*yawPitchRoll])
    self.SetAsBox()

  @property
  def size(self):
    return self.__size

  @size.setter
  def size(self, size):
    self.__size = tuple([*size])
    self.SetAsBox()

class udQueryContext:
  def __init__(self, context: udContext, pointcloud: udPointCloud, filter: udQueryFilter):
    self.udQueryContext_Create = getattr(udSDKlib, "udQueryContext_Create")
    self.udQueryContext_ChangeFilter = getattr(udSDKlib, "udQueryContext_ChangeFilter")
    self.udQueryContext_ChangePointCloud = getattr(udSDKlib, "udQueryContext_ChangePointCloud")
    self.udQueryContext_ExecuteF64 = getattr(udSDKlib, "udQueryContext_ExecuteF64")
    self.udQueryContext_ExecuteI64 = getattr(udSDKlib, "udQueryContext_ExecuteI64")
    self.udQueryContext_Destroy = getattr(udSDKlib, "udQueryContext_Destroy")

    self.context = context
    self.pQueryContext = c_void_p(0)
    self.pointcloud = pointcloud
    self.filter = filter
    self.Create()


  def Create(self):
    _HandleReturnValue(self.udQueryContext_Create(self.context.pContext, byref(self.pQueryContext), self.pointcloud.pPointCloud, self.filter.pFilter))

  def ChangeFilter(self, filter: udQueryFilter):
    self.filter = filter
    _HandleReturnValue(self.udQueryContext_ChangeFilter(self.pQueryContext, filter.pFilter))

  def ChangePointCloud(self, pointcloud: udPointCloud):
    self.pointcloud = pointcloud
    _HandleReturnValue(self.udQueryContext_ChangePointCloud(self.pQueryContext, pointcloud.pPointCloud))

  def ExecuteF64(self, points: udPointBufferF64):
    retVal = self.udQueryContext_ExecuteF64(self.pQueryContext, points)
    if retVal == udError.NotFound:
      return True
    _HandleReturnValue(retVal)
    return False

  def ExecuteI64(self, points:udPointBufferI64):
    retVal = self.udQueryContext_ExecuteI64(self.pQueryContext, points)
    if retVal == udError.NotFound:
      return True
    _HandleReturnValue(retVal)
    return False

  def Destroy(self):
    _HandleReturnValue(self.udQueryContext_Destroy(byref(self.pQueryContext)))

class udStreamer(Structure):
  _fields_ = [
    ("active", c_int32),
    ("memoryInUse", c_int64),
    ("modelsActive", c_int),
    ("starvedTimeMsSinceLastUpdate", c_int),
  ]
  def __init__(self):
    super(udStreamer, self).__init__()
    self.udStreamer_Update = getattr(udSDKlib, "udStreamer_Update")

  def update(self):
    _HandleReturnValue(self.udStreamer_Update(self))


