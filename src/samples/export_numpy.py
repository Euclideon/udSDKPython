"""
This example show querying a subset of a uds file into a python environment and visualising the result in matplotlib
"""

import udSDK
import udSDKProject
import sampleLogin
from os.path import abspath

udSDK.LoadUdSDK("")
context = udSDK.udContext()
sampleLogin.log_in_sample(context)


def getUDSFilter(projectPath):
  """
  load the udSDK project at project path, scans the project for a filter
  and a uds, loads the first uds and creates a udSDK filter from the first
  one found in the project
  @returns
  the first uds and filter found at the base level of the project located at projectPath
  """
  proj = udSDKProject.udProject(context=context)
  proj.load_from_file(projectPath)
  rootnode = proj.rootNode
  queryFilter = None
  model = None
  for child in rootnode.children:
    if child.itemtypeStr == b'UDS' and model is None:
      model = child.to_ud_type()
    if child.itemtypeStr == b'QFilter' and queryFilter is None:
      queryFilter = child.to_ud_type()
    if queryFilter is not None and model is not None:
      break
  return model, queryFilter

#model = udSDK.udPointCloud(path="C:/git/pclExperiments/data/manawatu/clusters/10_11_rgb_1_200/unclustered.uds", context=context)
def manuallyLoadModelFilter():
  """
  Use this to load a uds and set the query filter to cover that whole uds
  """
  model = udSDK.udPointCloud(path="C:/git/pclExperiments/data/manawatu/test/12_13_rgb.uds", context=context)
  f = udSDK.udQueryBoxFilter()
  f.size = [model.header.boundingBoxExtents[i] * model.header.scaledRange for i in range(3)]
  f.position = [model.header.baseOffset[i] + model.header.boundingBoxCenter[i] * model.header.scaledRange for i in range(3)]
  return model, f

def udRGBA_to_tuple(colour):
  """converts a 32 bit colour value to a tuple of (r,g,b) floats between 0 and 1"""
  out = ((colour >> 16 & 0xFF)/255, (colour >> 8 & 0xFF)/255, (colour & 0xFF)/255)
  return out


#this will attempt to load all points from the query at once:
#you will probably run out of memory if you do this:
#query.load_all_points(bufferSize=8000000)

#currently we only take the first buffer as being all the points -this will not be true if buffersize > number of points in selection
#from here we can use the points however we like, for example by drawing them in matplotlib:
def visualizeInMatPlotLib(resultBuffer, everyNth=1000, attribute='udRGB'):
  """
  We use this function to test if the points are loaded correctly:
  we do this by plotting a subset of the loaded points (everyNth point) using matplotlib
  This is by no means the preferred method of viewing uds files, but is used to confirm that
  the query has exported the data correctly
  """
  import matplotlib.pyplot as plt
  fig = plt.figure()
  ax = fig.add_subplot(projection='3d')
  if attribute == "udRGB":
    cs = [*map(udRGBA_to_tuple, resultBuffer.attrAccessors.get('udRGB')[::everyNth])]
  else: #treat the attribute as a scalar field:
    cs = [*resultBuffer.attrAccessors.get(attribute)[::everyNth]]

  ax.scatter(resultBuffer.positions[::everyNth,0], resultBuffer.positions[::everyNth,1], resultBuffer.positions[::everyNth,2], c=cs)
  plt.show()
  pass

filterProjectPath = abspath("./src/samples/queryExample.udjson")
model, f = getUDSFilter(filterProjectPath)
#for some reason the direction of yaw is opposite to that rendered in udStream
#TODO: investigate this
f.yawPitchRoll = [-f.yawPitchRoll[0], *[f.yawPitchRoll[i+1] for i in range(2)]]
#we construct queries with the log in context, the
query = udSDK.udQueryContext(context, model, f)
resultBuffer = udSDK.udPointBufferF64(maxPoints=1000000, attributeSet=model.header.attributes)

#running query.execute will fill the buffer with points: if the number of points are contai
r = query.execute(resultBuffer)

#demonstrating access to the first 5 coordinates, these are read as a numpy array
first5 = resultBuffer.positions[:5,:]
print(f"first 5 points are at {first5}")
#this demonstrates access to the attributes stored in the pointcloud:
print(f"present attributes: {resultBuffer.pStruct.contents.attributes}")
udRGBIterator = resultBuffer.attrAccessors.get("udRGB")
if udRGBIterator is not None:
  print(f"accessing RGB values:")
  #indexing, iteration, slicing and negative indices are supported
  print(f"elements 0:5 = {[*udRGBIterator[0:5]]}")
  print("zeroing elements 4 and 5 of the buffer:")
  udRGBIterator[3:5] = [0, 0]
  print(f"elements 0:5 = {[*udRGBIterator[0:5]]}")
  print(f"elements -1:-2 = {[*udRGBIterator[-1:-2:-1]]}")

visualizeInMatPlotLib(resultBuffer,50)

#samplePoint = udSDK.udQuerySphereFilter(position=[])
#PCA_transform(resultsBuffer.positions[::1000,:])

#query.load_all_points()
#print(query.resultBuffers[0].positions[0:3])
#print(resultBuffer.positions[15])
#print(resultBuffer.positions[0:3])
pass
