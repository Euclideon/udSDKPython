from ctypes import c_int, c_float
from os.path import basename, abspath
from sys import argv

from PIL import Image

import udSDK
import sampleLogin

# Load the SDK and fetch symbols
SDKPath = abspath("./udSDK")
udSDK.LoadUdSDK(SDKPath)


modelFile = abspath("../../samplefiles/DirCube.uds")
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

if __name__ == "__main__":

    # allow the passing of the model as the first argument:
    if len(argv) >= 2:
        modelFile = abspath(argv[1])

    # Do the thing
    udContext = udSDK.udContext()
    udRenderer = udSDK.udRenderContext(udContext)
    udRenderView = udSDK.udRenderTarget(udRenderer, width, height)
    udModel = udSDK.udPointCloud()

    try:
      #initialize

      sampleLogin.log_in_sample(udContext)
      udModel.load(udContext, modelFile)
      udRenderView.SetTargets(colourBuffer, 0, depthBuffer)
      udRenderView.SetMatrix(udSDK.udRenderTargetMatrix.Camera, cameraMatrix)

      renderInstance = udSDK.udRenderInstance(udModel)
      renderInstance.matrix = udModel.header.storedMatrix

      renderInstances = (udSDK.udRenderInstance * 1)()
      renderInstances[0] = renderInstance

      for x in range(10):
        udRenderer.render(udRenderView, renderInstances)

      Image.frombuffer("RGBA", (width, height), colourBuffer, "raw", "RGBA", 0, 1).save(outFile)
      print("{0} written to the build directory.\nPress enter to exit.\n".format(basename(outFile)))
    except udSDK.UdException as err:
      err.printout()
