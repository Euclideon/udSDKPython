## udSDK Python3 API Examples

<!-- TODO: Write a brief abstract explaining this sample -->
This directory contains a set of examples for using the udSDK high level API for creating and modifying udStream projects,
as well as converting, exporting and analyzing UDS files. The target user for these examples is the udStream power user 
wishing to automate parts of their data pipeline.

These examples assume that the environment variable `udSDK_HOME` is set to the location of udSDK
used has included the udSDKPython in the pythonpath

To run these samples the src/udSDK and src/samples should be added to your interpreters `PYTHONPATH`

By default the sample scripts will open a browser window on login to udCloud - if you posess an api key then it can be set in
`sampleLogin.py` to skip this step when 

<!-- TODO: Fill this section below with metadata about this sample-->
```
Language:              Python3
Type:                  Language Example
Contributor:           Euclideon udSDK Development Team <support@euclideon.com>
Organization:          Euclideon, https://euclideon.com/
Date:                  2022-05-10
udSDK Version:         2.2
Toolsets:              -
```


### visualiser
An example script using the udSDK API to visualise uds files 

### basic_convert.py
This files demonstrates the interface for converting [standard filetypes](https://desk.euclideon.com/portal/en/kb/articles/how-to-supported-data-formats-for-conversion) 
to uds file format. Addition of metadata and setting of SRID values are also demonstrated.

### basicRender.py
Script generating a .png image of a uds file from a defined perspective.

### customConvert.py
Script defining a custom file conversion. This demonstrates how to write uds files directly from data.

### export_las.py
This demonstrates the use of the udPointCloud interface to export to las format. The file gives examples of exporting a whole las,
as well as an example of exporting a uds into a regular grid of las files.

### export_numpy.py
This demonstrates the use of the udQuery interface to directly return points into the python environment. Examples of 
the interface to extract points and their attributes as well as plotting a subsampled pointcloud are given.

### converter.py
Example of a basic command line program converting for converting to UDS


### udcloud_scene_downloader.py
This app is used to make local copies of hosted udcloud scenes, or collate a local scene into one where all required resources are 
copied into a single content folder.