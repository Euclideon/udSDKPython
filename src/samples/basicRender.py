from os.path import abspath
from sys import argv
from PIL import Image
import udSDK
import sampleLogin
import numpy as np

# Load the SDK and fetch symbols
SDKPath = abspath("./udSDK")
udSDK.LoadUdSDK(SDKPath)


modelFile = abspath("../../samplefiles/DirCube.uds")
outFile = abspath("./tmp.png")

width = 1280
height = 720

#the camera matrix using left handed GL convention (i.e. last row is translation)
cameraMatrix = np.array([
  [1, 0, 0, 0],
  [0, 1, 0, 0],
  [0, 0, 1, 0],
  [0, -2, 0, 1]
])


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
      udRenderTarget = udSDK.udRenderTarget(width, height, 0, udContext, udRenderer)

      # the udRenderBuffer object contains depth and (optionally) the colour buffer to be rendered to.
      # the contents can be accessed as buffer.depthBuffer and buffer.colourBuffer
      buffer = udSDK.udRenderBuffer(udRenderTarget)
      buffer.set_as_target()

      udModel = udSDK.udPointCloud(modelFile, udContext)
      # cameraMatrix can be any unpackable array like type of length of 16 or a 4x4 numpy ndarray
      udRenderTarget.cameraMatrix = cameraMatrix
      # udRenderView.projectionMatrix and udRenderView.viewMatrix matrices can be set similarly

      # the renderInstance contains a reference to the point cloud along with information about how we will render it
      # these include the model transformations, shaders, filters and opacity
      renderInstance = udSDK.udRenderInstance(udModel)

      # for demonstration purposes we will scale the model to fit in a 1x1x1 box centred on the origin:
      renderInstance.scaleMode = "modelSpace"
      #renderInstance.matrix = udModel.header.storedMatrix

      renderInstances = [renderInstance]

      # set the blocking streaming flag so that the model will refine more quickly (good for offline rendering):
      udRenderTarget.renderSettings.flags = udSDK.udRenderContextFlags.BlockingStreaming
      # run a couple of times so that the streamer will fully refine
      for i in range(2):
        udRenderer.render(udRenderTarget, renderInstances)
      # set preview to false to prevent popping up a preview window prior to saving:
      preview = True
      save = True
      if preview:
        try:
          buffer.plot_matplotlib()
          res = input("save to file (y/n)")
          if res == "y":
            save = True
          else:
            save = False
        except:
          pass

      if save:
        # this operation can also be performed as buffer.save_to_png(filename)
        Image.frombuffer("RGBA", (width, height), buffer.colourBuffer, "raw", "RGBA", 0, 1).save(outFile)
      print("{0} written.".format(outFile))

    except udSDK.UdException as err:
      err.printout()
