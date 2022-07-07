from sys import argv

from udSDK import *
from udSDKConvert import *
from udSDKScene import *
import sampleLogin

if __name__ =="__main__":
  LoadUdSDK('./udSDK')
  context = udContext()
  server = "https://udstream.euclideon.com"
  appName = "SMIObjConverter"
  sampleLogin.log_in_sample(context)

  scene = udScene(context)
  scenePath = "C:/Users/BradenWockner/Desktop/Mt Isa Atlas/SMIScene.json"
  scene.load_from_file(scenePath)
  root = scene.rootNode
  #Traverse over the tree converting objs to uds:

  class objConverter(udSceneNode):
    def traverse(self):
      if self.pURI is not None:
        uri = self.pURI.decode('utf8')
      else:
        uri = ''
      if len(uri.split('.')) > 0 and uri.split('.')[-1] == 'obj':
        print(f"found obj at {uri}")
        start = uri[:2]
        if start == "./": #the scene path is relative
          relativePath = uri
          p = scenePath.split('/')[:-1]
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
            srid = (root.get_metadata_int("projectcrs"))
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
            pointCloud.load(context, outName)
            m = pointCloud.header
            position = [m.scaledRange * m.pivot[i] + m.baseOffset[i] for i in range(3)]
          except:
            position = [0, 0, 0]
          self.set_geometry(udSceneGeometryType.udPGT_Point, position)
          self.uri = projOutPath
          self.itemtypeStr = "UDS".encode('utf8')
          self.itemtype = udSceneNodeType.udPNT_PointCloud

      for child in self.children:
        child.__class__ = self.__class__
        child.traverse()
  root.__class__ = objConverter
  root.traverse()
  scene.save()

  pass
