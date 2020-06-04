import math
from ctypes import *
from enum import IntEnum, unique
import platform
import os
import logging

logger = logging.getLogger(__name__)
class VdkException(Exception):
  def printout(this):
    vaultError = this.args[1]
    if (vaultError == vdkError.ConnectionFailure):
      logger.error("Could not connect to server.")
    elif (vaultError == vdkError.AuthFailure):
      logger.error("Username or Password incorrect.")
    elif (vaultError == vdkError.OutOfSync):
      logger.error("Your clock doesn't match the remote server clock.")
    elif (vaultError == vdkError.SecurityFailure):
      logger.error("Could not open a secure channel to the server.")
    elif (vaultError == vdkError.ServerFailure):
      logger.error("Unable to negotiate with server, please confirm the server address")
    elif (vaultError != vdkError.Success):
      logger.error("Error {}: {}; please consult Vault SDK documentation".format(this.args[1], this.args[0]))


def LoadVaultSDK(SDKPath):
  global vaultSDK
  try:
    vaultSDK = CDLL(SDKPath)
  except OSError:
    logger.info(
      "No local Vault shared object/dll found in current working directory, trying path in VAULTSDK_HOME environment variable...")
    SDKPath = os.environ.get("VAULTSDK_HOME")
    if SDKPath == None:
      raise FileNotFoundError("Environment variable VAULTSDK_HOME not set, please refer to Vault SDK documentation")

    if platform.system() == 'Windows':
      SDKPath += "/lib/win_x64/vaultSDK"

    # TODO Add support for these paths:
    elif platform.system() == "Linux":
      SDKPath +="/lib/ubuntu18.04_GCC_x64/libvaultSDK.so"

    # elif platform.system() == "Darwin":
    #    print("Platform not supported"
    else:
      logger.error("Platform {} not supported by this sample".format(platform.system()))
      exit()
    logger.info("Using Vault SDK shared object located at {}".format(SDKPath))
    vaultSDK = CDLL(SDKPath)


@unique
class vdkError(IntEnum):
  Success = 0  # Indicates the operation was successful

  Failure = 1  # A catch-all value that is rarely used, internally the below values are favored
  InvalidParameter = 2  # One or more parameters is not of the expected format
  InvalidConfiguration = 3  # Something in the request is not correctly configured or has conflicting settings
  InvalidLicense = 4  # The required license isn't available or has expired
  SessionExpired = 5  # The Vault Server has terminated your session

  NotAllowed = 6  # The requested operation is not allowed (usually this is because the operation isn't allowed in the current state)
  NotSupported = 7  # This functionality has not yet been implemented (usually some combination of inputs isn't compatible yet)
  NotFound = 8  # The requested item wasn't found or isn't currently available
  NotInitialized = 9  # The request can't be processed because an object hasn't been configured yet

  ConnectionFailure = 10  # There was a connection failure
  MemoryAllocationFailure = 11  # VDK wasn't able to allocate enough memory for the requested feature
  ServerFailure = 12  # The server reported an error trying to fufil the request
  AuthFailure = 13  # The provided credentials were declined (usually username or password issue)
  SecurityFailure = 14  # There was an issue somewhere in the security system- usually creating or verifying of digital signatures or cryptographic key pairs
  OutOfSync = 15  # There is an inconsistency between the internal VDK state and something external. This is usually because of a time difference between the local machine and a remote server

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

  Count = 26  # Internally used to verify return values


def _HandleReturnValue(retVal):
  if retVal != vdkError.Success:
    err = vdkError(retVal)
    raise VdkException(err.name, err.value)


@unique
class vdkRenderViewMatrix(IntEnum):
  Camera = 0  # The local to world-space transform of the camera (View is implicitly set as the inverse)
  View = 1  # The view-space transform for the model (does not need to be set explicitly)
  Projection = 2  # The projection matrix (default is 60 degree LH)
  Viewport = 3  # Viewport scaling matrix (default width and height of viewport)
  Count = 4


@unique
class vdkLicenseType(IntEnum):
  Render = 0
  Convert = 1
  Count = 2


class vdkAttributeSet(Structure):
  _fields_ = [("standardContent", c_uint64),
              ("count", c_uint32),
              ("allocated", c_uint32),
              ("pDescriptors", c_void_p)
              ]


class vdkPointCloudHeader(Structure):
  _fields_ = [("scaledRange", c_double),
              ("unitMeterScale", c_double),
              ("totalLODLayers", c_uint32),
              ("convertedResolution", c_double),
              ("storedMatrix", c_double * 16),
              ("attributes", vdkAttributeSet),
              ("baseOffset", c_double * 3),
              ("pivot", c_double * 3),
              ("boundingBoxCenter", c_double * 3),
              ("boundingBoxExtents", c_double * 3)
              ]


class vdkRenderInstance(Structure):
  _fields_ = [("pPointCloud", c_void_p),
              ("matrix", c_double * 16),
              ("modelFlags", c_uint64),
              ("pFilter", c_void_p),
              ("pVoxelShader", c_void_p),
              ("pVoxelUserData", c_void_p)
              ]
  position = [0, 0, 0]
  rotation = [0, 0, 0]
  scale = [1, 1, 1]

  def __init__(self, model):
    super().__init__()
    self.model = model
    self.position = [0, 0, 0]
    self.rotation = [0, 0, 0]
    self.scale = [1, 1, 1]

  @property
  def position(self):
    return self.__position

  @position.setter
  def position(self, position):
    self.matrix[12:15] = position
    self.__position = position

  @property
  def scale(self):
    return self.__scale

  @scale.setter
  def scale(self, scale):
    #preserve any rotation of the model by normalizing the
    #rotation/ scaling part of the matrix (this can probably be done more efficiently)
    try:
      self.matrix[0] /=self.__scale[0]
      self.matrix[5] /=self.__scale[5]
      self.matrix[10] /= self.__scale[10]
    except:
      self.matrix[0] = 1
      self.matrix[5] = 1
      self.matrix[10] = 1
    #support either scalar of vecor scaling:
    try:
      len(scale)
    except TypeError:
      scale = [scale, scale, scale]
    self.__scale = scale

    #update the matrix with the new scale:
    self.matrix[0] *= self.__scale[0]
    self.matrix[5] *= self.__scale[1]
    self.matrix[10] *= self.__scale[2]

  @property
  def rotation(self):
    return self.__rotation

  @rotation.setter
  def rotation(self, rotation):
    """INCOMPLETE"""
    self.__rotation = rotation
    sy = math.sin(rotation[2])
    cy = math.cos(rotation[2])
    sp = math.sin(rotation[0])
    cp = math.cos(rotation[0])
    sr = math.sin(rotation[1])
    cr = math.cos(rotation[1])
    #self.matrix[0:3] = [cy * cp * self.scale[0], cy * sp * sr - sy * cr, cy * sp * cr + sy * sr]
    #self.matrix[4:7] = [sy * cp, self.scale[1]*(sy * sp * sr + cy * cr), sy * sp * cr - cy * sr]
    #self.matrix[8:11] = [-sp, cp * sr, self.scale[2] * cp * cr]
    self.matrix[0:3] = [cy * cp * 4, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr]
    self.matrix[4:7] = [sy * cp, 4*(sy * sp * sr + cy * cr), sy * sp * cr - cy * sr]
    self.matrix[8:11] = [-sp, cp * sr, 4 * cp * cr]



class vdkContext:
  def __init__(self):
    self.vdkContext_Connect = getattr(vaultSDK, "vdkContext_Connect")
    self.vdkContext_Disconnect = getattr(vaultSDK, "vdkContext_Disconnect")
    self.vdkContext_RequestLicense = getattr(vaultSDK, "vdkContext_RequestLicense")
    self.vdkContext_CheckLicense = getattr(vaultSDK, "vdkContext_CheckLicense")
    self.vdkContext_TryResume = getattr(vaultSDK, "vdkContext_TryResume")
    self.context = c_void_p(0)
    self.url = ""
    self.username = ""
  def Connect(self, url=None, applicationName=None, username=None, password=None):
    if password is None:
      raise Exception("Password must be set")

    if url is not None:
      self.url = url

    if applicationName is not None:
      self.appName =applicationName

    if username is not None:
      self.username = username

    username = self.username.encode('utf8')
    applicationName = self.appName.encode('utf8')
    url = self.url.encode('utf8')
    password = password.encode('utf8')


    _HandleReturnValue(self.vdkContext_Connect(byref(self.context), url, applicationName,
                                               username, password))

  def Disconnect(self):
    _HandleReturnValue(self.vdkContext_Disconnect(byref(self.context)))

  def RequestLicense(self, licenseType):
    _HandleReturnValue(self.vdkContext_RequestLicense(self.context, licenseType))

  def CheckLicense(self, licenseType):
    _HandleReturnValue(self.vdkContext_CheckLicense(self.context, licenseType))

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

    _HandleReturnValue(self.vdkContext_TryResume(byref(self.context), url, applicationName, username, tryDongle))

class vdkRenderContext:
  def __init__(self):
    self.vdkRenderContext_Create = getattr(vaultSDK, "vdkRenderContext_Create")
    self.vdkRenderContext_Destroy = getattr(vaultSDK, "vdkRenderContext_Destroy")
    self.vdkRenderContext_Render = getattr(vaultSDK, "vdkRenderContext_Render")
    self.renderer = c_void_p(0)
    self.context = None

  def Create(self, context):
    self.context = context
    _HandleReturnValue(self.vdkRenderContext_Create(context.context, byref(self.renderer)))

  def Destroy(self):
    _HandleReturnValue(self.vdkRenderContext_Destroy(byref(self.renderer), True))
    print("Logged out of Vault")

  def Render(self, renderView, renderInstances):
    _HandleReturnValue(
      self.vdkRenderContext_Render(self.renderer, renderView.renderView, renderInstances, len(renderInstances),
                                   c_void_p(0)))

  def __del__(self):
    self.Destroy()


class vdkRenderView:
  def __init__(self, width=1280, height=720, clearColour=0, context=None, renderContext=None):
    self.vdkRenderView_Create = getattr(vaultSDK, "vdkRenderView_Create")
    self.vdkRenderView_Destroy = getattr(vaultSDK, "vdkRenderView_Destroy")
    self.vdkRenderView_SetTargets = getattr(vaultSDK, "vdkRenderView_SetTargets")
    self.vdkRenderView_SetMatrix = getattr(vaultSDK, "vdkRenderView_SetMatrix")
    self.renderView = c_void_p(0)

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
    self.SetMatrix(vdkRenderViewMatrix.Camera, self.cameraMatrix)

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

  def Create(self, context, vaultRenderer, width, height):
    self.context = context
    self.renderContext = vaultRenderer
    self.width = width
    self.height = height
    if self.renderView is not c_void_p(0):
      self.Destroy()
    _HandleReturnValue(
      self.vdkRenderView_Create(vaultRenderer.context.context, byref(self.renderView), vaultRenderer.renderer, width,
                                height))

  def Destroy(self):
    _HandleReturnValue(self.vdkRenderView_Destroy(byref(self.renderView)))

  def SetTargets(self, colorBuffer, clearColor, depthBuffer):
    _HandleReturnValue(
      self.vdkRenderView_SetTargets(self.renderView, byref(colorBuffer), clearColor, byref(depthBuffer)))

  def SetMatrix(self, matrixType, matrix):
    cMatrix = (c_double * 16)(*matrix)
    _HandleReturnValue(self.vdkRenderView_SetMatrix(self.renderView, matrixType, byref(cMatrix)))

  def __del__(self):
    self.Destroy()


class vdkPointCloud:
  def __init__(self):
    self.vdkPointCloud_Load = getattr(vaultSDK, "vdkPointCloud_Load")
    self.vdkPointCloud_Unload = getattr(vaultSDK, "vdkPointCloud_Unload")
    self.vdkPointCloud_GetMetadata = getattr(vaultSDK, "vdkPointCloud_GetMetadata")
    self.model = c_void_p(0)
    self.header = vdkPointCloudHeader()

  def Load(self, context, modelLocation):
    _HandleReturnValue(
      self.vdkPointCloud_Load(context.context, byref(self.model), modelLocation.encode('utf8'), byref(self.header)))

  def Unload(self):
    _HandleReturnValue(self.vdkPointCloud_Unload(byref(self.model)))

  def GetMetadata(self):
    pMetadata = c_char_p(0)
    _HandleReturnValue(self.vdkPointCloud_GetMetadata(self.model, byref(pMetadata)))
    return pMetadata.value.decode('utf8')

  def __del__(self):
    self.Unload()


class vdkConvertContext:
  def __init__(self):
    self.vdkConvert_CreateContext = getattr(vaultSDK, "vdkConvert_CreateContext")
    self.vdkConvert_DestroyContext = getattr(vaultSDK, "vdkConvert_DestroyContext")
    self.vdkConvert_SetOutputFilename = getattr(vaultSDK, "vdkConvert_SetOutputFilename")
    self.vdkConvert_AddItem = getattr(vaultSDK, "vdkConvert_AddItem")
    self.vdkConvert_DoConvert = getattr(vaultSDK, "vdkConvert_DoConvert")
    self.convertContext = c_void_p(0)

  def Create(self, context):
    _HandleReturnValue(self.vdkConvert_CreateContext(context.context, byref(self.convertContext)))

  def Destroy(self):
    _HandleReturnValue(self.vdkConvert_DestroyContext(byref(self.convertContext)))

  def Output(self, fileName):
    _HandleReturnValue(self.vdkConvert_SetOutputFilename(self.convertContext, fileName.encode('utf8')))

  def AddItem(self, modelName):
    _HandleReturnValue(self.vdkConvert_AddItem(self.convertContext, modelName.encode('utf8')))

  def DoConvert(self):
    _HandleReturnValue(self.vdkConvert_DoConvert(self.convertContext))


class vdkPointBufferI64(Structure):
  _fields_ = [
    ("pPositions", c_void_p),  # !< Flat array of XYZ positions in the format XYZXYZXYZXYZXYZXYZXYZ...
    ("attributes", vdkAttributeSet),  # !< Information on the attributes that are available in this point buffer
    ("positionStride", c_uint32),
    # !< Total bytes between the start of one position and the start of the next (currently always 24 (8 bytes per int64 * 3 int64))
    ("attributeStride", c_uint32),
    # !< Total number of bytes between the start of the attibutes of one point and the first byte of the next attribute
    ("pointCount", c_uint32),  # !< How many points are currently contained in this buffer
    ("pointsAllocated", c_uint32),  # !< Total number of points that can fit in this vdkPointBufferF64
    ("_reserved", c_uint32)  # !< Reserved for internal use
  ]


class vdkPointBufferF64(Structure):
  _fields_ = [
    ("pPositions", c_void_p),  # !< Flat array of XYZ positions in the format XYZXYZXYZXYZXYZXYZXYZ...
    ("attributes", vdkAttributeSet),  # !< Information on the attributes that are available in this point buffer
    ("positionStride", c_uint32),
    # !< Total bytes between the start of one position and the start of the next (currently always 24 (8 bytes per int64 * 3 int64))
    ("attributeStride", c_uint32),
    # !< Total number of bytes between the start of the attibutes of one point and the first byte of the next attribute
    ("pointCount", c_uint32),  # !< How many points are currently contained in this buffer
    ("pointsAllocated", c_uint32),  # !< Total number of points that can fit in this vdkPointBufferF64
    ("_reserved", c_uint32)  # !< Reserved for internal use
  ]


class vdkQueryFilter:
  def __init__(self):
    self.vdkQueryFilter_Create = getattr(vaultSDK, "vdkQueryFilter_Create")
    self.vdkQueryFilter_Destroy = getattr(vaultSDK, "vdkQueryFilter_Destroy")
    self.vdkQueryFilter_SetInverted = getattr(vaultSDK, "vdkQueryFilter_SetInverted")
    self.vdkQueryFilter_SetAsBox = getattr(vaultSDK, "vdkQueryFilter_SetAsBox")
    self.vdkQueryFilter_SetAsCylinder = getattr(vaultSDK, "vdkQueryFilter_SetAsCylinder")
    self.vdkQueryFilter_SetAsSphere = getattr(vaultSDK, "vdkQueryFilter_SetAsSphere")

    self.queryFilter = c_void_p(0)
    self.create()

  def create(self):
    _HandleReturnValue(self.vdkQueryFilter_Create(byref(self.queryFilter)))

  def __del__(self):
    _HandleReturnValue(self.vdkQueryFilter_Destroy(byref(self.queryFilter)))

  def SetInverted(self, inverted: bool):
    _HandleReturnValue(self.vdkQueryFilter_SetInverted(self.queryFilter, inverted))

  def SetAsBox(self, centrePoint, halfSize, yawPitchRoll):
    _HandleReturnValue(self.vdkQueryFilter_SetAsBox(self.queryFilter, centrePoint, halfSize, yawPitchRoll))

  def SetAsCylinder(self, centrePoint, radius, halfHeight, yawPitchRoll):
    _HandleReturnValue(
      self.vdkQueryFilter_SetAsCylinder(self.queryFilter, centrePoint, radius, halfHeight, yawPitchRoll))

  def SetAsSphere(self, centrePoint, radius):
    _HandleReturnValue(self.vdkQueryFilter_SetAsSphere(self.queryFilter, centrePoint, radius))

  class vdkQuery:
    def __init__(self, context: vdkContext):
      self.vdkQuery_Create = getattr(vaultSDK, "vdkQuery_Create")
      self.vdkQuery_ChangeFilter = getattr(vaultSDK, "vdkQuery_ChangeFilter")
      self.vdkQuery_ChangeModel = getattr(vaultSDK, "vdkQuery_ChangeModel")
      self.vdkQuery_ExecuteF64 = getattr(vaultSDK, "vdkQuery_ExecuteF64")
      self.vdkQuery_ExecuteI64 = getattr(vaultSDK, "vdkQuery_ExecuteI64")
      self.vdkQuery_Destroy = getattr(vaultSDK, "vdkQuery_Destroy")

      self.context = context
      self.query = c_void_p(0)
      self.Create()

    def Create(self, pPointCloud, pFilter):
      _HandleReturnValue(self.vdkQuery_Create(self.context.context, byref(self.query), pPointCloud, pFilter))

    def ChangeFilter(self, pFilter):
      _HandleReturnValue(self.vdkQuery_ChangeFilter(self.query, pFilter))

    def ChangeModel(self, pPointCloud):
      _HandleReturnValue(self.vdkQuery_ChangeModel(self.query, pPointCloud))

    def ExecuteF64(self, pPoints):
      retVal = self.vdkQuery_ExecuteF64(self.query, pPoints)
      if retVal == vdkError.NotFound:
        return True
      _HandleReturnValue(retVal)
      return False

    def ExecuteI64(self, pPoints):
      retVal = self.vdkQuery_ExecuteI64(self.query, pPoints)
      if retVal == vdkError.NotFound:
        return True
      _HandleReturnValue(retVal)
      return False

    def Destroy(self):
      _HandleReturnValue(self.vdkQuery_Destroy(byref(self.query)))
