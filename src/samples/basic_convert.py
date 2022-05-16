"""
Bare basic example of using Python to perform a conversion to uds. This demonstrates the usage of the high level Python
wrapper
"""

import udSDK
import udSDKConvert
import sampleLogin
udSDK.LoadUdSDK("")


if __name__ == "__main__":
  context = udSDK.udContext()
  sampleLogin.log_in_sample(context)

  convertContext = udSDKConvert.udConvertContext(context)

  #add the input files:
  convertContext.add_item("../samplefiles/sampleInput.las")
  #additional items can be added, this will result in a single uds file containing the  eg:
  #convertContext.add_item("../samplefiles/inputlas2.las")

  convertContext.set_output("./basicConvertOutput.uds")

  #metadata stored in the file header, for example certain keys are read in a certain way by udStream:
  #this is read using a call to udPointCloud_GetMetadata on the loaded UDS. Certain keys have special usage
  #when viewed in udStream
  convertContext.set_metadata("Copyright", "Euclideon, 2022")
  ### The following can be uncommented to modify the output
  #this sets the uds grid size in metres, downsampling is performed by taking only the first point read in for each grid cube and discarding all others:
  #convertContext.set_point_resolution(0.01)
  #overrides the projection (srid is equivalent to EPSG code)
  #convertContext.set_input_source_projection(inputSRID)
  #this sets the output srid/epsg code. A transformation is performed to the data internally if this does not match the srid set by the function above
  #convertContext.set_srid(4978)
  #start the conversion
  convertContext.do_convert()