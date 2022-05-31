import ctypes
from enum import IntEnum

import udSDK
from udSDK import _HandleReturnValue, udAttributeSet


class udConvertInfo(ctypes.Structure):
    """
    Class detailing the input parameters and current convert status of a job
    """
    _fields_ = [
        ("pOutputName", ctypes.c_char_p), #!< The output filename
        ("pTempFilesPrefix", ctypes.c_char_p), #!< The file prefix for temp files

        ("pMetadata", ctypes.c_char_p),#!< The metadata that will be added to this model (in JSON format)

        ("attributes", udSDK.udAttributeSet),  # !< The metadata that will be added to this model (in JSON format)
        ("ignoredAttributesLength", ctypes.c_uint32),  # !< The metadata that will be added to this model (in JSON format)
        ("ignoredAttributesList", ctypes.POINTER(ctypes.c_char_p)),

        ("globalOffset", ctypes.c_double *3), #!< This amount is added to every point during conversion. Useful for moving the origin of the entire scene to geolocate

        ("minPointResolution", ctypes.c_double), #!< The native resolution of the highest resolution file
        ("maxPointResolution", ctypes.c_double),  #!< The native resolution of the lowest resolution file
        ("skipErrorsWherePossible", ctypes.c_uint32),  #!< If not 0 it will continue processing other files if a file is detected as corrupt or incorrect

        ("everyNth", ctypes.c_uint32),  #!< If this value is >1, only every Nth point is included in the model. e.g. 4 means only every 4th point will be included, skipping 3/4 of the points
        ("polygonVerticesOnly", ctypes.c_uint32),  #!< If not 0 it will skip rasterization of polygons in favour of just processing the vertices
        ("retainPrimitives", ctypes.c_uint32),  #!< If not 0 rasterised primitives such as triangles/lines/etc are retained to be rendered at finer resolution if required at runtime
        ("bakeLighting", ctypes.c_uint32),
        ("exportOtherEmbeddedAssets", ctypes.c_uint32),

        ("overrideResolution", ctypes.c_uint32),  #!< Set to not 0 to stop the resolution from being recalculated
        ("pointResolution", ctypes.c_double), #!< The scale to be used in the conversion (either calculated or overriden)

        ("overrideSRID", ctypes.c_uint32),  #!< Set to not 0 to prevent the SRID being recalculated
        ("srid", ctypes.c_int), #!< The geospatial reference ID (either calculated or overriden)
        ("pWKT", ctypes.c_char_p),  # !< The geospatial WKT string

        ("totalPointsRead", ctypes.c_uint64),  #!< How many points have been read in this model
        ("totalItems", ctypes.c_uint64),  #!< How many items are in the list

        # These are quick stats while converting
        ("currentInputItem", ctypes.c_uint64),  #!< The index of the item that is currently being read
        ("outputFileSize", ctypes.c_uint64),  #!< Size of the result UDS file
        ("sourcePointCount", ctypes.c_uint64),  #!< Number of points added (may include duplicates or out of range points)
        ("uniquePointCount", ctypes.c_uint64),  #!< Number of unique points in the final model
        ("discardedPointCount", ctypes.c_uint64),  #!< Number of duplicate or ignored out of range points
        ("outputPointCount", ctypes.c_uint64),  #!< Number of points written to UDS (can be used for progress)
        ("peakDiskUsage", ctypes.c_uint64),  #!< Peak amount of disk space used including both temp files and the actual output file
        ("peakTempFileUsage", ctypes.c_uint64),  #!< Peak amount of disk space that contained temp files
        ("peakTempFileCount", ctypes.c_uint32),  #!< Peak number of temporary files written
    ]


class udConvertItemInfo(ctypes.Structure):
    _fields_ = [
        ("pFilename", ctypes.c_char_p),
        ("pointsCount", ctypes.c_int64),
        ("pointsRead", ctypes.c_uint64),
        ("estimatedResolution", ctypes.c_double),
        ("srid", ctypes.c_int)
    ]


class udConvertContext:
    """
    Class representing a conversion from a pointcloud format to a UDS model compatible with the UD renderer
    """
    def __init__(self, context):
        self._udConvert_CreateContext = getattr(udSDK.udSDKlib, "udConvert_CreateContext")
        self._udConvert_DestroyContext = getattr(udSDK.udSDKlib, "udConvert_DestroyContext")
        self._udConvert_SetOutputFilename = getattr(udSDK.udSDKlib, "udConvert_SetOutputFilename")
        self._udConvert_SetTempDirectory = getattr(udSDK.udSDKlib, "udConvert_SetTempDirectory")
        self._udConvert_SetPointResolution = getattr(udSDK.udSDKlib, "udConvert_SetPointResolution")
        self._udConvert_IgnoreAttribute = getattr(udSDK.udSDKlib, "udConvert_IgnoreAttribute")
        self._udConvert_RestoreAttribute = getattr(udSDK.udSDKlib, "udConvert_RestoreAttribute")
        self._udConvert_SetSRID = getattr(udSDK.udSDKlib, "udConvert_SetSRID")
        self._udConvert_SetWKT = getattr(udSDK.udSDKlib, "udConvert_SetWKT")
        self._udConvert_SetGlobalOffset = getattr(udSDK.udSDKlib, "udConvert_SetGlobalOffset")
        self._udConvert_SetSkipErrorsWherePossible = getattr(udSDK.udSDKlib, "udConvert_SetSkipErrorsWherePossible")
        self._udConvert_SetEveryNth = getattr(udSDK.udSDKlib, "udConvert_SetEveryNth")
        self._udConvert_SetPolygonVerticesOnly = getattr(udSDK.udSDKlib, "udConvert_SetPolygonVerticesOnly")
        self._udConvert_SetRetainPrimitives = getattr(udSDK.udSDKlib, "udConvert_SetRetainPrimitives")
        self._udConvert_SetMetadata = getattr(udSDK.udSDKlib, "udConvert_SetMetadata")
        self._udConvert_SetExportOtherEmbeddedAssets = getattr(udSDK.udSDKlib, "udConvert_SetExportOtherEmbeddedAssets")
        self._udConvert_SetBakeLighting = getattr(udSDK.udSDKlib, "udConvert_SetBakeLighting")
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
        self._udCompare_BPA = udSDK.udExceptionDecorator(udSDK.udSDKlib.udCompare_BPA)
        self.pConvertContext = ctypes.c_void_p(0)
        self._create(context)

    def _create(self, context):
        _HandleReturnValue(self._udConvert_CreateContext(context.pContext, ctypes.byref(self.pConvertContext)))

    def __del__(self):
        _HandleReturnValue(self._udConvert_DestroyContext(ctypes.byref(self.pConvertContext)))

    def set_output(self, filename):
        """
        Sets the output filename for the conversion
        """
        _HandleReturnValue(self._udConvert_SetOutputFilename(self.pConvertContext, filename.encode('utf8')))

    def set_temp_directory(self, directory):
        """
        Sets the directory used for storage of temp files used during the conversion process. To increase throughput on
        large conversion it is recommended that this is set to a different physical drive to the one being read from
        """
        _HandleReturnValue(self._udConvert_SetTempDirectory(self.pConvertContext, directory))

    def set_point_resolution(self, resolution):
        """
        Sets the minimum point/voxel size of the conversion. During conversion the pointcloud is divided into a grid of
        this size and points occupying the same grid cube as one already read will be discarded.

        UDS models will be rendered with a mimimum cube size equal to this, for more 'solid' looking point clouds
        it is recommended to increase this value (at the expense of potentially lost information).
        """
        resolution = ctypes.c_double(resolution)
        _HandleReturnValue(self._udConvert_SetPointResolution(self.pConvertContext, 1, resolution))

    def ignore_attribute(self, attributeName:str):
        """
        Instruct the conversion process to not copy the named attribute into the UDS model on conversion. This is often to
        save hard disk space and improve streaming speeds
        """
        attributeName = attributeName.encode('utf8')
        _HandleReturnValue(self._udConvert_IgnoreAttribute(self.pConvertContext, attributeName))

    def restore_attribute(self, attributeName:str):
        """
        Reverses the ignore_attribute operation for named attribute attributeName
        """
        attributeName = attributeName.encode('utf8')
        _HandleReturnValue(self._udConvert_RestoreAttribute(self.pConvertContext, attributeName))

    def set_srid(self, srid):
        """
        sets the spatial reference identifier/ epsg code for the output model
        """
        srid = ctypes.c_int32(srid)
        _HandleReturnValue(self._udConvert_SetSRID(self.pConvertContext, 1, srid))

    def set_wkt(self, wkt:str):
        """
        sets the geozone for the output model using the epsg well known text
        """
        wkt = wkt.encode('utf8')
        _HandleReturnValue(self._udConvert_SetWKT(self.pConvertContext, wkt))

    def set_global_offset(self, offset):
        """
        adds an offset of offset=(XYZ) to the points at convert time
        """
        offset = (ctypes.c_double*3)(*offset)
        _HandleReturnValue(self._udConvert_SetGlobalOffset(self.pConvertContext, offset))

    def set_skip_errors_where_possible(self, skip=True):
        """
        Instructs the conversion process to not fail on non-critical errors
        """
        _HandleReturnValue(self._udConvert_SetSkipErrorsWherePossible(self.pConvertContext, skip))

    def set_every_nth(self, everynth):
        """
        Instructs the convert process to only read every nth (e.g. 3rd for everynth = 3) point in the input. This results
        in a quicker conversion and smaller file size at the expense of loss of detail.
        """
        everynth = ctypes.c_uint32(everynth)
        _HandleReturnValue(self._udConvert_SetEveryNth(self.pConvertContext, everynth))

    def set_polygon_vertices_only(self, set=True):
        """
        When converting polygon formats (e.g. .obj or .fbx files) do not convert the polygon faces to points, instead only
        read the vertices of the model.
        """
        _HandleReturnValue(self._udConvert_SetPolygonVerticesOnly(self.pConvertContext, set))

    def set_retain_primitives(self, set=True):
        """
        If set to true when converting a polygon model retain the underlying polygon at the base level of the model.
        This results in a larger file but retains the base level geometry and textures of the source giving a better
        visual appearance
        """
        _HandleReturnValue(self._udConvert_SetRetainPrimitives(self.pConvertContext, set))

    def set_metadata(self, key, value):
        """
        Insert the metadata key value pair into the file metadata

       There are a number of 'standard' keys that are recommended to support.
            - `Author`: The name of the company that owns or captured the data
            - `Comment`: A miscellaneous information section
            - `Copyright`: The copyright information
            - `License`: The general license information
        """
        key = key.encode('utf8')
        value = value.encode('utf8')
        _HandleReturnValue(self._udConvert_SetMetadata(self.pConvertContext, key, value))

    def set_bake_lighting(self, set=True):
        """
        Bake lighting into the model
        """
        _HandleReturnValue(self._udConvert_SetBakeLighting(self.pConvertContext, ctypes.c_uint32(set)))

    def set_export_other_embedded_assets(self, set=True):
        """
        Where other assets are embedded in an imput file (e.g. orthophotos in a .e57 format) extract them and save to
        the output folder
        """
        _HandleReturnValue(self._udConvert_SetExportOtherEmbeddedAssets(self.pConvertContext, ctypes.c_uint32(set)))

    def remove_item(self, index):
        """
        remove a previously added item from the conversion
        """
        index = ctypes.c_uint64(index)
        _HandleReturnValue(self._udConvert_RemoveItem(self.pConvertContext, index))

    def set_input_source_projection(self, srid:int):
        """
        Overrides the geozone of the input to be srid (as defined by EPSG)
        """
        _HandleReturnValue(self._udConvert_SetInputSourceProjection(self.pConvertContext, srid))

    def add_item(self, inputPath:str):
        """
        adds an input to the conversion
        """
        _HandleReturnValue(self._udConvert_AddItem(self.pConvertContext, inputPath.encode('utf8')))

    def do_convert(self):
        """
        Begins the conversion process with the settings contained in this class
        """
        _HandleReturnValue(self._udConvert_DoConvert(self.pConvertContext))

    def cancel(self):
        """
        Cancels the conversion process
        """
        _HandleReturnValue(self._udConvert_Cancel(self.pConvertContext))

    def reset(self):
        """
        resets the state of the conversion
        """
        _HandleReturnValue(self._udConvert_Reset(self.pConvertContext))

    def generate_preview(self, pointcloud):
        """
        generates a preview of the conversion in memory. The pointcloud is loaded into this.pointcloud and is renderable
        using udsdk
        """
        _HandleReturnValue(self._udConvert_GeneratePreview(self.pConvertContext, pointcloud.pPointCloud))

    def get_info(self):
        """
        returns the information about the conversion
        """
        info = udConvertInfo()
        _HandleReturnValue(self._udConvert_GetInfo(self.pConvertContext, ctypes.byref(info)))
        return info

    def get_item_info(self, index:int):
        """
        returns information about the item at index that has been added to the convert
        """
        info = udConvertItemInfo()
        _HandleReturnValue(self._udConvert_GetItemInfo(self.pConvertContext, index, ctypes.byref(info)))
        return info

    def add_custom_item(self, item:"udConvertCustomItem"):
        """
        Adds a custom item to the conversion (see udConvertCustomItem)
        """
        _HandleReturnValue(udSDK.udSDKlib.udConvert_AddCustomItem(self.pConvertContext, ctypes.byref(item)))

    def compare_bpa(self, baseModelPath:str, comparisonModelPath:str, ballRadius:float, gridSize:float, outputName:str):
        """
        Sets the conversion to compare two models using the ball pivot algorithm (BPA). The output model will have channels
        containing the result of this algorithm
        """
        self._udCompare_BPA(self.pConvertContext, baseModelPath.encode('utf8'), comparisonModelPath.encode('utf8'), ctypes.c_double(ballRadius), ctypes.c_double(gridSize), outputName.encode('utf8'))

class udConvertCustomItemFlags(IntEnum):
    udCCIF_None = 0 #!< No additional flags specified
    udCCIF_SkipErrorsWherePossible = 1 #!< If its possible to continue parsing that is perferable to failing
    udCCIF_PolygonVerticesOnly = 2 #!< Do not rasterise the polygons just use the vertices as points
    udCCIF_BakeLighting = 8
    udCCIF_ExportImages = 16


OPENFUNCTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_double * 3, ctypes.c_double, ctypes.c_int)
READFLOATFUNCTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(udSDK.udPointBufferF64._udPointBufferF64))
CLOSEFUNCTYPE = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
DESTROYFUNCTYPE = ctypes.CFUNCTYPE(None, ctypes.c_void_p)


def passFCN(*args):
    """
    Default callback performing no operation
    """
    return 0


class UserData(ctypes.Structure):
    """
    Default user data struct containing the number of points written during a conversion
    """
    _fields_ = [("pointCount", ctypes.c_uint32)]


class udConvertCustomItem(ctypes.Structure):
    """
    Class representing a filetype that can be read by udConvert. See samples/custom_convert for example usage
    """
    _fields_ = [
        ("pOpen", OPENFUNCTYPE),
        ("pReadPointsFloat", READFLOATFUNCTYPE),
        ("pDestroy", DESTROYFUNCTYPE),
        ("pClose", CLOSEFUNCTYPE),
        ("pData", ctypes.c_void_p), #!< Private user data relevant to the specific geomtype, must be freed by the pClose function

        ("pName", ctypes.c_char_p), #!< Filename or other identifier
        ("boundMin", ctypes.c_double*3),#!< Optional (see boundsKnown) source space minimum values
        ("boundMax", ctypes.c_double*3),#!< Optional (see boundsKnown) source space maximum values
        ("sourceResolution", ctypes.c_double),  #!< Source resolution (eg 0.01 if points are 1cm apart). 0 indicates unknown
        ("pointCount", ctypes.c_int64), #!< Number of points coming, -1 if unknown
        ("srid", ctypes.c_int32),  #!< If non-zero, this input is considered to be within the given srid code (useful mainly as a default value for other files in the conversion)
        ("attributes", udAttributeSet), #!< Content of the input; this might not match the output
        ("boundsKnown", ctypes.c_uint32), #!< If not 0, boundMin and boundMax are valid, if 0 they will be calculated later
        ("pointCountIsEstimate", ctypes.c_uint32) #!< If not 0, the point count is an estimate and may be different
    ]

    def __init(self):
        super.__init__()
        self.open = passFCN
        self.close = passFCN
        self.destroy = passFCN
        self.read_points_float = passFCN
        self.userData = UserData()
        self.userData.pointCount = 0

    @property
    def open(self):
        """
        Function called prior to reading the points. Can be used to open file streams and initialise variables
        for the reading process prior to beginning

        function must return a udError indicating the success of opening the file, and accept as arguments
        - a pointer to (this) udConvertCustomItem
        - uint32_t everyNth,
        - double pointResolution
        - udConvertCustomItemFlags flags
        """
        return self._open
    @open.setter
    def open(self, fcn):
        self._open = fcn
        self.pOpen = OPENFUNCTYPE(self._open)

    @property
    def close(self):
        """
        Function called on closing the file. Must accept a pointer to (this) udCustomConvertItem as an argument
        """
        return self._close
    @close.setter
    def close(self, fcn):
        self._close = fcn
        self.pClose = CLOSEFUNCTYPE(self._close)

    @property
    def read_points_float(self):
        """
        Function to perform the point reading operation. returns a udError to indicate success of the operation.
        Must accept as arguments:
        - a pointer to (this) udConvertCustomItem
        - a pointer to a udPointBufferF64 to which the points will be written

        This function will be called after open repeatedly by the convert process until:
        - The the pointbuffer has a point count of 0 on exit from this function
        - a udError not equal to udSuccess is returned, causing the convert process to fail
        """
        return self._read_points_float

    @read_points_float.setter
    def read_points_float(self, fcn):
        self._read_points_float = fcn
        self.pReadPointsFloat = READFLOATFUNCTYPE(self._read_points_float)

    @property
    def destroy(self):
        """
        Function called on finishing the item. Must accept a pointer to (this) udCustomConvertItem as an argument
        """
        return self._destroy
    @destroy.setter
    def destroy(self, fcn):
        self._destroy = fcn
        self.pClose = DESTROYFUNCTYPE(self._destroy)

    @property
    def userData(self):
        """
        User data struct stored inside this object and passed to the callback functions. Used to store the conversion
        state between calls to the various callbacks.
        """
        return ctypes.cast(ctypes.pointer(self.pData), ctypes.POINTER(self._userDataType)).contents

    @userData.setter
    def userData(self, val):
        self._userDataType = val.__class__
        self._userData = val
        self.pData = ctypes.cast(ctypes.pointer(self._userData), ctypes.c_void_p)

