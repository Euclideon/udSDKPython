"""
Example of running a custom conversion with callbacks defined in Python
It demonstrates creating a UDS with an RGB, Intensity, and an arbitrary 32 bit float channel
Output is a uds of a green plane

Note that using Python for this kind of task is significantly slower than a compiled language. For large conversions
we recommend using C++
"""

from sys import argv
import udSDK
import udSDKConvert
import math
from ctypes import *
import sampleLogin

udSDK.LoadUdSDK("")
outputFileName = "./customConvertOutput.uds"
if __name__ == "__main__":
    context = udSDK.udContext()
    sampleLogin.log_in_sample(context)
    convertContext = udSDKConvert.udConvertContext(context)

    # the folllowing definitions are given to udSDK and executed after do_convert is called
    class InputData(Structure):
        """
        User data to be passed to callbacks
        """
        _fields_ = [("pointsWritten", c_int),
                    ("currentX", c_int),
                    ("currentY", c_int),
                    ("maxX", c_int),
                    ("maxY", c_int),
                    ]

    def encodeRGB(rgb:tuple):
        return (rgb[0] << 16 | rgb[1] << 8 | rgb[2])

    def openItem(*args):
        print("called open function")
        return udSDK.udError.Success

    def closeItem(*args):
        print("called close function")
        return udSDK.udError.Success

    def readFloatItem(convertInput: POINTER(udSDKConvert.udConvertCustomItem), pBuffer: POINTER(udSDK.udPointBufferF64._udPointBufferF64)):
        """
        This callback will write a maxX x maxY green plane into a UDS
        """
        buffer = udSDK.udPointBufferF64(pStruct=pBuffer)
        buffer.pStruct.contents.pointCount = 0
        convertInputStruct = cast(convertInput, POINTER(udSDKConvert.udConvertCustomItem))
        inputDataStruct = cast(convertInputStruct.contents.pData, POINTER(InputData)).contents
        # we will write a green plane to the file:
        for x in range(inputDataStruct.currentX, inputDataStruct.maxX):
            inputDataStruct.currentX = x
            for y in range(inputDataStruct.currentY, inputDataStruct.maxY):
                #we store the progress of the conversion in the data struct so we can continue once the buffer is full
                inputDataStruct.currentY = y

                try:
                    buffer.add_point()
                except OverflowError:
                    print(f"\rpoints read: {inputDataStruct.pointsWritten}/{inputDataStruct.maxX * inputDataStruct.maxY}", end="")
                    #the buffer is full, we need to return to get a new buffer
                    return udSDK.udError.Success

                buffer.positions[-1] = [x * convertInputStruct.contents.sourceResolution, y * convertInputStruct.contents.sourceResolution, 100 * z(x, y) * convertInputStruct.contents.sourceResolution] # set the position of our new point
                buffer.attrAccessors['udRGB'][-1] = encodeRGB((0, int((z(x, y) + 1) * 255), 0)) #RGB
                buffer.attrAccessors['udIntensity'][-1] = 2**16 - 1 # max value for 16 bit int
                buffer.attrAccessors['my_float'][-1] = 3.14159 # 32 bit float

                inputDataStruct.pointsWritten += 1
            inputDataStruct.currentY = 0
        inputDataStruct.currentX += 1 # this makes sure that the loop doesn't run on the next call
        print(f"\rpoints read: {inputDataStruct.pointsWritten}/{inputDataStruct.maxX * inputDataStruct.maxY}", end="")
        #if buffer.pointCount is 0 when we return then the reading stage will complete, otherwise we will call this again with another pointbuffer
        return udSDK.udError.Success

    def destroyItem(*args):
        print("called destroy function")
        return udSDK.udError.Success

    def z(x, y):
        """ definition of our model as a function in x, y"""
        return (math.sin(x/100) + math.cos(y/100))/2

    # this defines what data is stored in our points, we store a colour, an intensity, and a custom attribute
    stdContent = udSDK.udStdAttributeContent.udSAC_ARGB | udSDK.udStdAttributeContent.udSAC_Intensity
    attributes = udSDK.udAttributeSet(stdContent, 1) # 1 additional attribute to be defined

    # setting up a custom attribute:
    customAttributeDescriptor = udSDK.udAttributeDescriptor()
    customAttributeDescriptor.typeInfo = udSDK.udAttributeTypeInfo.udATI_float32
    customAttributeDescriptor.blendType = udSDK.udAttributeBlendType.udABT_Mean
    customAttributeDescriptor.name = "my_float".encode('utf8') # maximum 63 characters
    attributes.append(customAttributeDescriptor)

    customConvertItem = udSDKConvert.udConvertCustomItem()
    customConvertItem.open = openItem
    customConvertItem.close = closeItem
    customConvertItem.destroy = destroyItem
    customConvertItem.read_points_float = readFloatItem
    customConvertItem.attributes = attributes
    customConvertItem.sourceResolution = 0.5 # size of a point in m

    #passing user data struct to conversion
    userData = InputData()
    userData.pointCount = 0
    userData.currentX = 0
    userData.currentY = 0
    userData.maxX = 1000
    userData.maxY = 1000
    customConvertItem.userData = userData

    # metadata and the like can also be defined for the conversion as in basic_convert.py
    convertContext.add_custom_item(customConvertItem)
    convertContext.set_output(outputFileName)
    convertContext.do_convert()
