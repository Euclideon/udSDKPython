from ctypes import *
from enum import IntEnum
import udSDK
from udSDK import _HandleReturnValue,  udAttributeSet



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
    def __init__(self, context):
        self._udConvert_CreateContext = getattr(udSDK.udSDKlib, "udConvert_CreateContext")
        self._udConvert_DestroyContext = getattr(udSDK.udSDKlib, "udConvert_DestroyContext")
        self._udConvert_SetOutputFilename = getattr(udSDK.udSDKlib, "udConvert_SetOutputFilename")
        self._udConvert_SetTempDirectory = getattr(udSDK.udSDKlib, "udConvert_SetTempDirectory")
        self._udConvert_SetPointResolution = getattr(udSDK.udSDKlib, "udConvert_SetPointResolution")
        self._udConvert_SetSRID = getattr(udSDK.udSDKlib, "udConvert_SetSRID")
        self._udConvert_SetGlobalOffset = getattr(udSDK.udSDKlib, "udConvert_SetGlobalOffset")
        self._udConvert_SetSkipErrorsWherePossible = getattr(udSDK.udSDKlib, "udConvert_SetSkipErrorsWherePossible")
        self._udConvert_SetEveryNth = getattr(udSDK.udSDKlib, "udConvert_SetEveryNth")
        self._udConvert_SetPolygonVerticesOnly = getattr(udSDK.udSDKlib, "udConvert_SetPolygonVerticesOnly")
        self._udConvert_SetRetainPrimitives = getattr(udSDK.udSDKlib, "udConvert_SetRetainPrimitives")
        self._udConvert_SetMetadata = getattr(udSDK.udSDKlib, "udConvert_SetMetadata")
        self._udConvert_AddItem = getattr(udSDK.udSDKlib, "udConvert_AddItem")
        self._udConvert_RemoveItem = getattr(udSDK.udSDKlib, "udConvert_RemoveItem")
        self._udConvert_SetInputSourceProjection = getattr(udSDK.udSDKlib, "udConvert_SetInputSourceProjection")
        self._udConvert_GetInfo = getattr(udSDK.udSDKlib, "udConvert_GetInfo")
        self._udConvert_GetItemInfo = getattr(udSDK.udSDKlib, "udConvert_GetItemInfo")
        self._udConvert_DoConvert = getattr(udSDK.udSDKlib, "udConvert_DoConvert")
        self._udConvert_Cancel = getattr(udSDK.udSDKlib, "udConvert_Cancel")
        self._udConvert_Reset = getattr(udSDK.udSDKlib, "udConvert_Reset")
        self._udConvert_GeneratePreview = getattr(udSDK.udSDKlib, "udConvert_GeneratePreview")
        self._udConvert_AddCustomItem = getattr(udSDK.udSDKlib, "udConvert_AddCustomItem")
        self.pConvertContext = c_void_p(0)
        self.create(context)

    def create(self, context):
        _HandleReturnValue(self._udConvert_CreateContext(context.pContext, byref(self.pConvertContext)))

    def __del__(self):
        _HandleReturnValue(self._udConvert_DestroyContext(byref(self.pConvertContext)))

    def set_output(self, filename):
        _HandleReturnValue(self._udConvert_SetOutputFilename(self.pConvertContext, filename.encode('utf8')))

    def set_temp_directory(self, directory):
        _HandleReturnValue(self._udConvert_SetTempDirectory(self.pConvertContext, directory))

    def set_point_resolution(self, resolution):
        resolution = c_double(resolution)
        _HandleReturnValue(self._udConvert_SetPointResolution(self.pConvertContext, 1, resolution))

    def set_srid(self, srid):
        srid = c_int32(srid)
        _HandleReturnValue(self._udConvert_SetSRID(self.pConvertContext, 1, srid))

    def set_global_offset(self, offset):
        offset = (c_double*3)(*offset)
        _HandleReturnValue(self._udConvert_SetGlobalOffset(self.pConvertContext, offset))

    def set_skip_errors_where_possible(self, skip=True):
        _HandleReturnValue(self._udConvert_SetSkipErrorsWherePossible(self.pConvertContext, skip))

    def set_every_nth(self, everynth):
        everynth = c_uint32(everynth)
        _HandleReturnValue(self._udConvert_SetEveryNth(self.pConvertContext, everynth))

    def set_polygon_vertices_only(self, set=True):
        _HandleReturnValue(self._udConvert_SetPolygonVerticesOnly(self.pConvertContext, set))

    def set_retain_primitives(self, set=True):
        _HandleReturnValue(self._udConvert_SetRetainPrimitives(self.pConvertContext, set))

    def set_metadata(self, key, value):
        key = key.encode('utf8')
        value = value.encode('utf8')
        _HandleReturnValue(self._udConvert_SetMetadata(self.pConvertContext, key, value))

    def remove_item(self, index):
        index = c_uint64(index)
        _HandleReturnValue(self._udConvert_RemoveItem(self.pConvertContext, index))

    def set_input_source_projection(self, actualProjection):
        _HandleReturnValue(self._udConvert_SetInputSourceProjection(self.pConvertContext, actualProjection))

    def add_item(self, modelName):
        _HandleReturnValue(self._udConvert_AddItem(self.pConvertContext, modelName.encode('utf8')))

    def do_convert(self):
        _HandleReturnValue(self._udConvert_DoConvert(self.pConvertContext))

    def cancel(self):
        _HandleReturnValue(self._udConvert_Cancel(self.pConvertContext))

    def reset(self):
        _HandleReturnValue(self._udConvert_Reset(self.pConvertContext))

    def generate_preview(self, pointcloud:udSDK.udPointCloud):
        _HandleReturnValue(self._udConvert_GeneratePreview(self.pConvertContext, pointcloud.pPointCloud))

    def get_info(self):
        info = udConvertInfo()
        _HandleReturnValue(self._udConvert_GetInfo(self.pConvertContext, byref(info)))
        return info

    def get_item_info(self):
        info = udConvertItemInfo()
        _HandleReturnValue(self._udConvert_GetItemInfo(self.pConvertContext, byref(info)))

class udConvertCustomItemFlags(IntEnum):
    udCCIF_None = 0 #!< No additional flags specified
    udCCIF_SkipErrorsWherePossible = 1 #!< If its possible to continue parsing that is perferable to failing
    udCCIF_PolygonVerticesOnly = 2 #!< Do not rasterise the polygons just use the vertices as points


OPENFUNCTYPE = CFUNCTYPE(udSDK.udError, c_void_p, c_uint32, c_double * 3, c_double, c_int)
READFLOATFUNCTYPE = CFUNCTYPE(udSDK.udError, c_void_p, POINTER(udSDK.udPointBufferF64))
READINTFUNCTYPE = CFUNCTYPE(udSDK.udError, c_void_p, POINTER(udSDK.udPointBufferI64))
CLOSEFUNCTYPE = CFUNCTYPE(None, c_void_p)
DESTROYFUNCTYPE = CFUNCTYPE(None, c_void_p)

def passFCN(*args):
    return 0

class udConvertCustomItem(Structure):
    _fields_ = [
        ("pOpen", OPENFUNCTYPE),
        ("pReadPointsInt", READINTFUNCTYPE),
        ("pReadPointsFloat", READFLOATFUNCTYPE),
        ("pDestroy", DESTROYFUNCTYPE),
        ("pClose", CLOSEFUNCTYPE),
        ("pData", c_void_p), #!< Private user data relevant to the specific geomtype, must be freed by the pClose function

        ("pName", c_char_p), #!< Filename or other identifier
        ("boundMin", c_double*3),#!< Optional (see boundsKnown) source space minimum values
        ("boundMax", c_double*3),#!< Optional (see boundsKnown) source space maximum values
        ("sourceResolution", c_double),  #!< Source resolution (eg 0.01 if points are 1cm apart). 0 indicates unknown
        ("pointCount", c_int64), #!< Number of points coming, -1 if unknown
        ("srid", c_int32),  #!< If non-zero, this input is considered to be within the given srid code (useful mainly as a default value for other files in the conversion)
        ("attributes", udAttributeSet), #!< Content of the input; this might not match the output
        ("sourceProjection", c_int32 ), #!< SourceLatLong defines x as latitude, y as longitude in WGS84.
        ("boundsKnown", c_uint32), #!< If not 0, boundMin and boundMax are valid, if 0 they will be calculated later
        ("pointCountIsEstimate", c_uint32) #!< If not 0, the point count is an estimate and may be different
    ]
    def __init(self):
        super.__init__()
        self.open = passFCN
        self.close = passFCN
        self.destroy = passFCN
        self.read_points_float = passFCN
        self.read_points_int = passFCN

    @property
    def open(self):
        return self._open
    @open.setter
    def open(self, fcn):
        self._open = fcn
        self.pOpen = OPENFUNCTYPE(self._open)

    @property
    def close(self):
        return self._close
    @close.setter
    def close(self, fcn):
        self._close = fcn
        self.pClose = CLOSEFUNCTYPE(self._close)

    @property
    def read_points_int(self):
        return self._read_points_int
    @read_points_int.setter
    def read_points_int(self, fcn):
        self._read_points_int = fcn
        self.pReadPointsInt = READINTFUNCTYPE(self._read_points_int)

    @property
    def read_points_float(self):
        return self._read_points_float
    @read_points_float.setter
    def read_points_float(self, fcn):
        self._read_points_float = fcn
        self.pReadPointsFloat = READFLOATFUNCTYPE(self._read_points_float)

    @property
    def destroy(self):
        return self._destroy
    @destroy.setter
    def destroy(self, fcn):
        self._destroy = fcn
        self.pClose = DESTROYFUNCTYPE(self._destroy)


