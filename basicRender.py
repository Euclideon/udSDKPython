import udSDK

from ctypes import c_int, c_float
import os
import platform
from os.path import dirname, basename, abspath
from sys import exit
from PIL import Image
from sys import argv

# Load the SDK and fetch symbols
SDKPath = abspath("./udSDK")
udSDK.LoadUdSDK(SDKPath)


modelFile = abspath("../../samplefiles/DirCube.uds")
outFile = abspath("./tmp.png")

appName = "PythonSample"
serverPath = "https://udstream.euclideon.com"
userName = "Username"
userPass = "Password"

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

    if len(argv) >= 3:
        userName = argv[1]
        userPass = argv[2]

    if len(argv) >= 4:
        modelFile = abspath(argv[3])

    # Do the thing
    udContext = udSDK.udContext()
    udRenderer = udSDK.udRenderContext()
    udRenderView = udSDK.udRenderTarget()
    udModel = udSDK.udPointCloud()

    try:
      #initialize
      udContext.Connect(serverPath, appName, userName, userPass)
      udRenderer.Create(udContext)
      udRenderView.Create(udContext, udRenderer, width, height)
      udModel.Load(udContext, modelFile)
      udRenderView.SetTargets(colourBuffer, 0, depthBuffer)
      udRenderView.SetMatrix(udSDK.udRenderTargetMatrix.Camera, cameraMatrix)

      renderInstance = udSDK.udRenderInstance(udModel)
      renderInstance.matrix = udModel.header.storedMatrix

      renderInstances = (udSDK.udRenderInstance * 1)()
      renderInstances[0] = renderInstance

      for x in range(10):
        udRenderer.Render(udRenderView, renderInstances)

      Image.frombuffer("RGBA", (width, height), colourBuffer, "raw", "RGBA", 0, 1).save(outFile)
      print("{0} written to the build directory.\nPress enter to exit.\n".format(basename(outFile)))

      # Exit gracefully
      udModel.Unload()
      udRenderView.Destroy()
      udRenderer.Destroy()
      udContext.Disconnect()
    except udSDK.UdException as err:
      err.printout()
