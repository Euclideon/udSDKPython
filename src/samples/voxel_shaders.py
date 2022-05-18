"""
Demonstration of rendering using voxel shader callbacks
"""
import ctypes
import udSDK
from os.path import basename, abspath
from sys import argv
from PIL import Image
import sampleLogin

# Load the SDK and fetch symbols
SDKPath = abspath("./udSDK")
udSDK.LoadUdSDK(SDKPath)


modelFile = abspath("../../samplefiles/DirCube.uds")
outFile = abspath("./tmp.png")

width = 1280
height = 720

#the camera matrix using left handed GL convention (i.e. last row is translation)
cameraMatrix = [1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, -5, 0, 1]

class userDataType(ctypes.Structure):
  _fields_ = [
    ("rangeMin", ctypes.c_double),
    ("rangeMax", ctypes.c_double)
  ]

def voxel_shader_black(pPointCloud, pVoxelID:ctypes.POINTER(udSDK.udVoxelID), pUserData:ctypes.POINTER(userDataType)):
  """
  Demo voxel shader: this function is called for every voxel in the render
  """
  return 0xFF000000

def voxel_shader_intensity(pPointCloud:ctypes.c_void_p, pVoxelID:ctypes.POINTER(udSDK.udVoxelID), pUserData:ctypes.POINTER(userDataType)):
  """
  Demonstration of using a voxel shader to render an attribute
  This takes the 16 bit intensity from the point cloud (if present) and returns that value in greyscale

  @note This callback is computationally expensive due to language constraints and may not be appropriate for real time rendering
  """
  pointcloud = udSDK.udPointCloud.from_pointer(ctypes.c_void_p(pPointCloud))
  userData = ctypes.cast(ctypes.c_void_p(pUserData), ctypes.POINTER(userDataType)).contents
  minVal = userData.rangeMin
  maxVal = userData.rangeMax
  try:
    val = pointcloud.get_attribute(pVoxelID, "udIntensity")
  except IndexError:
    # the pointcloud has no intensity attribute, return black instead
    return 0xFF000000
  val = float(val)
  val = int((val - minVal)/(maxVal-minVal) * 255)
  if val > 255:
    val = 255
  if val < 0:
    val = 0
  # val could be mapped to another colour scale here if desired - this is linear greyscale
  return 0xFF000000 | val << 16 | val << 8 | val


if __name__ == "__main__":

  # allow the passing of the model as the first argument:
  if len(argv) >= 2:
    modelFile = abspath(argv[1])

  # Do the thing
  udContext = udSDK.udContext()
  sampleLogin.log_in_sample(udContext)
  udRenderer = udSDK.udRenderContext(udContext)
  udRenderView = udSDK.udRenderTarget(width, height, 0, udContext, udRenderer)
  udModel = udSDK.udPointCloud()

  try:

    udModel.Load(udContext, modelFile)
    udRenderView.SetMatrix(udSDK.udRenderTargetMatrix.Camera, cameraMatrix)

    renderInstance = udSDK.udRenderInstance(udModel)
    renderInstance.scaleMode = "minDim"

    # check that the pointcloud has the necessary attribute:
    if udModel.header.attributes.names.count("udIntensity"):
      userData = userDataType()
      userData.rangeMin = 0
      userData.rangeMax = 2**8 - 1
      renderInstance.voxelShader = voxel_shader_intensity
      renderInstance.voxelShaderData = userData
    else:
      print("model has no intensity channel: rendering in black")
      renderInstance.voxelShader = voxel_shader_black

    renderInstances = [renderInstance]

    for x in range(20):
      udRenderer.Render(udRenderView, renderInstances)

    Image.frombuffer("RGBA", (width, height), udRenderView.colourBuffer, "raw", "RGBA", 0, 1).save(outFile)
    print("{0} written.".format(outFile))

  except udSDK.UdException as err:
    err.printout()
