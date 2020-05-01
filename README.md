## Python3 Vault SDK

<!-- TODO: Write a brief abstract explaining this sample -->
This sample contains several demonstrations of using Vault SDK renderer in increasingly complex contexts.
The code is written to be as modular as possible and 

<!-- TODO: Fill this section below with metadata about this sample-->
```
Language:              Python3
Type:                  Language Example
Contributor:           Euclideon Vault Development Team <support@euclideon.com>
Organization:          Euclideon, https://euclideon.com/vault
Date:                  2020-04-30
Vault SDK Version:     0.5.2
Toolsets:              Python3 Pillow Pyglet Numpy IPython3
```

## Resources Required
<!-- TODO: Fill this section below with the resources required to do this sample-->

## How to use the sample
<!-- TODO: Explain how this sample can be used and what is required to get it running -->
#vault.py

This is the low level wrapper for Vault SDK to python. It implements a subset of the available C library as Python classes. Not all functionality
of Vault SDK is currently implemented in this file. See the Vault SDK documentation for a full list of exposed functions.

#### main.py

This file contains the basic usage of vault SDK for rendering a UDS and writing it to file using Pillow.
It demonstrates low level usage of functions and is a good starting point for users wanting to fully understand the process of generating a render using Vault SDK

Usage: `python3 main.py yourvaultusername yourvaultpassword [pathtoUDS]` will run the sample code and write an image using the Vault Renderer

#### easyrenderer.py
This file contains a python object wrapper `EasyRenderer` which automates many commonly set features and

### Client Example

This example includes and example client written in python using the above wrappers for Vault SDKs libraries. It is intended as a starting point
for Vault SDK users wanting to develop their own client implementations and is designed to be easily extensible using python. It relies on numpy
and pyglet libraries in addition to Vault and Pillow


#### pygletexample.py
A basic python client for viewing UDS models made using pyglet (an openGL wrapper for python). It makes use of the EasyRender object interface
`App` represents the window context that the application runs in. It handles all user input and manages dispaches the draw commands to the
various UI objects.
`VDKViewPort` and it's derived objects represents an OpenGL quad which is to be textured using the frame buffer written to by each call of vdkRenderContext.Render

When this file is run as a python script (i.e. by running `python3 pygletexample.py` with the appropriate python environment set up, the calling
terminal is transferred to an IPython session with access to the namespace of current session. This allows the user control
of the session from the terminal. For example, to change the camera object the main viewport is attached to the user may run
`main.set_camera(OrthoCamera)` to change the type of camera to the Orthographic projection camera. 


#### Camera.py
Contains camera classes for use with the python. For the purposes of this example  The class definitions included in this file are designed to be extended using python's inheritance features.
Each object inherits from the base `Camera` class to allow overwriting of object methods to achieve different effects and control schemes.

`Camera` is the basic camera class implemeting a 60 degree perspective camera with standard controls


`OrthoCamera` subclasses Camera and overwites the behaviour when setting the projection matrix of the render to Orthographic.
This mode displays all parts of the model at the same scale regardless of the distance from the camera (i.e. ignoring perspective)
As such the camera 'moving' in space corresopnds only to moving the locations of the planes that define the box that the user sees.
Controls are modified to reflect this, in particular we overwite the `update_move_direction` method so that the camera moves at a fixed height.

`OrbitCamera` sublasses `Camera` and modifies its behaviour to ignore all user input.

`MapCamera` Inherits from the `OrthoCamera` We add an additional parameter to this camera `target` which
is a reference to another camera that the MapCamera sets its position to be above and looking directly down on to.
It intended to be used in conjunction with `VDKMapPort` to produce the Map UI element in the sample.

<!-- End -->
