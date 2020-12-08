from ctypes import *
import udSDK
from udSDK import _HandleReturnValue
from enum import IntEnum, unique
import requests
from pathlib import Path


class udProjectLoadSource(IntEnum):
    udProjectLoadSource_Memory = 0  # !< The project source exists in memory; udProject_CreateInMemory = udProject_LoadFromMemory or udProject_SaveToMemory
    udProjectLoadSource_Server = 1  # !< The project source exists from the server; udProject_CreateInServer = udProject_LoadFromServer or udProject_SaveToServer
    udProjectLoadSource_URI = 2  # !< The project source exists from a file or URL; udProject_CreateInFile = udProject_LoadFromFile or udProject_SaveToFile

    udProjectLoadSource_Count = 3  # !< Total number of source types. Used internally but can be used as an iterator max when displaying different source types.


class udProjectGeometryType(IntEnum):
    udPGT_None = 0  # !< There is no geometry associated with this node

    udPGT_Point = 1  # !< pCoordinates is a single 3D position
    udPGT_MultiPoint = 2  # !< Array of udPGT_Point, pCoordinates is an array of 3D positions
    udPGT_LineString = 3  # !< pCoordinates is an array of 3D positions forming an open line
    udPGT_MultiLineString = 4  # !< Array of udPGT_LineString; pCoordinates is NULL and children will be present
    udPGT_Polygon = 5  # !< pCoordinates will be a closed linear ring (the outside), there MAY be children that are interior as pChildren udPGT_MultiLineString items, these should be counted as islands of the external ring.
    udPGT_MultiPolygon = 6  # !< pCoordinates is null, children will be udPGT_Polygon (which still may have internal islands)
    udPGT_GeometryCollection = 7  # !< Array of geometries; pCoordinates is NULL and children may be present of any type

    udPGT_Count = 8  # !< Total number of geometry types. Used internally but can be used as an iterator max when displaying different type modes.

    udPGT_Internal = 9  # !< Used internally when calculating other types. Do not use.


class udProjectNodeType(IntEnum):
    udPNT_Custom = 0  # !< Need to check the itemtypeStr string manually

    udPNT_PointCloud = 1  # !< A Euclideon Unlimited Detail Point Cloud file ("UDS")
    udPNT_PointOfInterest = 2  # !< A point, line or region describing a location of interest ("POI")
    udPNT_Folder = 3  # !< A folder of other nodes ("Folder")
    udPNT_LiveFeed = 4  # !< A Euclideon udServer live feed container ("IOT")
    udPNT_Media = 5  # !< An Image, Movie, Audio file or other media object ("Media")
    udPNT_Viewpoint = 6  # !< An Camera Location & Orientation ("Camera")
    udPNT_VisualisationSettings = 7  # !< Visualisation settings (itensity, map height etc) ("VizSet")
    udPNT_I3S = 8  # !< An Indexed 3d Scene Layer (I3S) or Scene Layer Package (SLPK) dataset ("I3S")
    udPNT_Water = 9  # !< A region describing the location of a body of water ("Water")
    udPNT_ViewShed = 10  # !< A point describing where to generate a view shed from ("ViewMap")
    udPNT_Polygon = 11  # !< A polygon model, usually an OBJ or FBX ("Polygon")
    udPNT_QueryFilter = 12  # !< A query filter to be applied to all PointCloud types in the scene ("QFilter")
    udPNT_Places = 13  # !< A collection of places that can be grouped together at a distance ("Places")
    udPNT_HeightMeasurement = 14  # !< A height measurement object ("MHeight")
    udPNT_Count = 15  # !< Total number of node types. Used internally but can be used as an iterator max when displaying different type modes.

class udProjectNodeDUMMY(Structure):
    pass
class udProjectNode(Structure):
    _fields_ = \
        [
            # Node header data
            ("isVisible", c_int),  # !< Non-zero if the node is visible and should be drawn in the scene
            ("UUID", (c_char * 37)),  # !< Unique identifier for this node "id"
            ("lastUpdate", c_double),  # !< The last time this node was updated in UTC

            ("itemtype", c_int),  # !< The type of this node, see udProjectNodeType for more information
            # !< The string representing the type of node. If its a known type during node creation `itemtype` will
            # be set to something other than udPNT_Custom
            ("itemtypeStr", (c_char * 8)),

            ("pName", c_char_p),  # !< Human readable name of the item
            ("pURI", c_char_p),  # !< The address or filename that the resource can be found.

            ("hasBoundingBox", c_uint32),  # !< Set to not 0 if this nodes boundingBox item is filled out
            # !< The bounds of this model, ordered as [West, South, Floor, East, North, Ceiling]
            ("boundingBox", (c_double * 6)),

            # Geometry Info
            ("geomtype", c_int),
            # !< Indicates what geometry can be found in this model. See the udProjectGeometryType documentation for more information.
            ("geomCount", c_uint32),  # !< How many geometry items can be found on this model
            ("pCoordinates", POINTER(c_double)),
            # !< The positions of the geometry of this node (NULL this this node doesn't have points). The format is [X0,Y0,Z0,...Xn,Yn,Zn]

            # Next nodes
            ("pNextSibling", POINTER(udProjectNodeDUMMY)),
            # !< This is the next item in the project (NULL if no further siblings)
            ("pFirstChild", POINTER(udProjectNodeDUMMY)),
            # !< Some types ("folder", "collection", "polygon"...) have children nodes, NULL if there are no children.

            # Node Data
            ("pUserData", c_void_p),
            # !< This is application specific user data. The application should traverse the tree to release these before releasing the udProject
            ("pInternalData", c_void_p),  # !< Internal udSDK specific state for this node
        ]
    _project = None
    parent = None
    fileList = None
    firstChild = None
    nextSibling = None

    def __init__(self, parent=None):
        #super().__init__()
        self.parent = parent
        self._udProjectNode_Create = getattr(udSDK.udSDKlib, "udProjectNode_Create")
        self._udProjectNode_MoveChild = getattr(udSDK.udSDKlib, "udProjectNode_MoveChild")
        self._udProjectNode_RemoveChild = getattr(udSDK.udSDKlib, "udProjectNode_RemoveChild")
        self._udProjectNode_SetName = getattr(udSDK.udSDKlib, "udProjectNode_SetName")
        self._udProjectNode_SetVisibility = getattr(udSDK.udSDKlib, "udProjectNode_SetVisibility")
        self._udProjectNode_SetURI = getattr(udSDK.udSDKlib, "udProjectNode_SetURI")
        self._udProjectNode_SetGeometry = getattr(udSDK.udSDKlib, "udProjectNode_SetGeometry")
        self._udProjectNode_GetMetadataInt = getattr(udSDK.udSDKlib, "udProjectNode_GetMetadataInt")
        self._udProjectNode_SetMetadataInt = getattr(udSDK.udSDKlib, "udProjectNode_SetMetadataInt")
        self._udProjectNode_GetMetadataUint = getattr(udSDK.udSDKlib, "udProjectNode_GetMetadataUint")
        self._udProjectNode_SetMetadataUint = getattr(udSDK.udSDKlib, "udProjectNode_SetMetadataUint")
        self._udProjectNode_GetMetadataInt64 = getattr(udSDK.udSDKlib, "udProjectNode_GetMetadataInt64")
        self._udProjectNode_SetMetadataInt64 = getattr(udSDK.udSDKlib, "udProjectNode_SetMetadataInt64")
        self._udProjectNode_GetMetadataDouble = getattr(udSDK.udSDKlib, "udProjectNode_GetMetadataDouble")
        self._udProjectNode_SetMetadataDouble = getattr(udSDK.udSDKlib, "udProjectNode_SetMetadataDouble")
        self._udProjectNode_GetMetadataBool = getattr(udSDK.udSDKlib, "udProjectNode_GetMetadataBool")
        self._udProjectNode_SetMetadataBool = getattr(udSDK.udSDKlib, "udProjectNode_SetMetadataBool")
        self._udProjectNode_GetMetadataString = getattr(udSDK.udSDKlib, "udProjectNode_GetMetadataString")
        self._udProjectNode_SetMetadataString = getattr(udSDK.udSDKlib, "udProjectNode_SetMetadataString")
        self.initialised = True
        
        if(udProjectNodeType(self.itemType) == udProjectNodeType.udPNT_Places):
            self.__class__ = PlaceNode

    @property
    def project(self):
        """The udProject that the node is attached to,
        this recursively moves up the tree to the root node, returningg the project stored there
        """
        if self.parent is None:
            return self._project
        else:
            return self.parent.project


    def load_dependents(self):
        #if self.pFirstChild is not None:
        if self.pFirstChild and not self.firstChild:
            self.firstChild = cast(self.pFirstChild, POINTER(udProjectNode)).contents
            self.firstChild.__init__(parent=self)
            self.firstChild.load_dependents()
        if self.pNextSibling and not self.nextSibling:
            self.nextSibling = cast(self.pNextSibling, POINTER(udProjectNode)).contents
            self.nextSibling.__init__(parent=self.parent)
            self.nextSibling.load_dependents()
        if self.pURI is not None:
            pass
            #self.add_file_to_list(self.pURI)

    def add_file_to_list(self, uri):
        if self.fileList is None:
            self.parent.add_file_to_list(uri)
        else:
            self.fileList.append(uri)

    def create_child(self, type:str, name:str, uri="", pUserData=None):
        self.load_dependents()
        if not self.firstChild:
            _HandleReturnValue(self._udProjectNode_Create(self.project.pProject, byref(self.pFirstChild), byref(self), type.encode('utf8'), name.encode('utf8'), uri.encode('utf8'), c_void_p(0)))
            self.load_dependents()
            assert self.firstChild is not None
            return self.firstChild
        else:
            return self.firstChild.create_sibling(type, name, uri, pUserData)

    def create_sibling(self, type:str, name:str, uri="", pUserData=None):
        self.load_dependents()
        if not self.nextSibling:
            _HandleReturnValue(self._udProjectNode_Create(self.project.pProject, byref(self.pNextSibling), byref(self.parent), type.encode('utf8'), name.encode('utf8'), uri.encode('utf8'), c_void_p(0)))
            self.load_dependents()
            assert self.nextSibling is not None
            return self.nextSibling
        else:
            return self.nextSibling.create_sibling(type, name, uri, pUserData)

    def MoveChild(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProjectNode_MoveChild)

    def RemoveChild(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProjectNode_RemoveChild)

    def SetName(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProjectNode_SetName)

    def SetVisibility(self, val:bool):
        return _HandleReturnValue(self._udProjectNode_SetVisibility(self, c_bool(val)))

    def set_uri(self, uri: str):
        _HandleReturnValue(self._udProjectNode_SetURI(self.project.pProject, byref(self), uri.encode('utf8')))
        return

    def SetGeometry(self, geometryType:udProjectGeometryType, coordinates):
        arrType = (c_double * len(coordinates))
        count = int(len(coordinates)//3)
        assert not len(coordinates) % 3, "coordinate list length must be a multiple of 3"
        arr = arrType(*coordinates)
        _HandleReturnValue(self._udProjectNode_SetGeometry(self.project.pProject, byref(self), int(geometryType), count, byref(arr)))

    def GetMetadataInt(self, key:str, defaultValue=int(0)):
        ret = c_int32(defaultValue)
        _HandleReturnValue(self._udProjectNode_GetMetadataInt(self.project.pProject, key.encode("utf8"), byref(ret), ret))
        return ret

    def SetMetadataInt(self, key:str, value:int):
        return _HandleReturnValue(self._udProjectNode_SetMetadataInt(byref(self), key.encode('utf8'), c_int32(value)))

    def GetMetadataUint(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProjectNode_GetMetadataUint)

    def SetMetadataUint(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProjectNode_SetMetadataUint)

    def GetMetadataInt64(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProjectNode_GetMetadataInt64)

    def SetMetadataInt64(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProjectNode_SetMetadataInt64)

    def GetMetadataDouble(self, key:str, defaultValue=float(0)):
        ret = c_double(defaultValue)
        _HandleReturnValue(self._udProjectNode_GetMetadataDouble(self.project.pProject, key.encode("utf8"), byref(ret), ret))
        return ret

    def SetMetadataDouble(self, key:str, value:float):
        raise NotImplementedError
        return _HandleReturnValue(self._udProjectNode_SetMetadataDouble(byref(self), key.encode('utf8'), c_double(value)))

    def GetMetadataBool(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProjectNode_GetMetadataBool)

    def SetMetadataBool(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProjectNode_SetMetadataBool)

    def GetMetadataString(self, key:str, defaultValue=""):
        ret = c_char_p()
        _HandleReturnValue(self._udProjectNode_GetMetadataString(self.project.pProject, key.encode("utf8"), byref(ret), defaultValue.encode('utf8')))
        return ret


    def SetMetadataString(self, key:str, value:str):
        return _HandleReturnValue(self._udProjectNode_SetMetadataString(byref(self), key.encode('utf8'), value.encode('utf8')))


class udProject():
    def __init__(self, context: udSDK.udContext):
        self._udProject_CreateInMemory = getattr(udSDK.udSDKlib, "udProject_CreateInMemory")
        self._udProject_CreateInFile = getattr(udSDK.udSDKlib, "udProject_CreateInFile")
        self._udProject_CreateInServer = getattr(udSDK.udSDKlib, "udProject_CreateInServer")
        self._udProject_LoadFromServer = getattr(udSDK.udSDKlib, "udProject_LoadFromServer")
        self._udProject_LoadFromMemory = getattr(udSDK.udSDKlib, "udProject_LoadFromMemory")
        self._udProject_LoadFromFile = getattr(udSDK.udSDKlib, "udProject_LoadFromFile")
        self._udProject_Release = getattr(udSDK.udSDKlib, "udProject_Release")
        self._udProject_Save = getattr(udSDK.udSDKlib, "udProject_Save")
        self._udProject_SaveToMemory = getattr(udSDK.udSDKlib, "udProject_SaveToMemory")
        self._udProject_SaveToServer = getattr(udSDK.udSDKlib, "udProject_SaveToServer")
        self._udProject_SaveToFile = getattr(udSDK.udSDKlib, "udProject_SaveToFile")
        self._udProject_GetProjectRoot = getattr(udSDK.udSDKlib, "udProject_GetProjectRoot")
        self._udProject_GetProjectUUID = getattr(udSDK.udSDKlib, "udProject_GetProjectUUID")
        self._udProject_HasUnsavedChanges = getattr(udSDK.udSDKlib, "udProject_HasUnsavedChanges")
        self._udProject_GetLoadSource = getattr(udSDK.udSDKlib, "udProject_GetLoadSource")
        self._udProject_GetTypeName = getattr(udSDK.udSDKlib, "udProject_GetTypeName")
        self._udProject_DeleteServerProject = getattr(udSDK.udSDKlib, "udProject_DeleteServerProject")
        self._udProject_SetLinkShareStatus = getattr(udSDK.udSDKlib, "udProject_SetLinkShareStatus")

        self._udContext = context
        self.pProject = c_void_p(0)
        self.rootNode = udProjectNode()
        self.uuid = ""

    def CreateInMemory(self, name:str):
        return _HandleReturnValue(self._udProject_CreateInMemory(self._udContext.pContext, byref(self.pProject),name.encode('utf8')))

    def CreateInFile(self, name:str, filename:str):
        return _HandleReturnValue(self._udProject_CreateInFile(self._udContext.pContext, byref(self.pProject), name.encode('utf8'), filename.encode('utf8')))

    def CreateInServer(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProject_CreateInServer)

    def LoadFromServer(self, uuid: str):
        self.uuid = uuid
        return _HandleReturnValue(
            self._udProject_LoadFromServer(self._udContext.pContext, byref(self.pProject), uuid.encode('utf8')))

    def LoadFromMemory(self, geoJSON: str):
        _HandleReturnValue(self._udProject_LoadFromMemory(self._udContext.pContext, byref(self.pProject), geoJSON.encode('utf8')))
        return

    def LoadFromFile(self, filename: str):
        self.filename = filename
        _HandleReturnValue(self._udProject_LoadFromFile(self._udContext.pContext, byref(self.pProject), filename.encode('utf8')))
        return

    def Release(self):
        _HandleReturnValue(self._udProject_Release(byref(self.pProject)))
        return

    def Save(self):
        return _HandleReturnValue(self._udProject_Save(self.pProject))

    def SaveToMemory(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProject_SaveToMemory)

    def SaveToServer(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProject_SaveToServer)

    def SaveToFile(self, filename: str):
        _HandleReturnValue(self._udProject_SaveToFile(self._udContext.pContext, self.pProject, filename.encode('utf8')))
        self.filename = filename
        self.uuid = ""
        return

    def GetProjectRoot(self):
        if (self.pProject == c_void_p(0)):
            raise Exception("Project not loaded")
        a = pointer(udProjectNode())
        _HandleReturnValue(self._udProject_GetProjectRoot(self.pProject, byref(a)))
        self.rootNode = a.contents
        self.rootNode.__init__()
        self.rootNode.fileList = []
        self.rootNode._project = self
        self.rootNode.load_dependents()
        return self.rootNode

    def GetProjectUUID(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProject_GetProjectUUID)

    def HasUnsavedChanges(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProject_HasUnsavedChanges)

    def GetLoadSource(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProject_GetLoadSource)

    def GetTypeName(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProject_GetTypeName)

    def DeleteServerProject(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProject_DeleteServerProject)

    def SetLinkShareStatus(self):
        raise NotImplementedError
        return _HandleReturnValue(self._udProject_SetLinkShareStatus)

    def __del__(self):
        self.Release()

class PlaceNode(udProjectNode):
    """
    Project node with the type of place, this is more efficient than a standard POI
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.model = self.Model(self)

    @property
    def pin(self):
        return self.GetMetadataString("pin")
    @pin.setter
    def pin(self, newVal:str):
        self.SetMetadataString("pin", newVal)

    @property
    def pinDistance(self):
        return self.GetMetadataDouble("pinDistance")
    @pinDistance.setter
    def pinDistance(self, newVal:float):
        self.SetMetadataDouble("pinDistance", newVal)

    @property
    def labelDistance(self):
        return self.GetMetadataDouble("labelDistance")
    @labelDistance.setter
    def labelDistance(self, newVal:float):
        self.SetMetadataDouble("labelDistance", newVal)

    class Model():
        def __init__(self, parent:udProjectNode):
            self.parent = parent
        @property
        def url(self):
            return self.parent.GetMetadataString("modelURL")
        @url.setter
        def url(self, val:str):
            self.parent.SetMetadataString("modelURL", val)

        @property
        def offset(self):
            return (
            self.parent.GetMetadataDouble("modelTransform.offset.x"),
            self.parent.GetMetadataDouble("modelTransform.offset.y"),
            self.parent.GetMetadataDouble("modelTransform.offset.z"),
            )
        @offset.setter
        def offset(self, val):
            self.parent.SetMetadataDouble("modelTransform.offset.x", val[0])
            self.parent.SetMetadataDouble("modelTransform.offset.y", val[1])
            self.parent.SetMetadataDouble("modelTransform.offset.z", val[2])

        @property
        def rotation(self):
            return (
            self.parent.GetMetadataDouble("modelTransform.rotation.x"),
            self.parent.GetMetadataDouble("modelTransform.rotation.y"),
            self.parent.GetMetadataDouble("modelTransform.rotation.z"),
            )
        @rotation.setter
        def rotation(self, val):
            self.parent.SetMetadataDouble("modelTransform.rotation.x", val[0])
            self.parent.SetMetadataDouble("modelTransform.rotation.y", val[1])
            self.parent.SetMetadataDouble("modelTransform.rotation.z", val[2])

        @property
        def scale(self):
            return (
            self.parent.GetMetadataDouble("modelTransform.scale.x"),
            self.parent.GetMetadataDouble("modelTransform.scale.y"),
            self.parent.GetMetadataDouble("modelTransform.scale.z"),
            )
        @scale.setter
        def scale(self, val):
            self.parent.SetMetadataDouble("modelTransform.scale.x", val[0])
            self.parent.SetMetadataDouble("modelTransform.scale.y", val[1])
            self.parent.SetMetadataDouble("modelTransform.scale.z", val[2])




