"""
Bare basic example of using Python to perform a conversion to uds
"""
from sys import argv

import udSDK
import udSDKConvert
udSDK.LoadUdSDK("")

if __name__ == "__main__":
  context = udSDK.udContext()
  #context.log_in_legacy(argv[1], argv[2])
  context.log_in_interactive()

  convertContext = udSDKConvert.udConvertContext(context)
  #add the input files:
  convertContext.add_item("../samplefiles/sampleInput.las")
  #additional items can be added, this will result in a single uds file containing the  eg:
  #convertContext.add_item("../samplefiles/inputlas2.las")

  convertContext.set_output("./basicConvertOutput.uds")

  #metadata stored in the file header, for example certain keys are read in a certain way by udStream:
  #this is read using a call to udPointCloud_GetMetadata on the loaded UDS. Certain keys have special usage
  #when viewed in udStream so care must be taken when setting some metadata values
  convertContext.set_metadata("Copyright", "Euclideon, 2021")
  ### The following can be uncommented to modify the output
  #this sets the uds grid size in metres, downsampling is performed by taking only the first point in:
  #convertContext.set_point_resolution(0.01)
  #overrides the projection
  #convertContext.set_input_source_projection(inputSRID)
  #this sets the output srid/epsg code. A transformation is performed to the data internally if this does not match the srid set by the function above
  #start the conversion
  convertContext.do_convert()