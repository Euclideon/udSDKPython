import ctypes
import os
from enum import IntEnum

import udSDK
import udSDKGeometry
from udSDK import _HandleReturnValue


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
    udPNT_Media = 4  # !< An Image, Movie, Audio file or other media object ("Media")
    udPNT_Viewpoint = 5  # !< An Camera Location & Orientation ("Camera")
    udPNT_VisualisationSettings = 6  # !< Visualisation settings (itensity, map height etc) ("VizSet")
    udPNT_I3S = 7  # !< An Indexed 3d Scene Layer (I3S) or Scene Layer Package (SLPK) dataset ("I3S")
    udPNT_Water = 8  # !< A region describing the location of a body of water ("Water")
    udPNT_ViewShed = 9  # !< A point describing where to generate a view shed from ("ViewMap")
    udPNT_Polygon = 10  # !< A polygon model, usually an OBJ or FBX ("Polygon")
    udPNT_QueryFilter = 11  # !< A query filter to be applied to all PointCloud types in the scene ("QFilter")
    udPNT_Places = 12  # !< A collection of places that can be grouped together at a distance ("Places")
    udPNT_HeightMeasurement = 13  # !< A height measurement object ("MHeight")
    udPNT_LassoNode = 14 #, //!< A Lasso Selection Folder ("LNode")
    udPNT_QueryGroup = 15 #, //!< A Group of Query node being represented as one node ("QGroup")
    udPNT_Count = 16  # !< Total number of node types. Used internally but can be used as an iterator max when displaying different type modes.

class udCameraPosition(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_double),
        ('y', ctypes.c_double),
        ('z', ctypes.c_double),
        ('heading', ctypes.c_double),
        ('pitch', ctypes.c_double),
    ]

class udSelectedNode(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_char * 37)
    ]

class udAvatarInfo(ctypes.Structure):
    _fields_ = [
        ("pURL", ctypes.c_char_p),
        ("offsetX", ctypes.c_double),
        ("offsetY", ctypes.c_double),
        ("offsetZ", ctypes.c_double),
        ("scaleX", ctypes.c_double),
        ("scaleY", ctypes.c_double),
        ("scaleZ", ctypes.c_double),
        ("yaw", ctypes.c_double),
        ("pitch", ctypes.c_double),
        ("roll", ctypes.c_double),
    ]

class udMessage(ctypes.Structure):
    _fields = [
        ("pMessageType", ctypes.c_char_p),
        ("pMessagePayload", ctypes.c_char_p),
        ("pTargetSessionID", ctypes.c_char_p),
        ("pReceivedFromSessionID", ctypes.c_char_p),
    ]

class udUserPosition(ctypes.Structure):
    _fields_ = [
        ("username", ctypes.c_char_p),
        ("ID", ctypes.c_char_p),
        ("pProjectSessionID", ctypes.c_char_p),
        ("lastUpdated", ctypes.c_double),
        ("selectedNodesCount", ctypes.c_uint32),
        ("selectedNodesList", ctypes.POINTER(udSelectedNode)),
        ("udCameraPosition", ctypes.POINTER(udCameraPosition)),
        ("udAvatarInfo", udAvatarInfo),
    ]

class udProjectUpdateInfo(ctypes.Structure):
    _fields_ = [
        ("forceSync", ctypes.c_uint32),
        ("udCameraPositions", ctypes.POINTER(udCameraPosition)),
        ("count", ctypes.c_uint32),

        ("pUserList", ctypes.POINTER(udUserPosition)),
        ("usersCount", ctypes.c_uint32),

        ("pSelectedNodesList", ctypes.POINTER(udSelectedNode)),
        ("selectedNodesCount", ctypes.c_uint32),
        ("avatar", udAvatarInfo),

        ("pReceivedMessages", ctypes.POINTER(udMessage)),
        ("receivedMessagesCount", ctypes.c_uint32),
    ]

class udProjectNode(ctypes.Structure):
    fileList = None
    def __init__(self, project):
        self.project = project
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

        # handle place layers specially as they are encoded differently:
        if(udProjectNodeType(self.itemtype) == udProjectNodeType.udPNT_Places):
            self.__class__ = PlaceLayerNode
            self.on_cast()

        self.children = self._Children(self)

    @property
    def uri(self):
        if self.pURI is not None:
            # remove windows \\ nonsense
            return self.pURI.decode('utf8').replace('\\','/')
        else:
            return None
    @uri.setter
    def uri(self, new):
        self._set_uri(new)

    @property
    def parent(self):
        return self.from_pointer(self.pParent)


    @property
    def coordinates(self):
        if self.pCoordinates is None:
            return []
        return [(self.pCoordinates[3*i], self.pCoordinates[3*i+1], self.pCoordinates[3*i+2] ) for i in range(self.geomCount)]

    @coordinates.setter
    def coordinates(self, coords):
        self.SetGeometry(udProjectGeometryType.udPGT_Point, coordinates=coords)

    def from_pointer(self, pointer, project=None):
        if project is None:
            project = self.project
        if pointer:
            a = pointer.contents
            a.__init__(project)
            return a
        else:
            return None

    @property
    def name(self):
        return self.pName.decode('utf8')

    @name.setter
    def name(self, newval:str):
        self._set_name(newval)

    @property
    def firstChild(self):
        return self.from_pointer(self.pFirstChild)

    @property
    def nextSibling(self):
        if self.parent is not None:
            return self.parent.child_from_pointer(self.pNextSibling)
        else:
            return None

    def add_file_to_list(self, uri):
        if self.fileList is None:
            self.parent.add_file_to_list(uri)
        else:
            self.fileList.append(uri)

    def create_child(self, type:str, name:str, uri="", pUserData=None):
        if self.firstChild is None:
            _HandleReturnValue(self._udProjectNode_Create(self.project.pProject, None, ctypes.byref(self), type.encode('utf8'), name.encode('utf8'), uri.encode('utf8'), ctypes.c_void_p(0)))
            assert self.firstChild is not None
            return self.firstChild
        else:
            return self.firstChild.create_sibling(type, name, uri, pUserData)

    def create_sibling(self, type:str, name:str, uri="", pUserData=None):
        if self.nextSibling is None:
            _HandleReturnValue(self._udProjectNode_Create(self.project.pProject, None, ctypes.byref(self.parent), type.encode('utf8'), name.encode('utf8'), uri.encode('utf8'), ctypes.c_void_p(0)))
            assert self.nextSibling is not None
            return self.nextSibling
        else:
            return self.nextSibling.create_sibling(type, name, uri, pUserData)

    @property
    def boundingBox(self):
        if self.hasBoundingBox:
            return [self._boundingBox[i] for i in range(6)]
        else:
            return None

    @boundingBox.setter
    def boundingBox(self, boundingBox):
        assert len(boundingBox) == 6, "boundingBox list length must be 6"
        arrType = (ctypes.c_double * len(boundingBox))
        arr = arrType(*boundingBox)
        _HandleReturnValue(self._udProjectNode_SetBoundingBox(self.project.pProject, ctypes.byref(self), arr))
        return

    def to_ud_type(self):
        """
        returns an instance of the corresponding UDSDK type (if implemented)
        """
        context = self.project._udContext
        if self.itemtypeStr == b'QFilter':
            shape = self.GetMetadataString("shape")
            position = self.coordinates[0]
            size =[self.GetMetadataDouble(f"size.{a}") for a in 'xyz']
            ypr =[self.GetMetadataDouble(f"transform.rotation.{a}") for a in 'ypr']
            halfheight = self.GetMetadataDouble("size.y")
            radius = self.GetMetadataDouble("size.x")
            if shape == "box":
                ret = udSDKGeometry.udGeometryOBB(position, size, ypr)
            elif shape == "sphere":
                raise NotImplementedError()
            elif shape == "cylinder":
                raise NotImplementedError()
            else:
                raise NotImplementedError(f"filtertype {shape} not supported")
            return ret
        elif self.itemtypeStr == b"UDS":
            # this should really return a udRenderInstance with the metadata read from the node
            if context is None:
                raise Exception("project context not set")
            model = udSDK.udPointCloud(path=self.uri, context=context)
            modelGeoPosition = model.header.storedMatrix[12:15]
            return model
        else:
            raise NotImplementedError(f"itemtype {self.itemtypeStr} not supported")

    def move(self, newParent=None, beforeSibling = None):
        """
        Moves the node to be the child of newParent (None to retain current parent)
        beforeSibling may be an existing child of new parent or an index representing then nth child, None to move to end
        """
        pCurrentParent = ctypes.byref(self.parent)
        if newParent is None:
            pNewParent = pCurrentParent
            newParent = self.parent
        else:
            pNewParent = ctypes.byref(newParent)

        if beforeSibling is None:
            pBeforeSibling = ctypes.c_void_p(0)
        elif type(beforeSibling) == int:
            beforeSibling = newParent.children[beforeSibling]
            pBeforeSibling = ctypes.byref(beforeSibling)
        elif type(beforeSibling) == udProjectNode:
            pBeforeSibling = ctypes.byref(beforeSibling)
        else:
            raise TypeError(f"Unsupported sibling type ({type(beforeSibling)}): must be integer, udProjectNode or None")

        _HandleReturnValue(self._udProjectNode_MoveChild(self.project.pProject, pCurrentParent, pNewParent, ctypes.byref(self), pBeforeSibling))

    def remove(self):
        _HandleReturnValue(self._udProjectNode_RemoveChild(self.project.pProject, ctypes.byref(self.parent), ))

    def _set_name(self, newName:str):
        return _HandleReturnValue(self._udProjectNode_SetName(self.project.pProject, ctypes.byref(self), newName.encode('utf8')))

    @property
    def visibility(self):
        return self._isVisible

    @visibility.setter
    def visibility(self, val:bool):
        _HandleReturnValue(self._udProjectNode_SetVisibility(self, ctypes.c_bool(val)))

    def _set_uri(self, uri: str):
        _HandleReturnValue(self._udProjectNode_SetURI(self.project.pProject, ctypes.byref(self), uri.encode('utf8')))


    def SetGeometry(self, geometryType:udProjectGeometryType, coordinates):
        arrType = (ctypes.c_double * len(coordinates))
        count = int(len(coordinates)//3)
        assert not len(coordinates) % 3, "coordinate list length must be a multiple of 3"
        arr = arrType(*coordinates)
        _HandleReturnValue(self._udProjectNode_SetGeometry(self.project.pProject, ctypes.byref(self), int(geometryType), count, ctypes.byref(arr)))

    def GetMetadataInt(self, key:str, defaultValue=int(0)):
        ret = ctypes.c_int32(defaultValue)
        success = (self._udProjectNode_GetMetadataInt(ctypes.byref(self), key.encode("utf8"), ctypes.byref(ret), ctypes.c_int32(defaultValue)))
        if success != udSDK.udError.NotFound:
            _HandleReturnValue(success)
            return ret.value
        else:
            return defaultValue

    def SetMetadataInt(self, key:str, value:int):
        _HandleReturnValue(self._udProjectNode_SetMetadataInt(ctypes.byref(self), key.encode('utf8'), ctypes.c_int32(value)))

    def GetMetadataUint(self, key :str, defaultValue):
        ret = ctypes.c_uint32(defaultValue)
        success = (self._udProjectNode_GetMetadataUInt(ctypes.byref(self), key.encode("utf8"), ctypes.byref(ret), ctypes.c_int32(defaultValue)))
        if success != udSDK.udError.NotFound:
            _HandleReturnValue(success)
            return ret.value
        else:
            return defaultValue

    def SetMetadataUint(self, key:str, value):
        _HandleReturnValue(self._udProjectNode_SetMetadataUInt(ctypes.byref(self), key.encode('utf8'), ctypes.c_uint32(value)))

    def GetMetadataInt64(self, key:str, defaultValue):
        ret = ctypes.c_int64(defaultValue)
        success = (self._udProjectNode_GetMetadataInt64(ctypes.byref(self), key.encode("utf8"), ctypes.byref(ret), ctypes.c_int32(defaultValue)))
        if success != udSDK.udError.NotFound:
            _HandleReturnValue(success)
            return ret.value
        else:
            return defaultValue

    def SetMetadataInt64(self, key, value):
        _HandleReturnValue(self._udProjectNode_SetMetadataInt64(ctypes.byref(self), key.encode('utf8'), ctypes.c_int64(value)))

    def GetMetadataDouble(self, key:str, defaultValue=float(0)):
        ret = ctypes.c_double(0)
        success = (self._udProjectNode_GetMetadataDouble(ctypes.byref(self), key.encode("utf8"), ctypes.byref(ret), ctypes.c_double(defaultValue)))
        if success != udSDK.udError.NotFound:
            _HandleReturnValue(success)
            return ret.value
        else:
            return defaultValue


    def SetMetadataDouble(self, key:str, value:float):
        _HandleReturnValue(self._udProjectNode_SetMetadataDouble(ctypes.byref(self), key.encode('utf8'), ctypes.c_double(value)))

    def GetMetadataBool(self, key:str, defaultValue = ctypes.c_uint32(False)):
        ret = ctypes.c_uint32(0)
        success = (self._udProjectNode_GetMetadataBool(ctypes.byref(self), key.encode("utf8"), ctypes.byref(ret), ctypes.c_double(defaultValue)))
        if success != udSDK.udError.NotFound:
            _HandleReturnValue(success)
            return bool(ret.value)
        else:
            return bool(defaultValue)

    def SetMetadataBool(self, key, value):
        _HandleReturnValue(self._udProjectNode_SetMetadataDouble(ctypes.byref(self), key.encode('utf8'), ctypes.c_uint32(value)))

    def GetMetadataString(self, key:str, defaultValue=None):
        ret = ctypes.c_char_p(0)
        success = self._udProjectNode_GetMetadataString(self, key.encode("utf8"), ctypes.byref(ret), "")
        if success != udSDK.udError.NotFound:
            _HandleReturnValue(success)
            return ret.value.decode('utf8')
        else:
            return defaultValue


    def SetMetadataString(self, key:str, value:str):
        _HandleReturnValue(self._udProjectNode_SetMetadataString(ctypes.byref(self), key.encode('utf8'), value.encode('utf8')))


    class _Children():
        """
        Iterator class for returning the children of a node
        """
        def __init__(self, node):
            self.node = node

        def __len__(self):
            counter = 0
            node = self.node.firstChild
            while True:
                if node is None:
                    break
                node = node.nextSibling
                counter += 1
            return counter

        def __iter__(self):
            self.currentNode = self.node.firstChild
            return self

        def __next__(self):
            n = self.currentNode
            if n is not None:
                self.currentNode = self.currentNode.nextSibling
                return n
            else:
                raise StopIteration

        def __getitem__(self, item):
            counter = 0
            node = self.node.firstChild
            if node is None:
                raise IndexError

            if item < 0:
                item = len(self) + item

            while counter < item:
                node = node.nextSibling
                counter += 1
                if node is None:
                    raise IndexError
            return node


udProjectNode._fields_ = \
    [
        # Node header data
        ("_isVisible", ctypes.c_int),  # !< Non-zero if the node is visible and should be drawn in the scene
        ("UUID", (ctypes.c_char * 37)),  # !< Unique identifier for this node "id"
        ("lastUpdate", ctypes.c_double),  # !< The last time this node was updated in UTC

        ("itemtype", ctypes.c_int),  # !< The type of this node, see udProjectNodeType for more information
        # !< The string representing the type of node. If its a known type during node creation `itemtype` will
        # be set to something other than udPNT_Custom
        ("itemtypeStr", (ctypes.c_char * 8)),

        ("pName", ctypes.c_char_p),  # !< Human readable name of the item
        ("pURI", ctypes.c_char_p),  # !< The address or filename that the resource can be found.

        ("hasBoundingBox", ctypes.c_uint32),  # !< Set to not 0 if this nodes boundingBox item is filled out
        # !< The bounds of this model, ordered as [West, South, Floor, East, North, Ceiling]
        ("_boundingBox", (ctypes.c_double * 6)),

        # Geometry Info
        ("geomtype", ctypes.c_int),
        # !< Indicates what geometry can be found in this model. See the udProjectGeometryType documentation for more information.
        ("geomCount", ctypes.c_uint32),  # !< How many geometry items can be found on this model
        ("pCoordinates", ctypes.POINTER(ctypes.c_double)),
        # !< The positions of the geometry of this node (NULL this this node doesn't have points). The format is [X0,Y0,Z0,...Xn,Yn,Zn]

        ("pParent", ctypes.POINTER(udProjectNode)),
        # Next nodes
        ("pNextSibling", ctypes.POINTER(udProjectNode)),
        # !< This is the next item in the project (NULL if no further siblings)
        ("pFirstChild", ctypes.POINTER(udProjectNode)),
        # !< Some types ("folder", "collection", "polygon"...) have children nodes, NULL if there are no children.

        # Node Data
        ("pUserDataCleanup", ctypes.c_void_p),
        ("pUserData", ctypes.c_void_p),
        # !< This is application specific user data. The application should traverse the tree to release these before releasing the udProject
        ("pInternalData", ctypes.c_void_p),  # !< Internal udSDK specific state for this node
    ]


class udProject():
    filename = None
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
        self._udProject_Update = udSDK.udExceptionDecorator(udSDK.udSDKlib.udProject_Update)
        self._udProject_GetSessionID = udSDK.udExceptionDecorator(udSDK.udSDKlib.udProject_GetSessionID)
        self._udProject_QueueMessage = udSDK.udExceptionDecorator(udSDK.udSDKlib.udProject_QueueMessage)
        self._udProject_SaveThumbnail = udSDK.udExceptionDecorator(udSDK.udSDKlib.udProject_SaveThumbnail)

        self._udContext = context
        self.pProject = ctypes.c_void_p(0)

    @property
    def rootNode(self):
        return self._get_project_root()

    def create_in_memory(self, name:str):
        _HandleReturnValue(self._udProject_CreateInMemory(self._udContext.pContext, ctypes.byref(self.pProject),name.encode('utf8')))

    def create_in_file(self, name:str, filename:str, override_if_exists=False):
        self.filename = filename
        if os.path.exists(filename):
            if override_if_exists:
                os.remove(filename)
            else:
                raise FileExistsError
        _HandleReturnValue(self._udProject_CreateInFile(self._udContext.pContext, ctypes.byref(self.pProject), name.encode('utf8'), filename.encode('utf8')))

    def create_in_server(self, name:str, groupID:str):
        _HandleReturnValue(self._udProject_CreateInServer(self._udContext.pContext, ctypes.byref(self.pProject), name.encode('utf8'), groupID.encode('utf8')))

    def load_from_server(self, uuid: str, groupID:str):
        self.filename = None
        return _HandleReturnValue(
            self._udProject_LoadFromServer(self._udContext.pContext, ctypes.byref(self.pProject), uuid.encode('utf8'), groupID.encode('utf8')))

    def load_from_memory(self, geoJSON: str):
        self.filename = None
        _HandleReturnValue(self._udProject_LoadFromMemory(self._udContext.pContext, ctypes.byref(self.pProject), geoJSON.encode('utf8')))
        return

    def load_from_file(self, filename: str):
        self.filename = filename.replace('\\\\','/')
        _HandleReturnValue(self._udProject_LoadFromFile(self._udContext.pContext, ctypes.byref(self.pProject), filename.encode('utf8')))

    def release(self):
        _HandleReturnValue(self._udProject_Release(ctypes.byref(self.pProject)))

    def save(self):
        _HandleReturnValue(self._udProject_Save(self.pProject))

    @property
    def geoJSON(self):
        """
        The current project as a GEOJSON string
        """
        ret = ctypes.c_char_p(0)
        _HandleReturnValue(self._udProject_SaveToMemory(self._udContext.pContext, self.pProject, ctypes.byref(ret)))
        return ret.value.decode('utf8')

    def save_to_server(self, groupID:str):
        _HandleReturnValue(self._udProject_SaveToServer(self._udContext.pContext, self.pProject, groupID.encode('utf8')))

    def save_to_file(self, filename: str):
        _HandleReturnValue(self._udProject_SaveToFile(self._udContext.pContext, self.pProject, filename.encode('utf8')))
        self.filename = filename

    def _get_project_root(self)->udProjectNode:
        if (self.pProject == ctypes.c_void_p(0)):
            raise Exception("Project not loaded")
        a = ctypes.pointer(udProjectNode())
        _HandleReturnValue(self._udProject_GetProjectRoot(self.pProject, ctypes.byref(a)))
        rootNode = a.contents
        rootNode.__init__(self)
        rootNode.fileList = []
        return rootNode

    def update(self):
        info = udProjectUpdateInfo()
        self._udProject_Update(self.pProject, info)
        return info

    @property
    def uuid(self):
        ret = ctypes.c_char_p(0)
        _HandleReturnValue(self._udProject_GetProjectUUID(self.pProject, ctypes.byref(ret)))
        return ret.value.decode('utf8')

    @property
    def hasUnsavedChanges(self):
        return self._udProject_HasUnsavedChanges(self.pProject) == udSDK.udError.Success

    @property
    def loadSource(self):
        source = ctypes.c_int
        _HandleReturnValue(self._udProject_GetLoadSource(self.pProject, ctypes.byref(source)))
        return udProjectLoadSource(source)

    def item_type_to_type_name(self, value:udProjectNodeType):
        ret = self._udProject_GetTypeName(value)
        if ret == ctypes.c_void_p:
            return None
        else:
            return ctypes.c_char_p(ret).value.decode('utf8')

    def delete_from_server(self, groupID:str):
        return _HandleReturnValue(self._udProject_DeleteServerProject(self._udContext.pContext, self.uuid.encode('utf8'), groupID.encode('utf8')))

    def set_link_share_status(self, sharableWithAnyoneWithLink:bool, groupID:str):
        return _HandleReturnValue(self._udProject_SetLinkShareStatus(self._udContext.pContext, self.uuid, sharableWithAnyoneWithLink, groupID.encode('utf8')))

    @property
    def sessionID(self):
        """
        The session ID (for server projects)
        """
        sessionID = ctypes.c_char_p(0)
        self._udProject_GetSessionID(self._udContext.pContext, ctypes.byref(sessionID))
        return sessionID.value.decode('utf8')

    def queue_message(self, messageType:str, messagePayload:str, targetSessionID=None):
        if targetSessionID is None:
            targetSessionID = self.sessionID
        self._udProject_QueueMessage(self.pProject, targetSessionID.encode('utf8'), messageType.encode('utf8'), messagePayload.encode('utf8'))

    def save_thumbnail(self, imageBase64):
        """
        Saves a project thumbnail in base64 to a udCloud server
        """
        self._udProject_SaveThumbnail(self.pProject, imageBase64)

    def __del__(self):
        self.release()



class ArrayLayerNode(udProjectNode):
    """
    Project node representing an array
    """
    _arrLength = None
    def __init__(self, parent, arrayItemType):
        super().__init__(parent)
        self.model = Model(self)
        self.arrayItemType = arrayItemType

    def __len__(self):
        self._arrLength = 0
        while self.arrayItemType(self, self._arrLength).name is not None:
            self._arrLength += 1
        return self._arrLength


    def add_item(self, name, coordinates, count):
        place = self.arrayItemType(self, len(self))
        place.count = count
        place.name = name
        place.coordinates = coordinates
        self._arrLength = len(self) +1
        #self.places.append(place)

    def on_cast(self):
        self.model = Model(self)

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


    def __getitem__(self, item):
        if item < 0:
            i = 0
            p = self.arrayItemType(self, i)
            if p.name is None:
                raise IndexError
            while p.name is not None:
                i += 1
                p = self.arrayItemType(self, i)
            item = i-item
        return self.arrayItemType(self, item)

    def __iter__(self):
        self.currentPlaceIndex = 0
        return self

    def __next__(self):
        p = self.arrayItemType(self, self.currentPlaceIndex)
        if p.name is not None:
            self.currentPlaceIndex = self.currentPlaceIndex + 1
            return p
        else:
            raise StopIteration

    class _Children():
        """
        Iterator class for returning the children of a node
        Instead of returning child nodes we iterate through the place array
        """
        def __init__(self, node:udProjectNode):
            self.node = node

class PlaceLayerNode(ArrayLayerNode):
    def __init__(self, parent):
        super().__init__(self, parent, Place)

    def on_cast(self):
        self.model = Model(self)
        self.arrayItemType = Place


class ProjectArrayItem():
    """
    Abstract class representing an item stored as an array in node metadata e.g. places
    """
    def __init__(self, parent:PlaceLayerNode, index:int, arrayName:str):
        self.parent = parent
        self.index = index
        self.arrayName = arrayName

    def get_property(self, name:str, type=float):
        if type==float:
            return self.parent.GetMetadataDouble(f"{self.arrayName}[{self.index}].{name}")
        if type=="int64":
            return self.parent.GetMetadataInt64(f"{self.arrayName}[{self.index}].{name}")
        if type==int:
            return self.parent.GetMetadataInt(f"{self.arrayName}[{self.index}].{name}")
        if type==bool:
            return self.parent.GetMetadataBool(f"{self.arrayName}[{self.index}].{name}")
        if type==str:
            return self.parent.GetMetadataString(f"{self.arrayName}[{self.index}].{name}")

    def set_property(self, name, value, type=float):
        if type==float:
            self.parent.SetMetadataDouble(f"{self.arrayName}[{self.index}].{name}", value)
        if type=="int64":
            self.parent.SetMetadataInt64(f"{self.arrayName}[{self.index}].{name}", value)
        if type==int:
            self.parent.SetMetadataInt(f"{self.arrayName}[{self.index}].{name}", value)
        if type==bool:
            self.parent.SetMetadataBool(f"{self.arrayName}[{self.index}].{name}", value)
        if type==str:
            self.parent.SetMetadataString(f"{self.arrayName}[{self.index}].{name}", value)

    @property
    def coordinates(self):
        return (
            self.parent.GetMetadataDouble(f"{self.arrayName}[{self.index}].crds[0]"),
            self.parent.GetMetadataDouble(f"{self.arrayName}[{self.index}].crds[1]"),
            self.parent.GetMetadataDouble(f"{self.arrayName}[{self.index}].crds[2]"),
        )
    @coordinates.setter
    def coordinates(self, newVal):
        self.parent.SetMetadataDouble(f"{self.arrayName}[{self.index}].crds[0]", newVal[0]),
        self.parent.SetMetadataDouble(f"{self.arrayName}[{self.index}].crds[1]", newVal[1]),
        self.parent.SetMetadataDouble(f"{self.arrayName}[{self.index}].crds[2]", newVal[2]),

    @property
    def name(self):
        return self.parent.GetMetadataString(f"{self.arrayName}[{self.index}].name")
    @name.setter
    def name(self, newVal):
        self.parent.SetMetadataString(f"{self.arrayName}[{self.index}].name", newVal)

    @property
    def count(self):
        return self.parent.GetMetadataInt(f"{self.arrayName}[{self.index}].count", 1)
    @count.setter
    def count(self, newVal):
        return self.parent.SetMetadataInt(f"{self.arrayName}[{self.index}].count", newVal)

class Place(ProjectArrayItem):
    def __init__(self, parent, index):
        super().__init__(parent, index, arrayName="places")

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


