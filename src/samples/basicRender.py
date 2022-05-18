from ctypes import c_int, c_float
from os.path import basename, abspath
from sys import argv

from PIL import Image

import udSDK
import sampleLogin

# Load the SDK and fetch symbols
SDKPath = abspath("./udSDK")
udSDK.LoadUdSDK(SDKPath)


#modelFile = abspath("../../samplefiles/DirCube.uds")
modelFile = abspath("C:/Users/BradenWockner/Downloads/Brisbane_2009_LGA_SW_515000_6955000_1K_Las.uds")
outFile = abspath("./tmp.png")

width = 1280
height = 720
#array of 32 bit ARGB pixels:
colourBuffer = (c_int * width * height)()
#float depths, z' is normalized between 0 and 1
depthBuffer = (c_float * width * height)()

#the camera matrix using left handed GL convention (i.e. last row is translation)
cameraMatrix = [1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, -5, 0, 1]

#OPTIONAL: definition of voxel shader
import ctypes

class userDataType(ctypes.Structure):
  _fields_ = [
    ("rangeMin", ctypes.c_double)
  ]

def voxel_shader_black(pPointCloud, pVoxelID:ctypes.POINTER(udSDK.udVoxelID), pUserData:ctypes.POINTER(userDataType)):
  """
  Demo voxel shader: this function is called for every voxel in the render
  """
  # this function is being passed the pointer to the underlying C point cloud so we must interact with it using unwrapped functions

  #udSDK.udPointCloud.udPointCloud_GetAttributeAddress(pPointCloud, pVoxelID, )
  #pUserData.contents.cameraPositionX
  return 0xFF000000

def voxel_shader_intensity(pPointCloud:ctypes.c_void_p, pVoxelID:ctypes.POINTER(udSDK.udVoxelID), pUserData:ctypes.POINTER(userDataType)):
  """
  Demonstration of using a voxel shader to render an attribute
  This takes the 16 bit intensity from the point cloud (if present) and returns that value in greyscale

  @warning 
  """
  pointcloud = udSDK.udPointCloud.from_pointer(ctypes.c_void_p(pPointCloud))
  minVal = 0
  maxVal = 10
  try:
    val = pointcloud.get_attribute(pVoxelID, "udIntensity")
    val = float(val.value) + 1
    val = int((val - minVal)/(maxVal-minVal) * 255)
    if val > 255:
      val = 255
    if val < 0:
      val = 0
    return 0xFF000000 | val << 16 | val << 8 | val
  except IndexError:
    # the uds has no intensity attribute, return black instead
    return 0xFF000000

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
      #initialize

      udModel.Load(udContext, modelFile)
      udRenderView.SetTargets(colourBuffer, 0, depthBuffer)
      udRenderView.SetMatrix(udSDK.udRenderTargetMatrix.Camera, cameraMatrix)

      renderInstance = udSDK.udRenderInstance(udModel)
      renderInstance.scaleMode = "minDim"
      #renderInstance.matrix = udModel.header.storedMatrix
      renderInstance.voxelShader = voxel_shader_intensity

      renderInstances = [renderInstance]

      for x in range(20):
        udRenderer.Render(udRenderView, renderInstances)

      Image.frombuffer("RGBA", (width, height), colourBuffer, "raw", "RGBA", 0, 1).save(outFile)
      print("{0} written to the build directory.\nPress enter to exit.\n".format(basename(outFile)))

    except udSDK.UdException as err:
      err.printout()
