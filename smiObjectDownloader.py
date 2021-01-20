from udSDK import *
from udSDKConvert import *
from udSDKProject import *
from sys import argv


if __name__ =="__main__":
  LoadUdSDK('./udSDK')
  context = udContext()
  server = "https://udstream.euclideon.com"
  appName = "SMIObjConverter"

  try:
    context.try_resume(server,appName,argv[1])
  except UdException:
    context.Connect(server,appName , argv[1], argv[2])

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
      start = uri[:2]
      oldURI = None
      if start =="./":
        oldURI = uri
        p = projectPath.split('/')[:-1]
        p.append(uri[2:])
        uri = '/'.join(p)
        pass
      if len(uri.split('.')) > 0 and uri.split('.')[-1] == 'obj':
        print(f"found obj at {uri}")
        if oldURI is None:
          outName = ''.join(uri.split('.')[:-1])+'.uds'
        else:
          outName = '.'+''.join(oldURI.split('.')[:-1])+'.uds'
        try:
          doConvert = False
          if doConvert:
            converter = udConvertContext(context)
            converter.set_output(outName)
            converter.add_item(uri)
            converter.set_point_resolution(10)
            #converter.set_global_offset()
            converter.do_convert()
          self.set_uri(outName)
          self.itemtypeStr = "UDS".encode('utf8')
          self.itemtype = udProjectNodeType.udPNT_PointCloud
        except UdException as e:
          print(f"conversion failed: {e}")

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
