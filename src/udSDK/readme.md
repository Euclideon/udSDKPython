## udSDK Python3 API Examples

<!-- TODO: Write a brief abstract explaining this sample -->
This directory contains the library wrapping the udSDK C API. Object functionality largely mirrors this API.

```
Language:              Python3
Type:                  Language Example
Contributor:           Euclideon udSDK Development Team <support@euclideon.com>
Organization:          Euclideon, https://euclideon.com/
Date:                  2022-05-10
udSDK Version:         2.2
Toolsets:              -
```
### Known Limitations
Some functionality accessible through the C API may not be available through this wrapper. Future releases will aim to further 
close this gap but some functionality may not be supported in Python for technical reasons. If you encounter a gap in functionality 
necessary for your project please [contact us](support@euclideon.com).

- Only `udGeometry_OBB` geometry type is currently supported as a query filter type
- Voxel Shaders are not supported for render
- Not all `udProject` scene item types supported by udStream are supported in the wrapper. 
- 
