from udSDK import *
from udSDKConvert import *
from udSDKProject import *
from sys import argv

if __name__ =="__main__":
  LoadUdSDK("./udSDK")
  context = udContext()
  server = "https://udstream.euclideon.com"
  appName = "SMIObjConverter"

  try:
    context.try_resume(server,appName,argv[1])
  except UdException:
    context.Connect(server,appName , argv[1], argv[2])

    project = udProject(context)
  project.CreateInMemory("testProj")
  root = project.rootNode

  converter = udConvertContext(context)
  converter.set_output("out.uds")
  converter.add_item("C:/git/udSDKPython/T-Rex.obj")
  
  converter.do_convert()
  pass
