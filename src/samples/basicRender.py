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

#the camera matrix using left handed GL convention (i.e. last row is translation)
cameraMatrix = [1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, -2, 0, 1]


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
      renderInstance.scaleMode = "modelSpace"
      #renderInstance.matrix = udModel.header.storedMatrix

      renderInstances = [renderInstance]

      for x in range(20):
        udRenderer.Render(udRenderView, renderInstances)

      Image.frombuffer("RGBA", (width, height), udRenderView.colourBuffer, "raw", "RGBA", 0, 1).save(outFile)
      print("{0} written.".format(outFile))

    except udSDK.UdException as err:
      err.printout()
