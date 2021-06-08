import udSDK
from sys import argv
udSDK.LoadUdSDK("")
context = udSDK.udContext()
context.log_in(argv[1], argv[2])

#model = udSDK.udPointCloud(path="C:/git/pclExperiments/data/manawatu/clusters/10_11_rgb_1_200/unclustered.uds", context=context)
model = udSDK.udPointCloud(path="C:/git/pclExperiments/data/manawatu/test/12_13_rgb.uds", context=context)
f = udSDK.udQueryBoxFilter()
f.size = [model.header.boundingBoxExtents[i] * model.header.scaledRange for i in range(3)]
f.position = [model.header.baseOffset[i] + model.header.boundingBoxCenter[i] * model.header.scaledRange for i in range(3)]

#we construct queries with the log in context, the
query = udSDK.udQueryContext(context, model, f)
#resultBuffer = udSDK.udPointBufferF64(maxPoints=7000000, attributeSet=model.header.attributes)

#r = query.execute(resultBuffer)
#resultBuffer2 = udSDK.udPointBufferF64(maxPoints=7000000, attributeSet=model.header.attributes)
#r = query.execute(resultBuffer2)

#this will attempt to load all points from the query at once:
#you will probably run out of memory if you do this:
query.load_all_points(bufferSize=8000000)
#currently we only take the first buffer as being all the points -this will not be true if buffersize > number of points in selection
resultsBuffer = query.resultBuffers[0]
#from here we can use the points however we like, for example by drawing them in matplotlib:
def visualizeInMatPlotLib(resultBuffer):
  import matplotlib.pyplot as plt
  fig = plt.figure()
  ax = fig.add_subplot(projection='3d')
  cs = [a.udRGB for a in resultBuffer.attributeArray[:resultBuffer.pStruct.contents.pointCount:1000]]
  ax.scatter(resultBuffer.positions[::1000,0], resultBuffer.positions[::1000,1], resultBuffer.positions[::1000,2], c=cs)
  plt.show()


import numpy as np
def PCA_transform(points: np.ndarray):
  var = np.corrcoef(points, rowvar=False)
  w, v = np.linalg.eig(var)
  pCentred = (points - points.mean(axis=0)).transpose()
  p = v.dot(pCentred)
  import matplotlib.pyplot as plt
  fig = plt.figure()
  ax = fig.add_subplot(projection='3d')
  ax.title = f"scale = {r}"
  plt.scatter(p[0, :], p[1, :], p[2, :], c='r')
  plt.scatter(pCentred[0, :], pCentred[1, :], pCentred[2, :], c='b')
  #plt.show()
  pass

  # this is the canupo descriptor at a single scale:
  # canupoDescriptor = np.array([l/(np.sum(w)) for l in w])
#visualizeInMatPlotLib(resultsBuffer)

samplePoint = udSDK.udQuerySphereFilter(position=[])
PCA_transform(resultsBuffer.positions[::1000,:])

#query.load_all_points()
#print(query.resultBuffers[0].positions[0:3])
#print(resultBuffer.positions[15])
#print(resultBuffer.positions[0:3])
pass
