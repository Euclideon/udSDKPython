"""
Demonstration of using udSDK to export LAS tiles from a UDS file. The uds is split a set number of
"""
import pathlib

import udSDK

udSDK.LoadUdSDK("")
import udSDKProject
import udSDKGeometry
import sampleLogin
from sys import argv

def export_tiles(divX=2, divY=2, divZ=1, previewOnly=False):
  """
  exports the pointcloud into a set of las files divided by nDivs along each respective axis
  previewOnly creates a udProject file with the appropriate box filters inserted at their locations in space without performing the full export
  """
  nDivs = (divX, divY, divZ)
  f = udSDKGeometry.udGeometryOBB()
  size = [model.header.boundingBoxExtents[i] * model.header.scaledRange for i in range(3)]
  size = [size[i] / nDivs[i] for i in range(3)]
  f.size = size
  modelCentre = [model.header.baseOffset[i] + model.header.boundingBoxCenter[i] * model.header.scaledRange for i in
                 range(3)]
  # the centre of the lower left octant
  lowerLeft = [modelCentre[i] - f.size[i] * (nDivs[i] - 1) for i in range(2)]
  lowerLeft.append(modelCentre[2])
  points = udSDK.udPointBufferF64(10000, attributeSet=model.header.attributes)
  pathlib.Path(f"./{modelName}").mkdir(parents=True, exist_ok=True)
  for i in range(nDivs[0]):
    for j in range(nDivs[1]):
      for k in range(nDivs[2]):
        f.position = [
          i * f.size[0] * 2 + lowerLeft[0],
          j * f.size[1] * 2 + lowerLeft[1],
          k * f.size[2] * 2 + lowerLeft[2],
          ]
        # here we use query to check if there are any points enclosed in our volume - if not we don't add the volume to
        # the project
        query = udSDK.udQueryContext(context, model, f)
        if not query.execute(points):
          continue

        if not previewOnly:
          model.export(f"./{modelName}/tile{i}_{j}_{k}.las", f)

        node = f.as_project_node(project.rootNode)
        node.name = f"tile{i}_{j}_{k}"
  project.save()

if __name__ == "__main":
  if len(argv) != 1:
    print(f"""Usage: {argv[0]} modelPath divX divY divZ preview\n"
          modelPath: the model to be exported\n
          divX: the number of divisions along the X axis to split the model\n
          divY: the number of divisions along the Y axis to split the model\n
          divZ: the number of divisions along the Z axis to split the model\n
          preview: if not 0 this will not export the las files, instead previewing in the written project file
          """)

  context = udSDK.udContext()
  sampleLogin(context)
  project = udSDKProject.udProject(context)
  project.create_in_file("Export Filter Placement Preview", "./testFilterPlacementGeo.udjson", True)
  modelPath = argv[1]
  modelName = modelPath.split('/')[-1].split('.')[0]
  model = udSDK.udPointCloud(path=modelPath, context=context)
  modelMetadata = model.metadata

  #this sets the geozone for the project:
  epsg = int(modelMetadata.get("ProjectionID", 0).split(":")[-1])
  project.rootNode.set_metadata_int("projectcrs", epsg)
  project.rootNode.set_metadata_int("defaultcrs", epsg)

  # Create an orinted bounding box from which we perform a query
  f = udSDKGeometry.udGeometryOBB()
  # this is a filter that is the size of the bounding box of the UDS.
  # Exporting or querying using this will give all points in the dataset
  f.size = [model.header.boundingBoxExtents[i] * model.header.scaledRange for i in range(3)]
  f.position = [model.header.baseOffset[i] + model.header.boundingBoxCenter[i] * model.header.scaledRange for i in
                range(3)]


  filterSize = [model.header.boundingBoxExtents[i] * model.header.scaledRange for i in range(3)]
  filterPosition = [model.header.baseOffset[i] + model.header.boundingBoxCenter[i] * model.header.scaledRange for i in
                range(3)]
  # here if we set the filter to None, we will export the whole point cloud as a las.
  # Depending on dataset size this may not be a good idea as las can be up to 10x the UDS size
  # model.export("./out_full.las", f)

  preview = False
  if int(argv[4]) != 0:
    preview = True
  export_tiles(int(argv[2]), int(argv[3]), int(argv[3]), previewOnly=preview)
