from os.path import abspath
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

#the camera matrix using left handed GL convention (i.e. last row is translation)
cameraMatrix = [1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, -2, 0, 1]


if __name__ == "__main__":
    # allow the passing of the model as the first argument:
    if len(argv) >= 2:
        modelFile = abspath(argv[1])

    try:
      # log in to udCloud:
      udContext = udSDK.udContext()
      sampleLogin.log_in_sample(udContext)

      # create the render context
      udRenderer = udSDK.udRenderContext(udContext)

      # define our target to render to
      udRenderView = udSDK.udRenderTarget(width, height, 0, udContext, udRenderer)
      udModel = udSDK.udPointCloud(modelFile, udContext)
      udRenderView.SetMatrix(udSDK.udRenderTargetMatrix.Camera, cameraMatrix)

      # the renderInstance contatins a reference to the point cloud along with information about how we will render it
      # these include the model transformations, shaders, filters and opacity
      renderInstance = udSDK.udRenderInstance(udModel)

      # for demonstration purposes we will scale the model to fit in a 1x1x1 box centred on the origin:
      renderInstance.scaleMode = "modelSpace"
      #renderInstance.matrix = udModel.header.storedMatrix

      renderInstances = [renderInstance]

      # set the blocking streaming flag so that the model will refine more quickly (good for offline rendering):
      udRenderView.renderSettings.flags = udSDK.udRenderContextFlags.BlockingStreaming
      # run a couple of times so that the streamer will fully refine
      for i in range(2):
        udRenderer.Render(udRenderView, renderInstances)

      # our image is stored as an array in udRenderView.colourBuffer we can now write it to file:
      Image.frombuffer("RGBA", (width, height), udRenderView.colourBuffer, "raw", "RGBA", 0, 1).save(outFile)
      print("{0} written.".format(outFile))

    except udSDK.UdException as err:
      err.printout()
