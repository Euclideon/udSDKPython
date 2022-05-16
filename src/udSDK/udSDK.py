import ctypes
import json
import logging
import math
import os
import platform
# from ctypes import *
from enum import IntEnum, unique

import numpy as np

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
    print(f"trying {SDKPath}")
    udSDKlib = ctypes.CDLL(SDKPath)
  except OSError:
    print(
      "No local udSDK shared object/dll found in current working directory, trying path in UDSDK_HOME environment variable...")
    SDKPath = os.environ.get("UDSDK_HOME")
    if SDKPath == None:
      raise FileNotFoundError("Environment variable UDSDK_HOME not set, please refer to udSDK documentation")

    if platform.system() == 'Windows':
      SDKPath += "/lib/win_x64/udSDK"

    # TODO Add support for these paths:
    elif platform.system() == "Linux":
      SDKPath += "/lib/ubuntu18.04_GCC_x64/libudSDK"

    # elif platform.system() == "Darwin":
    #    print("Platform not supported"
    else:
      logger.error("Platform {} not supported by this sample".format(platform.system()))
      exit()
    logger.info("Using udSDK shared object located at {}".format(SDKPath))
    print("using " + SDKPath)
    udSDKlib = ctypes.CDLL(SDKPath)


udErrorVersion = 2111031245
@unique
class udError(IntEnum):
  Success = 0  # !< Indicates the operation was successful

  Failure = 1  # !< A catch-all value that is rarely used =  internally the below values are favored
  NothingToDo = 2  # !< The operation didn't specifically fail but it also didn't do anything
  InternalError = 3  # !< There was an internal error that could not be handled

  NotInitialized = 4  # !< The request can't be processed because an object hasn't been configured yet
  InvalidConfiguration = 5  # !< Something in the request is not correctly configured or has conflicting settings
  InvalidParameter = 6  # !< One or more parameters is not of the expected format
  OutstandingReferences = 7  # !< The requested operation failed because there are still references to this object

  MemoryAllocationFailure = 8  # !< udSDK wasn't able to allocate enough memory for the requested feature
  CountExceeded = 9  # !< An internal count was exceeded by the request =  generally going beyond the end of a buffer or internal limit

  NotFound = 10  # !< The requested item wasn't found or isn't currently available

  BufferTooSmall = 11  # !< Either the provided buffer or an internal one wasn't big enough to fufill the request
  FormatVariationNotSupported = 12  # !< The supplied item is an unsupported variant of a supported format

  ObjectTypeMismatch = 13  # !< There was a mismatch between what was expected and what was found

  CorruptData = 14  # !< The data/file was corrupt

  InputExhausted = 15  # !< The input buffer was exhausted so no more processing can occur
  OutputExhausted = 16  # !< The output buffer was exhausted so no more processing can occur

  CompressionError = 17  # !< There was an error in compression or decompression
  Unsupported = 18  # !< This functionality has not yet been implemented (usually some combination of inputs isn't compatible yet)

  Timeout = 19  # !< The requested operation timed out. Trying again later may be successful

  AlignmentRequired = 20  # !< Memory alignment was required for the operation

  DecryptionKeyRequired = 21  # !< A decryption key is required and wasn't provided
  DecryptionKeyMismatch = 22  # !< The provided decryption key wasn't the required one

  SignatureMismatch = 23  # !< The digital signature did not match the expected signature

  ObjectExpired = 24  # !< The supplied object has expired

  ParseError = 25  # !< A requested resource or input was unable to be parsed

  InternalCryptoError = 26  # !< There was a low level cryptography issue

  OutOfOrder = 27  # !< There were inputs that were provided out of order
  OutOfRange = 28  # !< The inputs were outside the expected range

  CalledMoreThanOnce = 29  # !< This function was already called

  ImageLoadFailure = 30  # !< An image was unable to be parsed. This is usually an indication of either a corrupt or unsupported image format

  StreamerNotInitialised = 31  # !<  The streamer needs to be initialised before this function can be called

  OpenFailure = 32  # !< The requested resource was unable to be opened
  CloseFailure = 33  # !< The resource was unable to be closed
  ReadFailure = 34  # !< A requested resource was unable to be read
  WriteFailure = 35  # !< A requested resource was unable to be written
  SocketError = 36  # !< There was an issue with a socket problem

  DatabaseError = 37  # !< A database error occurred
  ServerError = 38  # !< The server reported an error trying to complete the request
  AuthError = 39  # !< The provided credentials were declined (usually email or password issue)
  NotAllowed = 40  # !< The requested operation is not allowed (usually this is because the operation isn't allowed in the current state)
  InvalidLicense = 41  # !< The required license isn't available or has expired

  Pending = 42  # !< A requested operation is pending.
  Cancelled = 43  # !< The requested operation was cancelled (usually by the user)
  OutOfSync = 44  # !< There is an inconsistency between the internal udSDK state and something external. This is usually because of a time difference between the local machine and a remote server
  SessionExpired = 45  # !< The udServer has terminated your session

  ProxyError = 46  # !< There was some issue with the provided proxy information (either a proxy is in the way or the provided proxy info wasn't correct)
  ProxyAuthRequired = 47  # !< A proxy has requested authentication
  ExceededAllowedLimit = 48  # !< The requested operation failed because it would exceed the allowed limits (generally used for exceeding server limits like number of projects)

  RateLimited = 49  # !< This functionality is currently being rate limited or has exhausted a shared resource. Trying again later may be successful
  PremiumOnly = 50  # !< The requested operation failed because the current session is not for a premium user
  InProgress = 51 # The requested operation is currently in progress

  Count = 52  # !< Internally used to verify return values


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
  Rectangles = 0  # !< This is the default, renders the voxels expanded as screen space rectangles
  Cubes = 1  # !< Renders the voxels as cubes
  Points = 2  # !< Renders voxels as a single point (Note: does not accurately reflect the 'size' of voxels)

  Count = 3  # !< Total number of point modes. Used internally but can be used as an iterator max when displaying different point modes.


@unique
class udRenderContextFlags(IntEnum):
  none = 0,  # !< Render the points using the default configuration.

  PreserveBuffers = 1 << 0  # !< The colour and depth buffers won't be cleared before drawing and existing depth will be respected
  ComplexIntersections = 1 << 1  # !< This flag is required in some scenes where there is a very large amount of intersecting point clouds
  # !< It will internally batch rendering with the udRCF_PreserveBuffers flag after the first render.
  BlockingStreaming = 1 << 2  # !< This forces the streamer to load as much of the pointcloud as required to give an accurate representation in the current view. A small amount of further refinement may still occur.
  LogarithmicDepth = 1 << 3  # !< Calculate the depth as a logarithmic distribution.
  ManualStreamerUpdate = 1 << 4  # !< The streamer won't be updated internally but a render call without this flag or a manual streamer update will be required


@unique
class udRenderTargetMatrix(IntEnum):
  Camera = 0  # The local to world-space transform of the camera (View is implicitly set as the inverse)
  View = 1  # The view-space transform for the model (does not need to be set explicitly)
  Projection = 2  # The projection matrix (default is 60 degree LH)
  Viewport = 3  # Viewport scaling matrix (default width and height of viewport)
  Count = 4


class udVoxelID(ctypes.Structure):
  _fields_ = \
    [
      ("index", ctypes.c_uint64),  # internal index info
      ("pTrav", ctypes.c_uint64),  # internal traverse info
      ("pRenderInfo", ctypes.c_void_p),  # internal render info
    ]


class udRenderPicking(ctypes.Structure):
  _fields_ = \
    [
      # input variables:
      ("x", ctypes.c_uint),  # !< Mouse X position in udRenderTarget space
      ("y", ctypes.c_uint),  # !< Mouse Y position in udRenderTarget space
      # output variables
      ("hit", ctypes.c_uint32),
      ("isHighestLOD", ctypes.c_uint32),
      ("modelIndex", ctypes.c_uint),
      ("pointCentre", ctypes.c_double * 3),
      ("voxelID", ctypes.POINTER(udVoxelID))
    ]


class udRenderSettings(ctypes.Structure):
  _fields_ = [
    ("flags", ctypes.c_int),
    ("pPick", ctypes.POINTER(udRenderPicking)),
    ("pointMode", ctypes.c_int),
    ("pFilter", ctypes.c_void_p),
  ]

  def __init__(self):
    super(udRenderSettings, self).__init__()
    self.pick = udRenderPicking()
    self.pPick = ctypes.pointer(self.pick)

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


@unique
class udAttributeBlendType(IntEnum):
  udABT_Mean = 0  # !< This blend type merges nearby voxels together and finds the mean value for the attribute on those nodes
  udABT_FirstChild = 1  # !< This blend type selects the value from one of the nodes and uses that
  udABT_NoLOD = 2  # !< This blend type has no information in LODs and is only stored in the highest detail level

  udABT_Count = 3  # !< Total number of blend types. Used internally but can be used as an iterator max when checking attribute blend modes.


class udAttributeTypeInfo(IntEnum):
  udATI_Invalid = 0
  udATI_SizeMask = 0x000ff  # Lower 8 bits define the size in bytes - currently the actual maximum is 32
  udATI_SizeShift = 0
  udATI_ComponentCountMask = 0x0ff00  # Next 8 bits define the number of components component size is size/componentCount
  udATI_ComponentCountShift = 8
  udATI_Signed = 0x10000  # Set if type is signed (used in blend functions)
  udATI_Float = 0x20000  # Set if floating point type (signed should always be set)
  udATI_Color = 0x40000  # Set if type is de-quantized from a color
  udATI_Normal = 0x80000  # Set if type is encoded normal (32 bit = 16:15:1)

  # Some keys to define standard types
  udATI_uint8 = 1
  udATI_uint16 = 2
  udATI_uint32 = 4
  udATI_uint64 = 8
  udATI_int8 = 1 | udATI_Signed
  udATI_int16 = 2 | udATI_Signed
  udATI_int32 = 4 | udATI_Signed
  udATI_int64 = 8 | udATI_Signed
  udATI_float32 = 4 | udATI_Signed | udATI_Float
  udATI_float64 = 8 | udATI_Signed | udATI_Float
  udATI_color32 = 4 | udATI_Color
  udATI_normal32 = 4 | udATI_Normal
  udATI_vec3f32 = 12 | 0x300 | udATI_Signed | udATI_Float

  def to_ctype(self):
    return {
    self.udATI_uint8:ctypes.c_uint8,
    self.udATI_uint16:ctypes.c_uint16,
    self.udATI_uint32:ctypes.c_uint32,
    self.udATI_uint64:ctypes.c_uint64,
    self.udATI_int8:ctypes.c_int8,
    self.udATI_int16:ctypes.c_int16,
    self.udATI_int32:ctypes.c_int32,
    self.udATI_int64:ctypes.c_int64,
    self.udATI_float32:ctypes.c_float,
    self.udATI_float64:ctypes.c_double,
    self.udATI_color32:ctypes.c_uint32,
    self.udATI_normal32:ctypes.c_uint32,
    self.udATI_vec3f32:ctypes.c_float*3
    }.get(self.value)


class udAttributeDescriptor(ctypes.Structure):
  _fields_ = [
    ("typeInfo", ctypes.c_uint32),  # udAttributeTypeInfo
    ("blendType", ctypes.c_uint32),  # udAttributeBlendType
    ("name", ctypes.c_char * 64),
    ("prefix", ctypes.c_char * 16),
    ("suffix", ctypes.c_char * 16),
  ]

  def __repr__(self):
    return f"udAttributeDescriptor {self.name.decode('utf8')}({udAttributeTypeInfo(self.typeInfo)})"


class udAttributeSet(ctypes.Structure):
  _fields_ = [("standardContent", ctypes.c_uint32),
              ("count", ctypes.c_uint32),
              ("allocated", ctypes.c_uint32),
              ("pDescriptors", ctypes.POINTER(udAttributeDescriptor))
              ]
  _manuallyAllocated = False

  def get_offset(self, attributeName:str):
    ret = ctypes.c_uint32(0)
    _HandleReturnValue(udSDKlib.udAttributeSet_GetOffsetOfNamedAttribute(self, attributeName.encode('utf8'), ctypes.byref(ret)))
    return ret.value

  def __iter__(self):
    self.counter = 0
    return self

  def __next__(self):
    if self.counter == self.count:
      raise StopIteration
    else:
      ret = self.pDescriptors[self.counter]
      self.counter += 1
      return ret

  def __repr__(self):
    return f"udAttributeSet: {[self.pDescriptors[i] for i in range(self.count)]}"

  def __init__(self, standardContent: udStdAttributeContent = None, nAdditionalCustomAttributes=None):
    super(udAttributeSet, self).__init__()
    if standardContent is None and nAdditionalCustomAttributes is None:
      return
    _HandleReturnValue(udSDKlib.udAttributeSet_Create(ctypes.byref(self), ctypes.c_uint32(standardContent),
                                                      ctypes.c_uint32(nAdditionalCustomAttributes)))
    self._manuallyAllocated = True

  def __del__(self):
    if self._manuallyAllocated:
      _HandleReturnValue(udSDKlib.udAttributeSet_Destroy(ctypes.byref(self)))

  @property
  def names(self):
    return [self.pDescriptors[i].name.decode('utf8') for i in range(self.count)]


class udPointCloudHeader(ctypes.Structure):
  _fields_ = [("scaledRange", ctypes.c_double),
              ("unitMeterScale", ctypes.c_double),
              ("totalLODLayers", ctypes.c_uint32),
              ("convertedResolution", ctypes.c_double),
              ("storedMatrix", ctypes.c_double * 16),
              ("attributes", udAttributeSet),
              ("baseOffset", ctypes.c_double * 3),
              ("pivot", ctypes.c_double * 3),
              ("boundingBoxCenter", ctypes.c_double * 3),
              ("boundingBoxExtents", ctypes.c_double * 3)
              ]


class udRenderInstance(ctypes.Structure):
  """
Represents a renderInstance;
position, rotation and scale can be modified
directly to update the transformation matrix of the instance

This object is passed to udRenderContext.Render in order to
define the properties of the models to be rendered
"""
  _fields_ = [("pPointCloud", ctypes.c_void_p),
              ("matrix", ctypes.c_double * 16),
              ("pFilter", ctypes.c_void_p),
              ("pVoxelShader", ctypes.c_void_p),
              ("pVoxelUserData", ctypes.c_void_p),
              ("opacity", ctypes.c_double)
              ]
  position = [0, 0, 0]  # the position of the instance in world space
  rotation = [0, 0, 0]  # the rotation about the point pivot
  scale = [1, 1, 1]  # x, y and z scaling factors
  pivot = [0, 0, 0]  # point to rotate about

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
      raise AttributeError("Invalid scaling mode: " + mode)
    centrePos = [-self.model.header.pivot[0] * self.scale[0], -self.model.header.pivot[1] * self.scale[1],
                 -self.model.header.pivot[2] * self.scale[2]]
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
    # support either scalar of vecor scaling:
    try:
      assert (len(scale) == 3)
    except TypeError:
      scale = [scale, scale, scale]
    self.update_transformation(self.rotation, scale, self.skew)

  @property
  def rotation(self):
    return self.__rotation

  @rotation.setter
  def rotation(self, rotation):
    rotation = [rotation[0] % (2 * np.pi), rotation[1] % (2 * np.pi), rotation[2] % (2 * np.pi)]
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
    # self.skew=[0]*3
    self.scale = self.model.header.scaledRange
    # self.rotation = [self.model.header.storedMatrix[0]/self.scale[0],self.model.header.storedMatrix[5]/self.scale[1],self.model.header.storedMatrix[10]/self.scale[2]]
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
    trans[2] = [-sp, cp * sr, cp * cr, 0]

    trans = smat.dot(trans)
    trans[3] = [*self.position, 1]
    self.matrix = (ctypes.c_double * 16)(*(piv.dot(trans).dot(np.linalg.inv(piv))).flatten())


class udContext:
  def __init__(self):
    self._udContext_ConnectLegacy = getattr(udSDKlib, "udContext_ConnectLegacy")
    self._udContext_Disconnect = getattr(udSDKlib, "udContext_Disconnect")
    self._udContext_TryResume = getattr(udSDKlib, "udContext_TryResume")
    self._udContext_ConnectStart = udExceptionDecorator(udSDKlib.udContext_ConnectStart)
    self._udContext_ConnectComplete = udExceptionDecorator(udSDKlib.udContext_ConnectComplete)
    self._udContext_ConnectCancel = udExceptionDecorator(udSDKlib.udContext_ConnectCancel)
    self._udContext_ConnectWithKey = udExceptionDecorator(udSDKlib.udContext_ConnectWithKey)
    self.pContext = ctypes.c_void_p(0)
    self.isConnected = False
    self.url = ""
    self.username = ""

  def connect_legacy(self, url=None, applicationName=None, username=None, password=None):
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

    _HandleReturnValue(self._udContext_ConnectLegacy(ctypes.byref(self.pContext), url, applicationName,
                                               username, password))
    self.isConnected = True

  def Disconnect(self, endSession=True):
    if self.isConnected:
      _HandleReturnValue(self._udContext_Disconnect(ctypes.byref(self.pContext), ctypes.c_int32(endSession)))
      self.isConnected = False

  def log_in_legacy(self, userName: str, userPass: str, serverPath="https://udstream.euclideon.com",
                    appName="Python Sample") -> None:
    """
    Wraps the standard log in procedure which first attempts a try_resume
    """

    logger.info('Logging in to udStream server...')
    self.username = userName
    self.url = serverPath
    self.appName = appName

    try:
      logger.log(logging.INFO, "Attempting to resume session")
      self.try_resume(tryDongle=True)
    except UdException as e:
      logger.log(logging.INFO,
                 "Resume failed: ({})\n Attempting to connect new session...".format(str(e.args[0])))
      self.connect_legacy(password=userPass)

  def log_in_interactive(self, username=None, serverPath="https://udcloud.euclideon.com", appName="Python Sample", appVersion='0.1'):
    "log in method for udCloud based servers"
    try:
      self.try_resume(serverPath, appName, username)
    except UdException as e:
      pPartialConnection = ctypes.c_void_p(0)
      pApprovePath = ctypes.c_char_p(0)
      pApproveCode = ctypes.c_char_p(0)
      self._udContext_ConnectStart(ctypes.byref(pPartialConnection), serverPath.encode('utf8'), appName.encode('utf8'), appVersion.encode('utf8'), ctypes.byref(pApprovePath), ctypes.byref(pApproveCode))
      try:
        import webbrowser
        webbrowser.open(pApprovePath.value.decode('utf8'))
      except:
        print(f"Visit {pApprovePath.value.decode('utf8')} in your browser to complete connection")
      print(f"Alternatively visit {serverPath}/link and enter {pApproveCode.value.decode('utf8')} in your browser to complete connection")
      input("press any key to continue...")
      self._udContext_ConnectComplete(ctypes.byref(self.pContext), ctypes.byref(pPartialConnection))
      self.isConnected = True

  def connect_with_key(self, key : str, serverPath="https://udcloud.euclideon.com", appName="Python Sample", appVersion='0.1'):
    self._udContext_ConnectWithKey(ctypes.byref(self.pContext), serverPath.encode('utf8'), appName.encode('utf8'),
                                   appVersion.encode('utf8'), key.encode('utf8'))

  def __del__(self):
    pass #causes outstanging reference error if we try to do this
    #self.Disconnect(endSession=False)

  def try_resume(self, url=None, applicationName=None, username=None, tryDongle=False):
    if url is not None:
      self.url = url
    url = self.url.encode('utf8')
    if applicationName is not None:
      self.appName = applicationName
    applicationName = self.appName.encode('utf8')

    if username is not None:
      self.username = username
    username = self.username.encode('utf8')

    _HandleReturnValue(self._udContext_TryResume(ctypes.byref(self.pContext), url, applicationName, username, tryDongle))
    self.isConnected = True


class udRenderContext:
  def __init__(self, context: udContext = None):
    """Create object without attached context"""
    self.udRenderContext_Create = getattr(udSDKlib, "udRenderContext_Create")
    self.udRenderContext_Destroy = getattr(udSDKlib, "udRenderContext_Destroy")
    self.udRenderContext_Render = getattr(udSDKlib, "udRenderContext_Render")
    self.renderer = ctypes.c_void_p(0)
    self.context = context

    if context is not None:
      self.Create(context)

  def Create(self, context):
    self.context = context
    _HandleReturnValue(self.udRenderContext_Create(context.pContext, ctypes.byref(self.renderer)))

  def Destroy(self):
    _HandleReturnValue(self.udRenderContext_Destroy(ctypes.byref(self.renderer), True))
    # print("Logged out of udSDK")

  def Render(self, renderView, renderInstances, renderSettings=ctypes.c_void_p(0)):
    if isinstance(renderInstances, list):
      renderInstances = (udRenderInstance * len(renderInstances))(*renderInstances)
    _HandleReturnValue(
      self.udRenderContext_Render(self.renderer, renderView.pRenderView, renderInstances, len(renderInstances),
                                  renderSettings))

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
    self._udRenderTarget_SetLogarithmicDepthPlanes = udExceptionDecorator(udSDKlib.udRenderTarget_SetLogarithmicDepthPlanes)
    self.pRenderView = ctypes.c_void_p(0)
    self.renderSettings = udRenderSettings()
    self.filter = None

    self._width = width
    self._height = height
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
      self.renderSettings.pFilter = ctypes.c_void_p(0)

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
      width = self._width
    if height is None:
      height = self._height

    self.colourBuffer = (ctypes.c_int32 * (width * height))()
    self.depthBuffer = (ctypes.c_float * (width * height))()
    if self.context is not None and self.renderContext is not None:
      self.Create(self.context, self.renderContext, width, height)
      self.SetTargets(self.colourBuffer, self.clearColour, self.depthBuffer)
    else:
      raise Exception("Context and renderer must be created before calling set_size")

  @property
  def height(self):
    return self._height
  @height.setter
  def height(self, newValue):
    self.set_size(height=int(newValue))

  @property
  def width(self):
    return self._width
  @width.setter
  def width(self, newValue):
    self.set_size(width=int(newValue))

  def rgb_colour_buffer(self):
    """returns the colour buffer as a """
    out = []
    for colour in self.colourBuffer:
      out.append((colour >> 16 & 0xFF, colour >> 8 & 0xFF, colour & 0xFF))
    return out

  def plot_view(self):
    """plots the current view as an rgb image in matpotlib"""
    import matplotlib.pyplot as plt
    im = np.array(self.rgb_colour_buffer()).reshape([self.height, self.width, 3])
    plt.imshow(im)
    plt.show()

  def Create(self, context, udRenderer, width, height):
    self.context = context
    self.renderContext = udRenderer
    self._width = width
    self._height = height
    if self.pRenderView is not ctypes.c_void_p(0):
      self.Destroy()
    _HandleReturnValue(
      self.udRenderTarget_Create(udRenderer.context.pContext, ctypes.byref(self.pRenderView), udRenderer.renderer, width,
                                 height))

  def Destroy(self):
    _HandleReturnValue(self.udRenderTarget_Destroy(ctypes.byref(self.pRenderView)))

  def SetTargets(self, colorBuffer, clearColor, depthBuffer):
    _HandleReturnValue(
      self.udRenderTarget_SetTargets(self.pRenderView, ctypes.byref(colorBuffer), clearColor, ctypes.byref(depthBuffer)))

  def SetMatrix(self, matrixType: udRenderTargetMatrix, matrix):
    cMatrix = (ctypes.c_double * 16)(*matrix)
    _HandleReturnValue(self.udRenderTarget_SetMatrix(self.pRenderView, matrixType, ctypes.byref(cMatrix)))

  def GetMatrix(self, matrixType: udRenderTargetMatrix):
    cMatrix = (ctypes.c_double * 16)()
    _HandleReturnValue(self.udRenderTarget_GetMatrix(self.pRenderView, matrixType, ctypes.byref(cMatrix)))
    return [*cMatrix]

  def set_logarithmic_depth_planes(self, nearPlane, farPlane):
    self._udRenderTarget_SetLogarithmicDepthPlanes(self.pRenderView, ctypes.c_double(nearPlane), ctypes.c_double(farPlane))

  def __del__(self):
    self.Destroy()




class udPointCloud:
  def __init__(self, path: str = None, context: udContext = None):
    self.udPointCloud_Load = getattr(udSDKlib, "udPointCloud_Load")
    self.udPointCloud_Unload = getattr(udSDKlib, "udPointCloud_Unload")
    self.udPointCloud_GetMetadata = getattr(udSDKlib, "udPointCloud_GetMetadata")
    self.udPointCloud_GetHeader = getattr(udSDKlib, "udPointCloud_GetHeader")
    self.udPointCloud_Export = getattr(udSDKlib, "udPointCloud_Export")
    self.udPointCloud_GetNodeColour = getattr(udSDKlib, "udPointCloud_GetNodeColour")
    self.udPointCloud_GetNodeColour64 = getattr(udSDKlib, "udPointCloud_GetNodeColour64")
    self.udPointCloud_GetAttributeAddress = getattr(udSDKlib, "udPointCloud_GetAttributeAddress")
    self.udPointCloud_GetStreamingStatus = getattr(udSDKlib, "udPointCloud_GetStreamingStatus")
    self.pPointCloud = ctypes.c_void_p(0)
    self.header = udPointCloudHeader()

    if context is not None and path is not None:
      self.Load(context, path)
      self.uri = path

  def Load(self, context: udContext, modelLocation: str):
    self.path = modelLocation
    _HandleReturnValue(
      self.udPointCloud_Load(context.pContext, ctypes.byref(self.pPointCloud), modelLocation.encode('utf8'),
                             ctypes.byref(self.header)))

  def get_header(self):
    ret = udPointCloudHeader()
    _HandleReturnValue(self.udPointCloud_GetHeader(self.pPointCloud, ctypes.byref(ret)))
    return ret

  def Unload(self):
    if self.pPointCloud.value is not None:
      _HandleReturnValue(self.udPointCloud_Unload(ctypes.byref(self.pPointCloud)))

  def GetMetadata(self):
    pMetadata = ctypes.c_char_p(0)
    _HandleReturnValue(self.udPointCloud_GetMetadata(self.pPointCloud, ctypes.byref(pMetadata)))
    return json.loads(pMetadata.value.decode('utf8'))

  def export(self, outPath: str, filter: "udQueryFilter" = None):
    if filter is None:
      pFilter = ctypes.c_void_p(0)
    else:
      pFilter = filter.pGeometry
    _HandleReturnValue(self.udPointCloud_Export(self.pPointCloud, outPath.encode('utf8'), pFilter))

  def __eq__(self, other):
    if hasattr(other, "path") and hasattr(self, "path"):
      return other.path == self.path
    else:
      return False

  def __del__(self):
    self.Unload()

class udPointBuffer():
  """
  Structure used for reading and writing points to UDS.
  """
  def __init__(self):
    def f():
      arr = np.ctypeslib.as_array(self.pStruct.contents.pAttributes, )


  @property
  def positions(self):
    ret = np.ctypeslib.as_array(self.pStruct.contents.pPositions, (self.pStruct.contents.pointCount, 3))
    ret.dtype = self.dtype
    return ret

  def __len__(self):
    return self.pStruct.contents.pointCount

  def add_point(self):
    """add an unitialised point to the end of the buffer"""
    if(len(self) >= self.pStruct.contents.pointsAllocated):
      raise OverflowError("Buffer is full")
    self.pStruct.contents.pointCount += 1


class udPointBufferI64(udPointBuffer):
  class _udPointBufferI64(ctypes.Structure):
    _fields_ = [
      ("pPositions", ctypes.POINTER(ctypes.c_int64)),  # !< Flat array of XYZ positions in the format XYZXYZXYZXYZXYZXYZXYZ...
      ("pAttributes", ctypes.POINTER(ctypes.c_byte)),
      ("attributes", udAttributeSet),  # !< Information on the attributes that are available in this point buffer
      ("positionStride", ctypes.c_uint32),
      # !< Total bytes between the start of one position and the start of the next (currently always 24 (8 bytes per int64 * 3 int64))
      ("attributeStride", ctypes.c_uint32),
      # !< Total number of bytes between the start of the attibutes of one point and the first byte of the next attribute
      ("pointCount", ctypes.c_uint32),  # !< How many points are currently contained in this buffer
      ("pointsAllocated", ctypes.c_uint32),  # !< Total number of points that can fit in this udPointBufferF64
      ("_reserved", ctypes.c_uint32)  # !< Reserved for internal use
    ]
  pStruct = ctypes.POINTER(_udPointBufferI64)()#pointer(_udPointBufferI64)
  dtype = "i8"


  def __init__(self, maxPoints, attributeSet=None):
    raise NotImplementedError
    self.udPointBufferI64_Create = udExceptionDecorator(udSDKlib.udPointBufferI64_Create)
    self.udPointBufferI64_Destroy = udExceptionDecorator(udSDKlib.udPointBufferI64_Destroy)
    self.udPointBufferI64_Create(byref(self.pStruct), maxPoints, attributeSet)
    super(udPointBufferI64, self).__init__()

  def __del__(self):
    if self.pStruct is not None and self.isReference:
      self.udPointBufferI64_Destroy(ctypes.byref(self.pStruct))

class udAttributeAccessor():
  """
  class representing the array of a particular attribute stored in a udPointBuffer
  """
  def __init__(self, buffer:udPointBuffer, descriptorIndex, start=None, stop=None, step=1):
    self.buffer = buffer
    self.attributeStride = buffer.pStruct.contents.attributeStride
    self.descriptor = buffer.pStruct.contents.attributes.pDescriptors[descriptorIndex]
    self.attributeOffset = buffer.pStruct.contents.attributes.get_offset(self.descriptor.name.decode('utf8'))
    self.typeInfo = udAttributeTypeInfo(self.descriptor.typeInfo)

    self._start = start
    self._stop = stop
    if step is None:
      step = 1

    self.step = step
    self.descriptorIndex = descriptorIndex

  @property
  def stop(self):
    if self._stop is None:
      return self.buffer.pStruct.contents.pointCount - 1
    if self._stop >= 0:
      ret = self._stop - 1
    else:
      ret = self._stop + self.buffer.pStruct.contents.pointCount - 1
    if ret > self.buffer.pStruct.contents.pointCount:
      raise IndexError("iteration stop out of bounds")
    return ret

  @property
  def start(self):
    if self._start is None:
      return 0
    if self._start >= 0:
      ret = self._start
    else:
      ret = self._start + self.buffer.pStruct.contents.pointCount
    if ret > self.buffer.pStruct.contents.pointCount:
      raise IndexError("iteration start out of bounds")
    return ret

  def __iter__(self):
    self._counter = 0
    return self

  def __next__(self):
    if self._counter >= len(self):
      raise StopIteration
    else:
      ret = self[self._counter]
      self._counter += 1
      return ret

  def _getPtr(self, item):
    """
    returns the pointer to the object at for integer item numbers or another view into the array
    """
    if type(item) == slice:
      if item.step is not None:
        step = item.step
      else:
        step = 1
      return udAttributeAccessor(self.buffer, self.descriptorIndex, item.start, item.stop, step)
    elif type(item) == int:
      if(item > len(self)):
        raise IndexError
      start = item * self.step + self.start
    else:
      raise TypeError
    if start < 0:
      start = self.buffer.pStruct.contents.pointCount + start
    if start >= self.buffer.pStruct.contents.pointCount or start < 0:
      raise IndexError
    offset = start * self.attributeStride + self.attributeOffset
    return ctypes.cast(ctypes.c_void_p(self.buffer.pStruct.contents.pAttributes + offset), ctypes.POINTER(self.typeInfo.to_ctype())).contents

  def __getitem__(self, item):
    ret = self._getPtr(item)
    if type(ret) == udAttributeAccessor:
      return ret
    else:
      return ret.value

  def __setitem__(self, key, value):
    item = self._getPtr(key)
    if type(item) == udAttributeAccessor:
      if len(item) != len(value):
        raise Exception("slice to be replaced must be the same length as value")
      for i in range(len(item)):
        item[i] = value[i]
    else:
      item.value = value

  def __len__(self):
    return (self.stop-self.start)//self.step + 1


class udPointBufferF64(udPointBuffer):
  class _udPointBufferF64(ctypes.Structure):
    _fields_ = [
      ("pPositions", ctypes.POINTER(ctypes.c_double)),  # !< Flat array of XYZ positions in the format XYZXYZXYZXYZXYZXYZXYZ...
      ("pAttributes", ctypes.c_void_p),
      ("attributes", udAttributeSet),  # !< Information on the attributes that are available in this point buffer
      ("positionStride", ctypes.c_uint32),
      # !< Total bytes between the start of one position and the start of the next (currently always 24 (8 bytes per int64 * 3 int64))
      ("attributeStride", ctypes.c_uint32),
      # !< Total number of bytes between the start of the attibutes of one point and the first byte of the next attribute
      ("pointCount", ctypes.c_uint32),  # !< How many points are currently contained in this buffer
      ("pointsAllocated", ctypes.c_uint32),  # !< Total number of points that can fit in this udPointBufferF64
      ("_reserved", ctypes.c_uint32)  # !< Reserved for internal use
    ]
  dtype = "f8"

  def __init__(self, maxPoints=0, attributeSet=None, pStruct=None):
    self.udPointBufferF64_Create = udExceptionDecorator(udSDKlib.udPointBufferF64_Create)
    self.udPointBufferF64_Destroy = udExceptionDecorator(udSDKlib.udPointBufferF64_Destroy)
    if pStruct is None:
      self.pStruct = ctypes.POINTER(self._udPointBufferF64)()#pointer(_udPointBufferF64)
      self.udPointBufferF64_Create(ctypes.byref(self.pStruct), maxPoints, attributeSet)
      self.isReference = False
    else:
      self.pStruct = pStruct
      attributeSet = pStruct.contents.attributes
      self.isReference = True

    self.attrAccessors = {}
    for i, attr in enumerate(attributeSet):
      self.attrAccessors[attr.name.decode('utf8')] = udAttributeAccessor(self, i)
    super(udPointBufferF64, self).__init__()

  def __del__(self):
    if self.pStruct and not self.isReference:
      self.udPointBufferF64_Destroy(ctypes.byref(self.pStruct))


class udQueryContext:
  def __init__(self, context: udContext, pointcloud: udPointCloud, filter):
    self.udQueryContext_Create = getattr(udSDKlib, "udQueryContext_Create")
    self.udQueryContext_ChangeFilter = getattr(udSDKlib, "udQueryContext_ChangeFilter")
    self.udQueryContext_ChangePointCloud = getattr(udSDKlib, "udQueryContext_ChangePointCloud")
    self.udQueryContext_ExecuteF64 = getattr(udSDKlib, "udQueryContext_ExecuteF64")
    self.udQueryContext_ExecuteI64 = getattr(udSDKlib, "udQueryContext_ExecuteI64")
    self.udQueryContext_Destroy = getattr(udSDKlib, "udQueryContext_Destroy")

    self.context = context
    self.pQueryContext = ctypes.c_void_p(0)
    self.pointcloud = pointcloud
    self.filter = filter
    self.resultBuffers = []
    self.Create()

  def Create(self):
    _HandleReturnValue(
      self.udQueryContext_Create(self.context.pContext, ctypes.byref(self.pQueryContext), self.pointcloud.pPointCloud,
                                 self.filter.pGeometry))
  def ChangeFilter(self, filter):
    self.filter = filter
    _HandleReturnValue(self.udQueryContext_ChangeFilter(self.pQueryContext, filter.pGeometry))

  def ChangePointCloud(self, pointcloud: udPointCloud):
    self.pointcloud = pointcloud
    _HandleReturnValue(self.udQueryContext_ChangePointCloud(self.pQueryContext, pointcloud.pPointCloud))

  def execute(self, points: udPointBufferF64):
    retVal = self.udQueryContext_ExecuteF64(self.pQueryContext, points.pStruct)
    if retVal == udError.NotFound:
      return False
    _HandleReturnValue(retVal)
    return True

  def Destroy(self):
    _HandleReturnValue(self.udQueryContext_Destroy(ctypes.byref(self.pQueryContext)))

  def load_all_points(self, bufferSize=100000):
    """
    This loads all points from the UDS into the resultsBuffers array
    """
    #raise NotImplementedError("this function does not currently work correctly")
    res = True
    while res:
      buff = udPointBufferF64(bufferSize, attributeSet=self.pointcloud.header.attributes)
      res = self.execute(buff)
      if res:
        pass
        self.resultBuffers.append(buff)
        pass
    return self.resultBuffers

class udStreamer(ctypes.Structure):
  _fields_ = [
    ("active", ctypes.c_int32),
    ("memoryInUse", ctypes.c_int64),
    ("modelsActive", ctypes.c_int),
    ("starvedTimeMsSinceLastUpdate", ctypes.c_int),
  ]

  def __init__(self):
    super(udStreamer, self).__init__()
    self.udStreamer_Update = getattr(udSDKlib, "udStreamer_Update")

  def update(self):
    _HandleReturnValue(self.udStreamer_Update(ctypes.byref(self)))