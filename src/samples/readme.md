## Python3 API Examples

<!-- TODO: Write a brief abstract explaining this sample -->
This directory contains a set of examples for using the udSDK high level API for creating and modifying udStream projects,
as well as converting, exporting and analyzing UDS files. The target user for these examples is the udStream power user 
wishing to automate parts of their data pipeline.

These examples assume that the environment variable `udSDK_HOME` is set to the location of udSDK, additionally that the python interpreter
used has included the udSDKPython in the pythonpath

The scripts are intended to be run with the username and password as command line arguments
e.g. python basic_convert myUsername@domain.com myEuclideonPassword

Modification to the code will be required to use the non default server by changing the arguments to udContext.log_in()
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

### basic_convert.py
This files demonstrates the interface for converting [standard filetypes](https://desk.euclideon.com/portal/en/kb/articles/how-to-supported-data-formats-for-conversion) 
to uds file format. Addition of metadata and setting of SRID values are also demonstrated.

### export_las.py
This demonstrates the use of the udPointCloud interface to export to las format. The file gives examples of exporting a whole las,
as well as an example of exporting a uds into a regular grid of las files.

### export_numpy.py
This demonstrates the use of the udQuery interface to directly return points into the python environment. Examples of 
the interface to extract points and their attributes as well as plotting a subsampled pointcloud are given.