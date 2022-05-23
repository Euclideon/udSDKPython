#!/usr/bin/env python3

#######################################################
#  A udSDK Convert Hello World! program in Python3.8   #
#######################################################

"""
converter.py

General purpose command line converter for Euclideon udSDK using python
Requires udSDK shared libraries (.so or .dll)
Converts any point cloud format supported by udSDK to UDS format

By default will produce one UDS for each model provided
If no models are provided the program will attempt to convert the sample file located
at ../../samplefiles/DirCube.uds

--merge produces a single uds from the input files 

output files are stored in:
    ./convertedUDS/[inputName].uds for individual mode
    ./mergedUDS/[firstInputName].uds for merge mode
    
    
Usage:
    converter username password [models] [--merge]
"""

import os
from os.path import abspath
from sys import argv
from sys import exit

import udSDK
import udSDKConvert
import sampleLogin

#######################################################
####################### Setup #########################
#######################################################

# Load the SDK and fetch symbols
SDKPath = abspath("./udSDK") #this is where we will look for the dll first
udSDK.LoadUdSDK(SDKPath)

appName = "PythonSample_Convert"

#some default values; these should be overwritten by argv
modelFiles = [abspath("./samplefiles/DirCube.uds")]
outFile = abspath("./ConvertedUDS.uds")

context = udSDK.udContext()

def login():
    """
    Connect to the udStream server

    Returns
    -------
    None.

    """
    try:
        sampleLogin.log_in_sample(context)
        return udSDKConvert.udConvertContext(context)
    except udSDK.UdException as err:
        err.printout()
        exit()

def logout():
        # Exit gracefully
      context.disconnect()
  
def convert_model(convertContext, modelFiles, outFile):
    """
    performs a conversion of a list of input files to the output UDS at path outfile

    Parameters
    ----------
    modelFiles : List[string]
        List of paths to files to be converted
    outFile : string
        path to the output file to be written

    Returns
    -------
    None.

    """

    try:
      
      formattedInputNames = ""
      for modelFile in modelFiles:
          convertContext.add_item(modelFile)
          formattedInputNames += "\t {}\n".format(modelFile)
      convertContext.set_output(outFile)
      
      print("Converting files:\n {} to {}".format(formattedInputNames,outFile))
      convertContext.do_convert()
      print("done")
      
      
    except udSDK.UdException as err:
      err.printout()
    

#######################################################
######################## Main #########################
#######################################################
if __name__ == "__main__":
    if len(argv)<3:
        print("Usage: {} udSDKUserName udSDKPassword [--merge] [inputFiles]".format(argv[0]))
    try:
        argv.remove("--merge")
        merge = True
    except ValueError:
        merge = False
    
    #mass convert, single directory, individual output files
    if len(argv) >= 3:
        userName = argv[1]
        userPass = argv[2]

    if len(argv) >= 4:
        modelFiles = argv[3:]
    else:
        print("No model specified, falling back to example uds at {}".format(modelFiles[0]))
        
    convertContext = login()
    
    if merge:
        outFile = abspath("./mergedUDS/"+os.path.basename(modelFiles[0])+".uds")
        convert_model(convertContext, modelFiles, outFile)
    else:
        for modelFile in modelFiles:
            outFile = os.path.splitext(modelFile)[0]
            outFile = abspath("./convertedUDS/"+os.path.basename(outFile)+".uds")
            convert_model(convertContext, [modelFile], outFile)
    
    logout()
