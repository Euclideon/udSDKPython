## udSDK Python3 API

<!-- TODO: Write a brief abstract explaining this sample -->
This directory contains the library wrapping the udSDK C API. Object functionality largely mirrors this API.

```
Language:              Python3
Type:                  Language Wrapper
Contributor:           Euclideon udSDK Development Team <support@euclideon.com>
Organization:          Euclideon, https://euclideon.com/
Date:                  2022-05-10
udSDK Version:         2.2.0
Toolsets:              -
```
## Files
### udSDK.py
Contains the core functionality of udSDK including
- login (udContext)
- Pointcloud loading, headers, and export to las/uds (udPointCloud)
- Point cloud attributes/channel representation (udAttribute)
- Query of point clouds (udQuery)
- Storage of points for reading and writing to uds models (udPointBuffer)
- Rendering of point clouds (udRenderContext, udRenderTarget)
- Retrieving and interpreting the status of the udSDK streaming system (usStreamer)
- Setting of global parameters such as proxy settings for all udSDK library functions (udConfig)

### udSDKConvert.py
Contains components related to converting point clouds to unlimited detail format:
- Conversion to supported file formats and setting of standard settings (udConvert)
- Definition of custom file conversions to .uds (udCustomConvert)

### udSDKGeometry.py
Geometry definitions used when filtering point clouds during rendering or performing queries on a dataset

### udSDKProject.py
Interface for interacting with udSDK scenes. Allows the loading, reading, creation and modification of udCloud scenes
and local .udjson scenes created using udStream.

### udSDKServerAPI
Wrapper to allow queries to be sent to a udCloud server

## Known Limitations
Some functionality accessible through the C API may not be available through this wrapper. Future releases will aim to further 
close this gap but some functionality may not be supported in Python for technical reasons. If you encounter a gap in functionality 
necessary for your project please [contact us](support@euclideon.com).

### udGeometry
- `Capsule`, `CircleXY`, `RectangleXY` and `PolygonXY` geometries are not currently supported at the Python level
- Conversion of geometry objects to their equivalent udProjectNode for communication with udStream is currently limited 
to `OBB` and `Sphere` filters

### udPointBuffer
- `udPointBufferI64` is not implemented in favour of using `udPointBufferF64` for reading and writing to UDS

### udProject
- Many `itemtype` variations do not have associated objects. These interpretations are application dependant and must
be tailored to the client application.
 
### udConvert
- Postprocess callbacks used during the convert process are not implemented
- Addition of attributes is not implemented
- udConvert_AddCustomItemFormat is not implemented
