import udSDK
from sys import argv
udSDK.LoadUdSDK("")
context = udSDK.udContext()
context.log_in(argv[1], argv[2])

model = udSDK.udPointCloud(path="C:/git/pclExperiments/data/manawatu/clusters/10_11_rgb_1_200/unclustered.uds", context=context)
f = udSDK.udQueryBoxFilter()
f.size = [model.header.boundingBoxExtents[i] * 2 * model.header.scaledRange for i in range(3)]
f.position = [model.header.baseOffset[i] + model.header.boundingBoxCenter[i] * model.header.scaledRange for i in range(3)]

#here if we set the filter to None, we will export the whole point cloud as a las
#model.export("./out.las", f)
query = udSDK.udQueryContext(context, model, f)
resultBuffer = udSDK.udPointBufferI64(maxPoints=1000, attributeSet=model.header.attributes)
h = model.get_header()
r = query.ExecuteI64(resultBuffer)
pass
