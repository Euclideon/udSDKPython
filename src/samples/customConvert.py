"""
Very bare bones example of running a custom conversion with callbacks defined in Python
This currently only writes point positions, a future version will support writing attributes to the UDS
"""

from sys import argv
import udSDK
import udSDKConvert
from ctypes import *
import sampleLogin

udSDK.LoadUdSDK("")
outputFileName = "./customConvertOutput.uds"
if __name__ == "__main__":
    context = udSDK.udContext()
    sampleLogin.log_in_sample(context)
    convertContext = udSDKConvert.udConvertContext(context)

    class InputData(Structure):
        """
        User data to be passed to callbacks
        """
        _fields_ = [("pointsWritten", c_int)]

    def encodeRGB(rgb:tuple):
        return (rgb[0] << 16 | rgb[1] << 8 | rgb[2])

    def openItem(*args):
        return udSDK.udError.Success

    def closeItem(*args):
        return udSDK.udError.Success

    def readFloatItem(convertInput: POINTER(udSDKConvert.udConvertCustomItem), pBuffer: POINTER(udSDK.udPointBufferF64._udPointBufferF64)):
        """
        This callback will write a single green point into a UDS at position [1, 1, 1]
        """
        buffer = udSDK.udPointBufferF64(pStruct=pBuffer)
        buffer.pStruct.contents.pointCount = 0
        convertInputStruct = cast(convertInput, POINTER(udSDKConvert.udConvertCustomItem))
        inputDataStruct = cast(convertInputStruct.contents.pData, POINTER(InputData)).contents
        if inputDataStruct.pointsWritten == 0:
            buffer.add_point()
            buffer.positions[len(buffer) - 1] = [1, 1, 1]
            buffer.attrAccessors['udRGB'][len(buffer) - 1] = encodeRGB((0, 255, 0))
            inputDataStruct.pointsWritten = 1

        #if buffer.pointCount is 0 when we return then the reading stage will complete, otherwise we will call this again with another pointbuffer
        return udSDK.udError.Success

    def destroyItem(*args):
        return udSDK.udError.Success

    attributes = udSDK.udAttributeSet(udSDK.udStdAttributeContent.udSAC_ARGB, 0)

    customConvertItem = udSDKConvert.udConvertCustomItem()
    customConvertItem.open = openItem
    customConvertItem.close = closeItem
    customConvertItem.destroy = destroyItem
    customConvertItem.read_points_float = readFloatItem
    customConvertItem.attributes = attributes

    #passing user data struct to conversion
    userData = InputData()
    userData.pointCount = 0
    customConvertItem.userData = userData

    convertContext.add_custom_item(customConvertItem)
    convertContext.set_output(outputFileName)
    convertContext.do_convert()
    pass






