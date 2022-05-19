## Python3 udSDK Visualiser Example

<!-- TODO: Write a brief abstract explaining this sample -->
This integration contains a demonstration of using the udSDK renderer in a real time application accepting user input.
It is built as an interface to the OpenGL wrapper pyglet though the same principles apply to interfacing udSDK with other graphics libraries.
The code is written to be as modular as possible and is designed as an interface for udSDK to the Python language and it's libraries.

<!-- TODO: Fill this section below with metadata about this sample-->
```
Language:              Python3
Type:                  Language Example
Contributor:           Euclideon udSDK Development Team <support@euclideon.com>
Organization:          Euclideon, https://euclideon.com/
Date:                  2022-05-10
udSDK Version:         2.2
Toolsets:              IPython 3.8 Pillow Pyglet Numpy IPython3
```

## How to use the sample
<!-- TODO: Explain how this sample can be used and what is required to get it running -->

#### easyrenderer.py
This file contains a python object wrapper `EasyRenderer` which automates many commonly set features and renders a UDS 
to a set of images. It is intended as a demonstration of generating renderings from UDS files.

### Python Client

This example includes and example client written in python using the above wrappers for udSDKs libraries. It is intended as a starting point
for udSDK users wanting to develop their own client implementations and is designed to be easily extensible using python. It relies on numpy
and pyglet libraries in addition to udSDK and Pillow

The integration can be run by running the following in console from the main directory:

`ipython3 pygletExample.py [udStreamUsername] [udStreamPassword]`

UDS files can then be loaded by dragging and dropping from your OS shell (Explorer on Windows) into the window that is created.

![screenshot](/doc/clientScreenshot.png)

Controls are described for each camera type on the right hand side of the screen, the camera type can be changed using `tab`.
The terminal used to start the program can be used to directly modify the behaviour of the running program. 

The best way to familiarise yourself with the features of udSDK's python wrapper is to explore the `if name == "__main:` section of pygletExample.py. Examples of usage can be found in the [blog](https://www.euclideon.com/category/python/) 
#### pygletexample.py
A basic python client for viewing UDS models made using pyglet (an openGL wrapper for python). It makes use of the EasyRender object interface
`App` represents the window context that the application runs in. It handles all user input and manages dispaches the draw commands to the
various UI objects.
`UDViewPort` and it's derived objects represents an OpenGL quad which is to be textured using the frame buffer written to by each call of udRenderContext.Render

When this file is run as a python script (i.e. by running `python3 pygletexample.py` with the appropriate python environment set up, the calling
terminal is transferred to an IPython session with access to the namespace of current session. This allows the user control
of the session from the terminal. For example, to change the camera object the main viewport is attached to the user may run
`main.set_camera(OrthoCamera)` to change the type of camera to the Orthographic projection camera. 


#### Camera.py
Contains camera classes for use with the python. For the purposes of this example  The class definitions included in this file are designed to be extended using python's inheritance features.
Each object inherits from the base `Camera` class to allow overwriting of object methods to achieve different effects and control schemes.

`Camera` is a basic camera class implementing a perspective camera with standard controls


`OrthoCamera` subclasses Camera and overwites the behaviour when setting the projection matrix of the render to Orthographic.
This mode displays all parts of the model at the same scale regardless of the distance from the camera (i.e. ignoring perspective)
As such the camera 'moving' in space corresponds only to moving the locations of the planes that define the box that the user sees.


`OrbitCamera` sublasses `Camera` and modifies the method for determining camera movement direction such that it orbits about a fixed point in space.

`MapCamera` Inherits from the `OrthoCamera` We add an additional parameter to this camera `target` which
is a reference to another camera that the MapCamera sets its position to be above and looking directly down on to.
It intended to be used in conjunction with `UDMapPort` to produce the Map UI element in the sample.



<!-- End -->
