## Python3 udSDK 

<!-- TODO: Write a brief abstract explaining this sample -->
This integration contains several demonstrations of using udSDK renderer in increasingly complex contexts.
The code is written to be as modular as possible and is designed as an interface for udSDK to the Python language and it's libraries.

<!-- TODO: Fill this section below with metadata about this sample-->
```
Language:              Python3
Type:                  Language Example
Contributor:           Euclideon udSDK Development Team <support@euclideon.com>
Organization:          Euclideon, https://euclideon.com/
Date:                  2021-06-14
udSDK Version:         2.1
Toolsets:              IPython 3.8 Pillow Pyglet Numpy IPython3
```

## Resources Required
<!-- TODO: Fill this section below with the resources required to do this sample-->
This resource requires Euclideon udSDK and the following Python libraries to be installed for python 3.8:

### Install Euclideon udSDK
Euclideon udSDK can be obtained from [here](https://www.euclideon.com/udsdk/)

Set the system variable for `UDSDK_HOME` on your operating system to the folder that udSDK was downloaded to. The SDK functionality 
can be then accessed by adding src/udSDK to your `PYTHONPATH`. 

#### Windows
On Windows, run command prompt as administrator and then run the command:
`setx UDSDK_HOME "[path to udSDK]"`

e.g.

`setx UDSDK_HOME "C:\Euclideon_udSDKX.XX"`

This can also be achieved using the environment variables dialog.

#### Linux
Add the following command to your `.bashrc`

`export UDSDK_HOME="[path to udSDK]"`

Restart your terminal or open a new one

### Configure Python
The following packages are required to run the contained packages.

- pillow (formerly PIL)

- Pyglet

- Numpy (or Scipy)

- Ipython3

All packages are available through the pip repository and can be installed via 

`pip install ipython pyglet pillow scipy`

## How to use the sample
<!-- TODO: Explain how this sample can be used and what is required to get it running -->


# src/udSDK

This directory contains the core wrapper of udSDK for Python. Including this in your PYTHONPATH see the [readme](src/udSDK/readme.md) for
more information.

# src/samples

This directory contains a set of examples of use cases for udSDK. See the [readme](src/samples/readme.md) for more information.


## Supported Modules and Notes

This wrapper constitutes a subset of the larger udSDK C API. More complete documentation for wrapped functions can be found 
in the udSDK header files included with the current udSDK distribution


<!-- End -->
