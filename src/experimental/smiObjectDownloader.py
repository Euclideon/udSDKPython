from sys import argv

from udSDK import *
from udSDKConvert import *
from udSDKProject import *

if __name__ =="__main__":
  LoadUdSDK('./udSDK')
  context = udContext()
  server = "https://udstream.euclideon.com"
  appName = "SMIObjConverter"

  try:
    context.try_resume(server, appName, argv[1])
  except UdException:
    context.connect_legacy(server, appName, argv[1], argv[2])

  project = udProject(context)
  projectPath = "C:/Users/BradenWockner/Desktop/Mt Isa Atlas/SMIProject.json"
  project.LoadFromFile(projectPath)
  root = project.rootNode
  #Traverse over the tree converting objs to uds:

  class objConverter(udProjectNode):
    def traverse(self):
      if self.pURI is not None:
        uri = self.pURI.decode('utf8')
      else:
        uri = ''
      if len(uri.split('.')) > 0 and uri.split('.')[-1] == 'obj':
        print(f"found obj at {uri}")
        start = uri[:2]
        if start == "./": #the project path is relative
          relativePath = uri
          p = projectPath.split('/')[:-1]
          p.append(uri[2:])
          absolutePath = '/'.join(p) #this is passed to the converter
          projOutPath = '.' + ''.join(relativePath.split('.')[:-1]) + '.uds'

        else:
          absolutePath = uri
          projOutPath = ''.join(absolutePath.split('.')[:-1]) + '.uds'

        outName = ''.join(absolutePath.split('.')[:-1]) + '.uds'

        try:
          doConvert = False
          failure = False
          if doConvert:
            if os.path.exists(outName):
              raise FileExistsError("File has already been converted, skipping")

            converter = udConvertContext(context)
            converter.set_output(outName)
            converter.add_item(absolutePath)
            converter.set_point_resolution(10)
            converter.set_global_offset(self.coordinates[0])
            srid = (root.GetMetadataInt("projectcrs"))
            converter.set_srid(srid)
            converter.do_convert()

        except UdException as e:
          print(f"conversion failed: {e}")
          failure = True
        except Exception as e:
          print(f"conversion failed: {e}")

        if not failure:
          try:
            pointCloud = udPointCloud()
            pointCloud.Load(context, outName)
            m = pointCloud.header
            position = [m.scaledRange * m.pivot[i] + m.baseOffset[i] for i in range(3)]
          except:
            position = [0, 0, 0]
          self.SetGeometry(udProjectGeometryType.udPGT_Point, position)
          self.set_uri(projOutPath)
          self.itemtypeStr = "UDS".encode('utf8')
          self.itemtype = udProjectNodeType.udPNT_PointCloud

      for child in self.children:
        child.__class__ = self.__class__
        child.traverse()
  root.__class__ = objConverter
  root.traverse()
  project.Save()
  #converter.set_output("out.uds")
  #converter.add_item("C:/git/udSDKPython/T-Rex.obj")

  #converter.do_convert()
  pass
