import ctypes
import os
from enum import IntEnum

import udSDK
import udSDKGeometry
from udSDK import _HandleReturnValue


class udSceneLoadSource(IntEnum):
    """
    Indicates where the project is loaded from
    """
    udSceneLoadSource_Memory = 0  # !< The project source exists in memory; udScene_CreateInMemory = udScene_LoadFromMemory or udScene_SaveToMemory
    udSceneLoadSource_Server = 1  # !< The project source exists from the server; udScene_CreateInServer = udScene_LoadFromServer or udScene_SaveToServer
    udSceneLoadSource_URI = 2  # !< The project source exists from a file or URL; udScene_CreateInFile = udScene_LoadFromFile or udScene_SaveToFile

    udSceneLoadSource_Count = 3  # !< Total number of source types. Used internally but can be used as an iterator max when displaying different source types.


class udSceneGeometryType(IntEnum):
    """
    Indicates the type of geometry assocated with a project node
    """
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


class udSceneNodeType(IntEnum):
    """
    Indicates the type of object represented by the project node
    """
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
    """
    Represents the position and orientation of a users camera
    """
    _fields_ = [
        ('x', ctypes.c_double),
        ('y', ctypes.c_double),
        ('z', ctypes.c_double),
        ('heading', ctypes.c_double),
        ('pitch', ctypes.c_double),
    ]

class udSelectedNode(ctypes.Structure):
    """
    Represents the selected project node of a user
    """
    _fields_ = [
        ("id", ctypes.c_char * 37)
    ]

class udAvatarInfo(ctypes.Structure):
    """
    represents an avatar used in collaboration
    """
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
    """
    Represents a message sent in a project to users
    """
    _fields = [
        ("pMessageType", ctypes.c_char_p),
        ("pMessagePayload", ctypes.c_char_p),
        ("pTargetSessionID", ctypes.c_char_p),
        ("pReceivedFromSessionID", ctypes.c_char_p),
    ]

class udUserPosition(ctypes.Structure):
    """
    Represents a message sent in a project to users
    """
    _fields_ = [
        ("username", ctypes.c_char_p),
        ("ID", ctypes.c_char_p),
        ("pSceneSessionID", ctypes.c_char_p),
        ("lastUpdated", ctypes.c_double),
        ("selectedNodesCount", ctypes.c_uint32),
        ("selectedNodesList", ctypes.POINTER(udSelectedNode)),
        ("udCameraPosition", ctypes.POINTER(udCameraPosition)),
        ("udAvatarInfo", udAvatarInfo),
    ]

class udSceneUpdateInfo(ctypes.Structure):
    """
    This represents the update info given/received to/by udScene_Update
    """
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


class udSceneNode(ctypes.Structure):
    """
    A node of the project tree
    """
    fileList = None

    def __init__(self, project):
        self.project = project
        self._udSceneNode_Create = getattr(udSDK.udSDKlib, "udSceneNode_Create")
        self._udSceneNode_MoveChild = getattr(udSDK.udSDKlib, "udSceneNode_MoveChild")
        self._udSceneNode_RemoveChild = getattr(udSDK.udSDKlib, "udSceneNode_RemoveChild")
        self._udSceneNode_SetName = getattr(udSDK.udSDKlib, "udSceneNode_SetName")
        self._udSceneNode_SetVisibility = getattr(udSDK.udSDKlib, "udSceneNode_SetVisibility")
        self._udSceneNode_SetURI = getattr(udSDK.udSDKlib, "udSceneNode_SetURI")
        self._udSceneNode_SetGeometry = getattr(udSDK.udSDKlib, "udSceneNode_SetGeometry")
        self._udSceneNode_GetMetadataInt = getattr(udSDK.udSDKlib, "udSceneNode_GetMetadataInt")
        self._udSceneNode_SetMetadataInt = getattr(udSDK.udSDKlib, "udSceneNode_SetMetadataInt")
        self._udSceneNode_GetMetadataUint = getattr(udSDK.udSDKlib, "udSceneNode_GetMetadataUint")
        self._udSceneNode_SetMetadataUint = getattr(udSDK.udSDKlib, "udSceneNode_SetMetadataUint")
        self._udSceneNode_GetMetadataInt64 = getattr(udSDK.udSDKlib, "udSceneNode_GetMetadataInt64")
        self._udSceneNode_SetMetadataInt64 = getattr(udSDK.udSDKlib, "udSceneNode_SetMetadataInt64")
        self._udSceneNode_GetMetadataDouble = getattr(udSDK.udSDKlib, "udSceneNode_GetMetadataDouble")
        self._udSceneNode_SetMetadataDouble = getattr(udSDK.udSDKlib, "udSceneNode_SetMetadataDouble")
        self._udSceneNode_GetMetadataBool = getattr(udSDK.udSDKlib, "udSceneNode_GetMetadataBool")
        self._udSceneNode_SetMetadataBool = getattr(udSDK.udSDKlib, "udSceneNode_SetMetadataBool")
        self._udSceneNode_GetMetadataString = getattr(udSDK.udSDKlib, "udSceneNode_GetMetadataString")
        self._udSceneNode_SetMetadataString = getattr(udSDK.udSDKlib, "udSceneNode_SetMetadataString")
        self.initialised = True

        # handle place layers specially as they are encoded differently:
        if(udSceneNodeType(self.itemtype) == udSceneNodeType.udPNT_Places):
            self.__class__ = PlaceLayerNode
            self.on_cast()

        self.children = self._Children(self)

    @property
    def uri(self):
        """
        The url or local path to the resource referenced by this node
        """
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
        """
        The parent node of this one in the project tree
        """
        return self.from_pointer(self.pParent)

    @property
    def coordinates(self):
        """
        a list of x,y,z tuples associated with this node
        """
        if self.pCoordinates is None:
            return []
        return [(self.pCoordinates[3*i], self.pCoordinates[3*i+1], self.pCoordinates[3*i+2] ) for i in range(self.geomCount)]

    @coordinates.setter
    def coordinates(self, coords):
        self.set_geometry(coordinates=coords)

    def from_pointer(self, pointer, project=None):
        """
        creates a project node object from a native pointer to it
        """
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
        """
        The name of the node
        """
        return self.pName.decode('utf8')

    @name.setter
    def name(self, newval:str):
        self._set_name(newval)

    @property
    def firstChild(self):
        """
        The first child of this node in the tree, None if this node has none
        """
        return self.from_pointer(self.pFirstChild)

    @property
    def nextSibling(self):
        """
        The next node at the same level in the tree, None if this is the last node in this level
        """
        return self.from_pointer(self.pNextSibling)

    def create_child(self, type:str, name:str, uri="", pUserData=None):
        """
        Creates a node at the end of the next layer down in the tree
        """
        if self.firstChild is None:
            _HandleReturnValue(self._udSceneNode_Create(self.project.pScene, None, ctypes.byref(self), type.encode('utf8'), name.encode('utf8'), uri.encode('utf8'), ctypes.c_void_p(0)))
            assert self.firstChild is not None
            return self.firstChild
        else:
            return self.firstChild.create_sibling(type, name, uri, pUserData)

    def create_sibling(self, type:str, name:str, uri="", pUserData=None):
        """
        creates a node at the end of this layer in the tree
        """
        if self.nextSibling is None:
            _HandleReturnValue(self._udSceneNode_Create(self.project.pScene, None, ctypes.byref(self.parent), type.encode('utf8'), name.encode('utf8'), uri.encode('utf8'), ctypes.c_void_p(0)))
            assert self.nextSibling is not None
            return self.nextSibling
        else:
            return self.nextSibling.create_sibling(type, name, uri, pUserData)

    @property
    def boundingBox(self):
        """
        The bounds in order of [West, South, Floor, East, North, Ceiling]
        """
        if self.hasBoundingBox:
            return [self._boundingBox[i] for i in range(6)]
        else:
            return None

    @boundingBox.setter
    def boundingBox(self, boundingBox):
        assert len(boundingBox) == 6, "boundingBox list length must be 6"
        arrType = (ctypes.c_double * len(boundingBox))
        arr = arrType(*boundingBox)
        _HandleReturnValue(self._udSceneNode_SetBoundingBox(self.project.pScene, ctypes.byref(self), arr))
        return

    def to_ud_type(self):
        """
        returns an instance of the corresponding UDSDK type (if implemented)
        """
        context = self.project._udContext
        if self.itemtypeStr == b'QFilter':
            shape = self.get_metadata_string("shape")
            position = self.coordinates[0]
            size =[self.get_metadata_double(f"size.{a}") for a in 'xyz']
            ypr =[self.get_metadata_double(f"transform.rotation.{a}") for a in 'ypr']
            halfheight = self.get_metadata_double("size.y")
            radius = self.get_metadata_double("size.x")
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
        elif type(beforeSibling) == udSceneNode:
            pBeforeSibling = ctypes.byref(beforeSibling)
        else:
            raise TypeError(f"Unsupported sibling type ({type(beforeSibling)}): must be integer, udSceneNode or None")

        _HandleReturnValue(self._udSceneNode_MoveChild(self.project.pScene, pCurrentParent, pNewParent, ctypes.byref(self), pBeforeSibling))

    def remove(self):
        """
        removes this node from the tree
        """
        _HandleReturnValue(self._udSceneNode_RemoveChild(self.project.pScene, ctypes.byref(self.parent), ))

    def _set_name(self, newName:str):
        return _HandleReturnValue(self._udSceneNode_SetName(self.project.pScene, ctypes.byref(self), newName.encode('utf8')))

    @property
    def visibility(self):
        """
        determines if this node is marked as visible in udStream
        """
        return self._isVisible

    @visibility.setter
    def visibility(self, val:bool):
        _HandleReturnValue(self._udSceneNode_SetVisibility(self, ctypes.c_bool(val)))

    def _set_uri(self, uri: str):
        _HandleReturnValue(self._udSceneNode_SetURI(self.project.pScene, ctypes.byref(self), uri.encode('utf8')))

    def set_geometry(self, coordinates, geometryType:udSceneGeometryType=None):
        """
        sets the geometry type and the associated coordinates
        """
        if geometryType is None:
            geometryType = self.geomtype

        arrType = (ctypes.c_double * len(coordinates))
        count = int(len(coordinates)//3)
        assert not len(coordinates) % 3, "coordinate list length must be a multiple of 3"
        arr = arrType(*coordinates)
        _HandleReturnValue(self._udSceneNode_SetGeometry(self.project.pScene, ctypes.byref(self), int(geometryType), count, ctypes.byref(arr)))

    def get_metadata_int(self, key:str, defaultValue=int(0)):
        """
        gets the metadata entry key as an integer value
        """
        ret = ctypes.c_int32(defaultValue)
        success = (self._udSceneNode_GetMetadataInt(ctypes.byref(self), key.encode("utf8"), ctypes.byref(ret), ctypes.c_int32(defaultValue)))
        if success != udSDK.udError.NotFound:
            _HandleReturnValue(success)
            return ret.value
        else:
            return defaultValue

    def set_metadata_int(self, key:str, value:int):
        """
        sets the metadata entry key as an integer value
        """
        _HandleReturnValue(self._udSceneNode_SetMetadataInt(ctypes.byref(self), key.encode('utf8'), ctypes.c_int32(value)))

    def get_metadata_uint(self, key :str, defaultValue):
        """
        gets the metadata entry key as an unsigned integer value
        """
        ret = ctypes.c_uint32(defaultValue)
        success = (self._udSceneNode_GetMetadataUInt(ctypes.byref(self), key.encode("utf8"), ctypes.byref(ret), ctypes.c_int32(defaultValue)))
        if success != udSDK.udError.NotFound:
            _HandleReturnValue(success)
            return ret.value
        else:
            return defaultValue

    def set_metadata_uint(self, key:str, value):
        """
        sets the metadata entry key as an unsigned integer value
        """
        _HandleReturnValue(self._udSceneNode_SetMetadataUInt(ctypes.byref(self), key.encode('utf8'), ctypes.c_uint32(value)))

    def get_metadata_int64(self, key:str, defaultValue):
        """
        gets the metadata entry key as an unsigned long integer value
        """
        ret = ctypes.c_int64(defaultValue)
        success = (self._udSceneNode_GetMetadataInt64(ctypes.byref(self), key.encode("utf8"), ctypes.byref(ret), ctypes.c_int32(defaultValue)))
        if success != udSDK.udError.NotFound:
            _HandleReturnValue(success)
            return ret.value
        else:
            return defaultValue

    def set_metadata_int64(self, key, value):
        """
        sets the metadata entry key as an unsigned long integer value
        """
        _HandleReturnValue(self._udSceneNode_SetMetadataInt64(ctypes.byref(self), key.encode('utf8'), ctypes.c_int64(value)))

    def get_metadata_double(self, key:str, defaultValue=float(0)):
        """
        gets the metadata entry key as a double precision floating point value
        """
        ret = ctypes.c_double(0)
        success = (self._udSceneNode_GetMetadataDouble(ctypes.byref(self), key.encode("utf8"), ctypes.byref(ret), ctypes.c_double(defaultValue)))
        if success != udSDK.udError.NotFound:
            _HandleReturnValue(success)
            return ret.value
        else:
            return defaultValue

    def set_metadata_double(self, key:str, value:float):
        """
        sets the metadata entry key as a double precision floating point value
        """
        _HandleReturnValue(self._udSceneNode_SetMetadataDouble(ctypes.byref(self), key.encode('utf8'), ctypes.c_double(value)))

    def get_metadata_bool(self, key:str, defaultValue = ctypes.c_uint32(False)):
        """
        gets the metadata entry key as a boolean value
        """
        ret = ctypes.c_uint32(0)
        success = (self._udSceneNode_GetMetadataBool(ctypes.byref(self), key.encode("utf8"), ctypes.byref(ret), ctypes.c_double(defaultValue)))
        if success != udSDK.udError.NotFound:
            _HandleReturnValue(success)
            return bool(ret.value)
        else:
            return bool(defaultValue)

    def set_metadata_bool(self, key, value):
        """
        sets the metadata entry key as a boolean value
        """
        _HandleReturnValue(self._udSceneNode_SetMetadataBool(ctypes.byref(self), key.encode('utf8'), ctypes.c_uint32(value)))

    def get_metadata_string(self, key:str, defaultValue=None):
        """
        gets the metadata entry key as a string
        """
        ret = ctypes.c_char_p(0)
        success = self._udSceneNode_GetMetadataString(self, key.encode("utf8"), ctypes.byref(ret), "")
        if success != udSDK.udError.NotFound:
            _HandleReturnValue(success)
            return ret.value.decode('utf8')
        else:
            return defaultValue

    def set_metadata_string(self, key:str, value:str):
        """
        sets the metadata entry key as a string
        """
        _HandleReturnValue(self._udSceneNode_SetMetadataString(ctypes.byref(self), key.encode('utf8'), value.encode('utf8')))

    class _Children:
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


udSceneNode._fields_ = \
    [
        # Node header data
        ("_isVisible", ctypes.c_int),  # !< Non-zero if the node is visible and should be drawn in the scene
        ("UUID", (ctypes.c_char * 37)),  # !< Unique identifier for this node "id"
        ("lastUpdate", ctypes.c_double),  # !< The last time this node was updated in UTC

        ("itemtype", ctypes.c_int),  # !< The type of this node, see udSceneNodeType for more information
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
        # !< Indicates what geometry can be found in this model. See the udSceneGeometryType documentation for more information.
        ("geomCount", ctypes.c_uint32),  # !< How many geometry items can be found on this model
        ("pCoordinates", ctypes.POINTER(ctypes.c_double)),
        # !< The positions of the geometry of this node (NULL this this node doesn't have points). The format is [X0,Y0,Z0,...Xn,Yn,Zn]

        ("pParent", ctypes.POINTER(udSceneNode)),
        # Next nodes
        ("pNextSibling", ctypes.POINTER(udSceneNode)),
        # !< This is the next item in the project (NULL if no further siblings)
        ("pFirstChild", ctypes.POINTER(udSceneNode)),
        # !< Some types ("folder", "collection", "polygon"...) have children nodes, NULL if there are no children.

        # Node Data
        ("pUserDataCleanup", ctypes.c_void_p),
        ("pUserData", ctypes.c_void_p),
        # !< This is application specific user data. The application should traverse the tree to release these before releasing the udScene
        ("pInternalData", ctypes.c_void_p),  # !< Internal udSDK specific state for this node
    ]


class udScene():
    """
    Object representing a udCloud Scene as constructed using udStream
    """
    filename = None
    def __init__(self, context: udSDK.udContext):
        self._udScene_CreateInMemory = getattr(udSDK.udSDKlib, "udScene_CreateInMemory")
        self._udScene_CreateInFile = getattr(udSDK.udSDKlib, "udScene_CreateInFile")
        self._udScene_CreateInServer = getattr(udSDK.udSDKlib, "udScene_CreateInServer")
        self._udScene_LoadFromServer = getattr(udSDK.udSDKlib, "udScene_LoadFromServer")
        self._udScene_LoadFromMemory = getattr(udSDK.udSDKlib, "udScene_LoadFromMemory")
        self._udScene_LoadFromFile = getattr(udSDK.udSDKlib, "udScene_LoadFromFile")
        self._udScene_Release = getattr(udSDK.udSDKlib, "udScene_Release")
        self._udScene_Save = getattr(udSDK.udSDKlib, "udScene_Save")
        self._udScene_SaveToMemory = getattr(udSDK.udSDKlib, "udScene_SaveToMemory")
        self._udScene_SaveToServer = getattr(udSDK.udSDKlib, "udScene_SaveToServer")
        self._udScene_SaveToFile = getattr(udSDK.udSDKlib, "udScene_SaveToFile")
        self._udScene_GetProjectRoot = getattr(udSDK.udSDKlib, "udScene_GetProjectRoot")
        self._udScene_GetProjectUUID = getattr(udSDK.udSDKlib, "udScene_GetProjectUUID")
        self._udScene_HasUnsavedChanges = getattr(udSDK.udSDKlib, "udScene_HasUnsavedChanges")
        self._udScene_GetLoadSource = getattr(udSDK.udSDKlib, "udScene_GetLoadSource")
        self._udScene_GetTypeName = getattr(udSDK.udSDKlib, "udScene_GetTypeName")
        self._udScene_DeleteServerScene = getattr(udSDK.udSDKlib, "udScene_DeleteServerProject")
        self._udScene_SetLinkShareStatus = getattr(udSDK.udSDKlib, "udScene_SetLinkShareStatus")
        self._udScene_Update = udSDK.udExceptionDecorator(udSDK.udSDKlib.udScene_Update)
        self._udScene_GetSessionID = udSDK.udExceptionDecorator(udSDK.udSDKlib.udScene_GetSessionID)
        self._udScene_QueueMessage = udSDK.udExceptionDecorator(udSDK.udSDKlib.udScene_QueueMessage)
        self._udScene_SaveThumbnail = udSDK.udExceptionDecorator(udSDK.udSDKlib.udScene_SaveThumbnail)

        self._udContext = context
        self.pScene = ctypes.c_void_p(0)

    @property
    def rootNode(self):
        """
        The udSceneNode at the root of the project
        """
        return self._get_project_root()

    def create_in_memory(self, name:str):
        """
        creates the project in memory
        """
        _HandleReturnValue(self._udScene_CreateInMemory(self._udContext.pContext, ctypes.byref(self.pScene),name.encode('utf8')))

    def create_in_file(self, name:str, filename:str, override_if_exists=False):
        """
        creates the project as a .json or .udjson file locally
        """
        self.filename = filename
        if os.path.exists(filename):
            if override_if_exists:
                os.remove(filename)
            else:
                raise FileExistsError
        _HandleReturnValue(self._udScene_CreateInFile(self._udContext.pContext, ctypes.byref(self.pScene), name.encode('utf8'), filename.encode('utf8')))

    def create_in_server(self, name:str, groupID:str):
        """
        Creates the project on the server that context is currently logged in to
        groupID: The ID for the workspace/project for udCloud projects (null for udServer projects)
        """
        _HandleReturnValue(self._udScene_CreateInServer(self._udContext.pContext, ctypes.byref(self.pScene), name.encode('utf8'), groupID.encode('utf8')))

    def load_from_server(self, uuid: str, groupID:str):
        """
        loads the project from the server that context is currently logged in to
        groupID: The ID for the workspace/project for udCloud projects (null for udServer projects)
        """
        self.filename = None
        return _HandleReturnValue(
            self._udScene_LoadFromServer(self._udContext.pContext, ctypes.byref(self.pScene), uuid.encode('utf8'), groupID.encode('utf8')))

    def load_from_memory(self, geoJSON: str):
        """
        loads a project from memory
        """
        self.filename = None
        _HandleReturnValue(self._udScene_LoadFromMemory(self._udContext.pContext, ctypes.byref(self.pScene), geoJSON.encode('utf8')))
        return

    def load_from_file(self, filename: str):
        """
        loads a project from a geojson or .udjson file
        """
        self.filename = filename.replace('\\\\','/')
        _HandleReturnValue(self._udScene_LoadFromFile(self._udContext.pContext, ctypes.byref(self.pScene), filename.encode('utf8')))

    def release(self):
        """
        Destroy this instance of the project
        """
        _HandleReturnValue(self._udScene_Release(ctypes.byref(self.pScene)))

    def save(self):
        """
        Saves the current changes to the project to the current loading location
        """
        _HandleReturnValue(self._udScene_Save(self.pScene))

    @property
    def geoJSON(self):
        """
        The current project as a GEOJSON string
        """
        ret = ctypes.c_char_p(0)
        _HandleReturnValue(self._udScene_SaveToMemory(self._udContext.pContext, self.pScene, ctypes.byref(ret)))
        return ret.value.decode('utf8')

    def save_to_server(self, groupID:str):
        """
        saves this project to the server currently logged into
        groupID: The ID for the workspace/project for udCloud projects (null for udServer projects)
        """
        _HandleReturnValue(self._udScene_SaveToServer(self._udContext.pContext, self.pScene, groupID.encode('utf8')))

    def save_to_file(self, filename: str):
        """
        Saves the current project to a .udjson format file
        """
        _HandleReturnValue(self._udScene_SaveToFile(self._udContext.pContext, self.pScene, filename.encode('utf8')))
        self.filename = filename

    def _get_project_root(self)->udSceneNode:
        if (self.pScene == ctypes.c_void_p(0)):
            raise Exception("Scene not loaded")
        a = ctypes.pointer(udSceneNode(self))
        _HandleReturnValue(self._udScene_GetProjectRoot(self.pScene, ctypes.byref(a)))
        rootNode = a.contents
        rootNode.__init__(self)
        rootNode.fileList = []
        return rootNode

    def update(self):
        """
        updates the project, returning the latest update info
        """
        info = udSceneUpdateInfo()
        self._udScene_Update(self.pScene, ctypes.byref(info))
        return info

    @property
    def uuid(self):
        """
        The unique identifier of this project
        """
        ret = ctypes.c_char_p(0)
        _HandleReturnValue(self._udScene_GetProjectUUID(self.pScene, ctypes.byref(ret)))
        return ret.value.decode('utf8')

    @property
    def hasUnsavedChanges(self):
        """
        Whether this project has local unsaved changes
        """
        return self._udScene_HasUnsavedChanges(self.pScene) == udSDK.udError.Success

    @property
    def loadSource(self):
        """
        Where this project has been loaded from
        """
        source = ctypes.c_int
        _HandleReturnValue(self._udScene_GetLoadSource(self.pScene, ctypes.byref(source)))
        return udSceneLoadSource(source)

    def item_type_to_type_name(self, value:udSceneNodeType):
        """
        Utility to convert udSceneNodeType enum to a string
        """
        ret = self._udScene_GetTypeName(value)
        if ret == ctypes.c_void_p:
            return None
        else:
            return ctypes.c_char_p(ret).value.decode('utf8')

    def delete_from_server(self, groupID:str):
        """
        deletes the project from the server
        """
        return _HandleReturnValue(self._udScene_DeleteServerScene(self._udContext.pContext, self.uuid.encode('utf8'), groupID.encode('utf8')))

    def set_link_share_status(self, sharableWithAnyoneWithLink:bool, groupID:str):
        """
        Sets whether anyone with the link to this project can share it regardless of the receivers permissions
        """
        return _HandleReturnValue(self._udScene_SetLinkShareStatus(self._udContext.pContext, self.uuid, sharableWithAnyoneWithLink, groupID.encode('utf8')))

    @property
    def sessionID(self):
        """
        The session ID (for server projects)
        """
        sessionID = ctypes.c_char_p(0)
        self._udScene_GetSessionID(self._udContext.pContext, ctypes.byref(sessionID))
        return sessionID.value.decode('utf8')

    def queue_message(self, messageType:str, messagePayload:str, targetSessionID=None):
        """
        queues a message to be sent to all clients in collaboration
        """
        if targetSessionID is None:
            targetSessionID = self.sessionID
        self._udScene_QueueMessage(self.pScene, targetSessionID.encode('utf8'), messageType.encode('utf8'), messagePayload.encode('utf8'))

    def save_thumbnail(self, imageBase64):
        """
        Saves a project thumbnail in base64 to a udCloud server
        """
        self._udScene_SaveThumbnail(self.pScene, imageBase64)

    def __del__(self):
        self.release()



class ArrayLayerNode(udSceneNode):
    """
    Scene node representing an array
    """
    _arrLength = None
    def __init__(self, parent, arrayItemType):
        super().__init__(parent)
        self.model = Model(self)
        self.arrayItemType = arrayItemType
        self.geomtype = udSceneGeometryType.udPGT_MultiPoint

    def __len__(self):
        if self._arrLength is None:
            self._arrLength = 0
            while self.arrayItemType(self, self._arrLength).name is not None:
                self._arrLength += 1
        return self._arrLength

    def add_item(self, name, coordinates, count):
        place = self.arrayItemType(self, len(self))
        place.count = count
        place.name = name
        place.coordinates = coordinates
        self._arrLength += 1
        #self.places.append(place)

    def on_cast(self):
        self.model = Model(self)

    @property
    def pin(self):
        """
        location of the image to be displayed above each place in the place layer
        """
        return self.get_metadata_string("pin")
    @pin.setter
    def pin(self, newVal:str):
        self.set_metadata_string("pin", newVal)

    @property
    def pinDistance(self):
        """
        Distance above which to merge pins
        """
        return self.get_metadata_double("pinDistance")
    @pinDistance.setter
    def pinDistance(self, newVal:float):
        self.set_metadata_double("pinDistance", newVal)

    @property
    def labelDistance(self):
        """
        distance below which to display place labels
        """
        return self.get_metadata_double("labelDistance")
    @labelDistance.setter
    def labelDistance(self, newVal:float):
        self.set_metadata_double("labelDistance", newVal)

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
        def __init__(self, node:udSceneNode):
            self.node = node

class PlaceLayerNode(ArrayLayerNode):
    """
    Specialisation of udSceneNode using the special array syntax for storing places
    """
    def __init__(self, parent):
        super().__init__(self, parent, Place)

    def on_cast(self):
        self.model = Model(self)
        self.arrayItemType = Place


class SceneArrayItem():
    """
    Abstract class representing an item stored as an array in node metadata e.g. places
    """
    def __init__(self, parent:PlaceLayerNode, index:int, arrayName:str):
        self.parent = parent
        self.index = index
        self.arrayName = arrayName

    def get_property(self, name:str, type=float):
        if type==float:
            return self.parent.get_metadata_double(f"{self.arrayName}[{self.index}].{name}")
        if type=="int64":
            return self.parent.get_metadata_int64(f"{self.arrayName}[{self.index}].{name}")
        if type==int:
            return self.parent.get_metadata_int(f"{self.arrayName}[{self.index}].{name}")
        if type==bool:
            return self.parent.get_metadata_bool(f"{self.arrayName}[{self.index}].{name}")
        if type==str:
            return self.parent.get_metadata_string(f"{self.arrayName}[{self.index}].{name}")

    def set_property(self, name, value, type=float):
        if type==float:
            self.parent.set_metadata_double(f"{self.arrayName}[{self.index}].{name}", value)
        if type=="int64":
            self.parent.set_metadata_int64(f"{self.arrayName}[{self.index}].{name}", value)
        if type==int:
            self.parent.set_metadata_int(f"{self.arrayName}[{self.index}].{name}", value)
        if type==bool:
            self.parent.set_metadata_bool(f"{self.arrayName}[{self.index}].{name}", value)
        if type==str:
            self.parent.set_metadata_string(f"{self.arrayName}[{self.index}].{name}", value)

    @property
    def coordinates(self):
        return self.parent.coordinates[self.index]
    @coordinates.setter
    def coordinates(self, newVal):
        oldCoords = self.parent.coordinates
        if self.index < len(oldCoords):
            oldCoords[self.index] = newVal
        elif self.index == len(oldCoords):
            oldCoords.append(newVal)
        c = [x for xs in oldCoords for x in xs]
        self.parent.set_geometry(c, udSceneGeometryType.udPGT_MultiPoint)

    @property
    def name(self):
        return self.parent.get_metadata_string(f"{self.arrayName}[{self.index}].name")
    @name.setter
    def name(self, newVal):
        self.parent.set_metadata_string(f"{self.arrayName}[{self.index}].name", newVal)

    @property
    def count(self):
        return self.parent.get_metadata_int(f"{self.arrayName}[{self.index}].count", 1)
    @count.setter
    def count(self, newVal):
        return self.parent.set_metadata_int(f"{self.arrayName}[{self.index}].count", newVal)

class Place(SceneArrayItem):
    def __init__(self, parent, index):
        super().__init__(parent, index, arrayName="places")

class Model():
    def __init__(self, parent:udSceneNode):
        self.parent = parent
    @property
    def url(self):
        return self.parent.get_metadata_string("modelURL")
    @url.setter
    def url(self, val:str):
        self.parent.set_metadata_string("modelURL", val)

    @property
    def offset(self):
        return (
            self.parent.get_metadata_double("modelTransform.offset.x"),
            self.parent.get_metadata_double("modelTransform.offset.y"),
            self.parent.get_metadata_double("modelTransform.offset.z"),
        )
    @offset.setter
    def offset(self, val):
        self.parent.set_metadata_double("modelTransform.offset.x", val[0])
        self.parent.set_metadata_double("modelTransform.offset.y", val[1])
        self.parent.set_metadata_double("modelTransform.offset.z", val[2])

    @property
    def rotation(self):
        return (
            self.parent.get_metadata_double("modelTransform.rotation.x"),
            self.parent.get_metadata_double("modelTransform.rotation.y"),
            self.parent.get_metadata_double("modelTransform.rotation.z"),
        )
    @rotation.setter
    def rotation(self, val):
        self.parent.set_metadata_double("modelTransform.rotation.x", val[0])
        self.parent.set_metadata_double("modelTransform.rotation.y", val[1])
        self.parent.set_metadata_double("modelTransform.rotation.z", val[2])

    @property
    def scale(self):
        return (
            self.parent.get_metadata_double("modelTransform.scale.x"),
            self.parent.get_metadata_double("modelTransform.scale.y"),
            self.parent.get_metadata_double("modelTransform.scale.z"),
        )
    @scale.setter
    def scale(self, val):
        self.parent.set_metadata_double("modelTransform.scale.x", val[0])
        self.parent.set_metadata_double("modelTransform.scale.y", val[1])
        self.parent.set_metadata_double("modelTransform.scale.z", val[2])

