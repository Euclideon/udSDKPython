from ctypes import *
from enum import IntEnum
from udSDK import *


class udConvertSourceProjection(IntEnum):
    SourceCartesian = 0
    SourceLatLong = 1
    SourceLongLat = 2
    SourceEarthCenteredAndFixed = 3
    Count = 4

class udConvertInfo(Structure):
    _fields_ = [
        ("pOutputName", c_char_p), #!< The output filename
        ("pTempFilesPrefix", c_char_p), #!< The file prefix for temp files

        ("pMetadata", c_char_p),#!< The metadata that will be added to this model (in JSON format)

        ("globalOffset", c_double *3), #!< This amount is added to every point during conversion. Useful for moving the origin of the entire scene to geolocate

        ("minPointResolution", c_double), #!< The native resolution of the highest resolution file
        ("maxPointResolution", c_double),  #!< The native resolution of the lowest resolution file
        ("skipErrorsWherePossible", c_uint32),  #!< If not 0 it will continue processing other files if a file is detected as corrupt or incorrect

        ("everyNth", c_uint32),  #!< If this value is >1, only every Nth point is included in the model. e.g. 4 means only every 4th point will be included, skipping 3/4 of the points
        ("polygonVerticesOnly", c_uint32),  #!< If not 0 it will skip rasterization of polygons in favour of just processing the vertices
        ("retainPrimitives", c_uint32),  #!< If not 0 rasterised primitives such as triangles/lines/etc are retained to be rendered at finer resolution if required at runtime

        ("overrideResolution", c_uint32),  #!< Set to not 0 to stop the resolution from being recalculated
        ("pointResolution", c_double), #!< The scale to be used in the conversion (either calculated or overriden)

        ("overrideSRID", c_uint32),  #!< Set to not 0 to prevent the SRID being recalculated
        ("srid", c_int), #!< The geospatial reference ID (either calculated or overriden)

        ("totalPointsRead", c_uint64),  #!< How many points have been read in this model
        ("totalItems", c_uint64),  #!< How many items are in the list

        # These are quick stats while converting
        ("currentInputItem", c_uint64),  #!< The index of the item that is currently being read
        ("outputFileSize", c_uint64),  #!< Size of the result UDS file
        ("sourcePointCount", c_uint64),  #!< Number of points added (may include duplicates or out of range points)
        ("uniquePointCount", c_uint64),  #!< Number of unique points in the final model
        ("discardedPointCount", c_uint64),  #!< Number of duplicate or ignored out of range points
        ("outputPointCount", c_uint64),  #!< Number of points written to UDS (can be used for progress)
        ("peakDiskUsage", c_uint64),  #!< Peak amount of disk space used including both temp files and the actual output file
        ("peakTempFileUsage", c_uint64),  #!< Peak amount of disk space that contained temp files
        ("peakTempFileCount", c_uint32),  #!< Peak number of temporary files written
    ]

class udConvertItemInfo(Structure):
    _fields_ = [
        ("pFilename", c_char_p),
        ("pointsCount", c_int64),
        ("pointsRead", c_uint64),
        ("sourceProjection", c_int)
    ]

class udConvertContext:
    def __init__(self):
        self.udConvert_CreateContext = getattr(udSDKlib, "udConvert_CreateContext")
        self.udConvert_DestroyContext = getattr(udSDKlib, "udConvert_DestroyContext")
        self.udConvert_SetOutputFilename = getattr(udSDKlib, "udConvert_SetOutputFilename")
        self.udConvert_SetTempDirectory = getattr(udSDKlib, "udConvert_SetTempDirectory")
        self.udConvert_SetPointResolution = getattr(udSDKlib, "udConvert_SetPointResolution")
        self.udConvert_SetSRID = getattr(udSDKlib, "udConvert_SetSRID")
        self.udConvert_SetGlobalOffset = getattr(udSDKlib, "udConvert_SetGlobalOffset")
        self.udConvert_SetSkipErrorsWherePossible = getattr(udSDKlib, "udConvert_SetSkipErrorsWherePossible")
        self.udConvert_SetEveryNth = getattr(udSDKlib, "udConvert_SetEveryNth")
        self.udConvert_SetPolygonVerticesOnly = getattr(udSDKlib, "udConvert_SetPolygonVerticesOnly")
        self.udConvert_SetRetainPrimitives = getattr(udSDKlib, "udConvert_SetRetainPrimitives")
        self.udConvert_SetMetadata = getattr(udSDKlib, "udConvert_SetMetadata")
        self.udConvert_AddItem = getattr(udSDKlib, "udConvert_AddItem")
        self.udConvert_RemoveItem = getattr(udSDKlib, "udConvert_RemoveItem")
        self.udConvert_SetInputSourceProjection = getattr(udSDKlib, "udConvert_SetInputSourceProjection")
        self.udConvert_GetInfo = getattr(udSDKlib, "udConvert_GetInfo")
        self.udConvert_DoConvert = getattr(udSDKlib, "udConvert_DoConvert")
        self.udConvert_Cancel = getattr(udSDKlib, "udConvert_Cancel")
        self.udConvert_Reset = getattr(udSDKlib, "udConvert_Reset")
        self.udConvert_GeneratePreview = getattr(udSDKlib, "udConvert_GeneratePreview")
        self.pConvertContext = c_void_p(0)

    def Create(self, context):
        _HandleReturnValue(self.udConvert_CreateContext(context.pContext, byref(self.pConvertContext)))

    def Destroy(self):
        _HandleReturnValue(self.udConvert_DestroyContext(byref(self.pConvertContext)))

    def Output(self, fileName):
        _HandleReturnValue(self.udConvert_SetOutputFilename(self.pConvertContext, fileName.encode('utf8')))

    def AddItem(self, modelName):
        _HandleReturnValue(self.udConvert_AddItem(self.pConvertContext, modelName.encode('utf8')))

    def DoConvert(self):
        _HandleReturnValue(self.udConvert_DoConvert(self.pConvertContext))

