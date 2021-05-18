import udSDK
from sys import argv
udSDK.LoadUdSDK("")
context = udSDK.udContext()
context.log_in(argv[1], argv[2])

model = udSDK.udPointCloud(path="C:/git/pclExperiments/data/manawatu/clusters/10_11_rgb_1_200/unclustered.uds", context=context)
f = udSDK.udQueryBoxFilter()

#this is a filter that is the size of the bounding box of the UDS.
#Exporting or querying using this will give all points in the dataset
f.size = [model.header.boundingBoxExtents[i] * 2 * model.header.scaledRange for i in range(3)]
f.position = [model.header.baseOffset[i] + model.header.boundingBoxCenter[i] * model.header.scaledRange for i in range(3)]

#here if we set the filter to None, we will export the whole point cloud as a las.
#Depending on dataset size this may not be a good idea as las can be up to 10x the UDS size
model.export("./out_full.las", f)

#here we export the full dataset into 8 las file octants
nDivs = 2
f.size = [f.size[i]/nDivs for i in range(3)]
modelCentre = [model.header.baseOffset[i] + model.header.boundingBoxCenter[i] * model.header.scaledRange for i in range(3)]
#the centre of the lower left octant
lowerLeft = [modelCentre[i] - f.size[i] * nDivs/2 for i in range(3)]
for i in range(nDivs):
  for j in range(nDivs):
    for k in range(nDivs):
      f.position = [
        (i + 1) * f.size[0] + lowerLeft[0],
        (j + 1) * f.size[1] + lowerLeft[1],
        (k + 1) * f.size[2] + lowerLeft[2],
      ]
      print(f.position)
      model.export(f"./out_{i}{j}{k}.las", f)



pass
