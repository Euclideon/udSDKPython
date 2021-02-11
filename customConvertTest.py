"""
This is an attempt at wrapping udCustomConvert: the result is currently a udE_Failure
when trying to run doConvert...
"""

from sys import argv

import udSDK
import udSDKConvert
from ctypes import *

udSDK.LoadUdSDK("")
if __name__ == "__main__":
    context = udSDK.udContext()
    udServer = "https://udstream.euclideon.com"
    appName = "customConvertPython"
    try:
        context.try_resume(udServer,appName,argv[1])
    except udSDK.UdException:
        context.Connect(udServer, appName, argv[1], argv[2])
    convertContext = udSDKConvert.udConvertContext(context)

    class InputData(Structure):
        _fields_ = [("pointsWritten", c_int)]

    def openItem(*args):
        return udSDK.udError.Success

    def closeItem(*args):
        return udSDK.udError.Success

    def readFloatItem(convertInput: POINTER(udSDKConvert.udConvertCustomItem), pBuffer: POINTER(udSDK.udPointBufferF64)):
        buffer = pBuffer.contents
        #pointsWritten = cast(convertInput.contents.pData,POINTER(InputData)).contents.pointsWritten
        #if pointsWritten == 0:
            #buffer.pointCount = 0
            #buffer.pPositions[buffer.pointCount] = 0
            #buffer.pPositions[buffer.pointCount + 1] = 0
            #buffer.pPositions[buffer.pointCount + 2] = 0
            #buffer.pointCount += 1
        buffer.pointCount = 0

        return udSDK.udError.Success

    def destroyItem(*args):
        return udSDK.udError.Success

    class ItemData(Structure):
        _fields_ = []

    attributes = udSDK.udAttributeSet(0, 1)

    customConvertItem = udSDKConvert.udConvertCustomItem()
    customConvertItem.open = openItem
    customConvertItem.close = closeItem
    customConvertItem.destroy = destroyItem
    customConvertItem.read_points_float = readFloatItem
    customConvertItem.attributes = attributes

    convertContext.add_custom_item(customConvertItem)
    convertContext.set_output("C:/git/testout.uds")
    convertContext.do_convert()
    pass






