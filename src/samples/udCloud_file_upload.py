"""
Sample Program using udServerAPI interface to upload a file in a udCloud project and get its share code.

requires azure-storage-blob package
pip install azure-storage-blob

"""

from os.path import abspath, basename, getsize
from sys import argv, exit

from numpy import double

from udSDKServerAPI import udServerAPI
from azure.storage.blob import BlobClient

import udSDK
import json

def GetWorkspace(udServer, workspaceName:str):
    res = udServer.query("org/list", None)
    if res is not None and res['success']:
        for workspace in res['organisations']:
            if workspace['name'] == workspaceName:
                return workspace
        print("Workspace named: " + workspaceName + " not found")
        exit(1)
    print("Query unsuccesful. Unable to get workspace")
    exit(1)

def GetProject(udServer, workspace:json, projectName:str):
    res = udServer.query(workspace['id']+"/_project/list", None)
    if res is not None and res['success']:
        for project in res['projects']:
            if project['name'] == projectName:
                return project
        print("project named: " + projectName + " not found")
        exit(1)
    print("Query unsuccesful. Unable to get project")
    exit(1)

def UploadFile(udServer, workspace:json, project:json, folderPath:str, filePath:str):
    path = abspath(filePath)

    # create json data for the sas query
    filename = basename(path)
    filesize = getsize(path)
    fileData = {"filename": filename, "folder": folderPath, "filesize": filesize}
    jsonData = json.dumps(fileData)
    # get sas token
    res = udServer.query(workspace['id'] + "/" + project['id'] + "/_files/create", jsonData)
    if res is not None and res['success']:
        sas = res['sas']
    else:
        print("unable to obtain sas token for " + filename)
        print(res['message'])
        exit(1)

    if folderPath != '':
        sas_url="https://" + res['account'] + ".blob.core.windows.net/"+ res['container'] + "/" + workspace['id'] + "_" + project['id'] + "/" + folderPath + "/" + filename + sas
    else:
        sas_url="https://" + res['account'] + ".blob.core.windows.net/"+ res['container'] + "/" + workspace['id'] + "_" + project['id'] + "/" + filename + sas

    client = BlobClient.from_blob_url(sas_url)

    with open(path,'rb') as data:
        client.upload_blob(data)

def GetShareCode(udServer, workspace:json, project:json, folderPath:str, filePath:str, expire:double):
    path = abspath(filePath)
    filename = basename(path)
    fileData = {"projid": project['id'], "filename": filename, "folder": folderPath, "expiry": expire}
    jsonData = json.dumps(fileData)
    
    # create a share code
    res = udServer.query(workspace['id'] + "/sharecode/create", jsonData)
    if res is not None and res['success']:
        return res['id']
    else:
        print("unable to get sharecode for " + filename)
        print(res['message'])
        exit(1)

if __name__ == "__main__":

    usageStr = f"""
    ************************************************************
    Usage: {argv[0]} workspaceName projectName folderPath filePath [server] [username] [password] [apikey]


    ************************************************************
    workspaceName: The udCloud Workspace name where the file will be updloaded
    projectName:   The udCloud project name where the file will be uploaded
    folderPath:    A path if the file is updated to a folder in the udCloud project (use " " if no folder)
    filePath:      The path of the file to be uploaded
    server:        (optional) udCloud server to use for licencing and to download the project from, defaults to https://udcloud.euclideon.com
    username:      (optional) udCloud username
    password:      (optional) udCloud password
    apikey:        (optional) key to be used when logging in to the server. If not set interactive log in or username password will be used
    ************************************************************
            """
    if len(argv) < 3 or len(argv) > 6:
        print(usageStr)
        exit(1)

    posAppName = 0
    posWkspaceName = 1
    posProjectName = 2
    posFolderPath = 3
    posFilename = 4
    posServerPath = 5
    posUsername = 6
    posPassword = 7
    posAPIKey = 8

    if argv[posFolderPath] == ' ':
        folderPath = ''

    if len(argv) > posServerPath:
        serverPath = argv[posServerPath]
    else:
        serverPath = "https://udcloud.euclideon.com"

    if len(argv) > posAPIKey:
        apiKey = argv[posAPIKey]
    else:
        apiKey = None


    udSDK.LoadUdSDK("")
    context = udSDK.udContext()
    if apiKey is None:
        context.log_in_interactive(serverPath, "Python Uploader", "0.1")
    elif len(argv) > posPassword:
        context.log_in_legacy(argv[posUsername], argv[posPassword], appName="Python Uploader")
    else:
        context.connect_with_key(apiKey, serverPath, "Python Uploader", '0.1')

    udServer = udServerAPI(context)

    # Get workspace
    workspace = GetWorkspace(udServer, argv[posWkspaceName])

    # Get project
    project = GetProject(udServer, workspace, argv[posProjectName])

    # Upload the file to udCloud
    UploadFile(udServer, workspace, project, folderPath,  argv[posFilename])

    # Create a share code that does not expire
    expiry = 0.0 # 0.0 -> does not expire, expiry in hrs
    sharecode = GetShareCode(udServer, workspace, project, folderPath,  argv[posFilename], expiry)
    print(sharecode)
