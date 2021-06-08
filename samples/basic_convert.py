"""
Bare basic example of using Python to perform a conversion to uds
All file
"""
from sys import argv

import udSDK
import udSDKConvert
udSDK.LoadUdSDK("")

if __name__ == "__main__":
  context = udSDK.udContext()
  context.log_in(argv[1], argv[2])

  convertContext = udSDKConvert.udConvertContext(context)
  #add the input files:
  convertContext.add_item("../samplefiles/sampleInput.las")
  #additional items can be added, eg:
  #convertContext.add_item("../samplefiles/inputlas2.las")

  convertContext.set_output("./basicConvertOutput.uds")

  #metadata stored in the file header, for example certain keys are read in a certain way by udStream:
  convertContext.set_metadata("Copyright", "Euclideon, 2021")
  #this sets the uds grid size in metres, downsampling is performed as first point in
  convertContext.set_point_resolution(0.01)

  convertContext.do_convert()