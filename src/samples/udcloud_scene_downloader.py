"""
Sample Program using udProject interface to copy all files in a udCloud scene into a single local location.

Not all objects will be supported, currently the project is traversed and:
    -all udProjectNodes with uris are copied and redirected to a relative location to the download folder
    -the .mtl files associated with an obj are downloaded, the .mtl is then parsed for certain (not necessarily all) textures and downloaded
    -images within projectNode descriptions are downloaded and redirected (though general links are preserved as is)
"""

import shutil
from pathlib import Path
from sys import argv, exit

import requests

import udSDK
import udSDKProject

downloadedFiles = {}
class ProjectDownloader(udSDKProject.udProjectNode):
    """
    specialised version of udProjectNode
    """
    newDir = ''
    skipUDS = True
    absPath = ""
    def make_local_path(self):
        if self.parent is None:
            return self.newDir + "/content"
        else:
            return f"{self.parent.make_local_path()}/{str(self.pName)[2:-1]}"
    def make_absolute_path(self):
        if self.absPath is not None:
            return self.absPath
        else:
            return self.parent.make_absolute_path() + self.make_local_path()

    # Find and download material files from obj.
    def scrape_mtl(self, fileName):
        """
        This attempts to look for texture files located in the .mtl file included with wavefront objs
        and downloads them to the appropriate location
        """
        print(f"reading mtl file {fileName}")
        try:
            with open(fileName, 'r') as f:
                textureNames = ["map_Kd", "map_Ka", "map_Ks", "map_bump", "bump"]
                for line in f:
                    for name in textureNames:
                        if line.find(name) != -1:
                            texName = line.split(" ")[-1].strip()
                            directory = self.parent.make_local_path() + "/" + "/".join(texName.split('/')[:-1])
                            newLocation = self.parent.make_local_path() + "/" + texName
                            url = "/".join(self.uri.split('/')[:-1]) + '/' + texName
                            try:
                                res = requests.get(url)
                                print(f"Getting texture {url}...")
                                if res.status_code == 200:
                                    p = Path(directory)
                                    p.mkdir(parents=True, exist_ok=True)
                                    with open(newLocation, mode='wb') as g:
                                        g.write(res.content)
                            except Exception as e:
                                print(e)
                                p = Path(directory)
                                p.mkdir(parents=True, exist_ok=True)
                                shutil.copy(url, newLocation)
        except Exception as e:
            print(f"failed to scrape mtl: {e}")

    def download_resource_local(self, url:str, ext=None):
        if ext is None:
            ext = self.uri.split('.')[-1]
        newFileName = "".join(self.uri.split('/')[-1].split('.')[:-1])
        newLocation = self.parent.make_local_path() + '/' + newFileName + '.' + ext
        #handle duplicating instances of objects
        if downloadedFiles.get(url) is None:
            downloadedFiles[url] = newLocation
        else:
            print(f"duplicate file {url}, skipping download")
            self.uri = downloadedFiles[url]
            return

        print(f"Copying  {url} to {newLocation}")
        #case for web requests:
        success = True
        try:
            res = requests.get(url)
            if res.status_code == 200:
                Path(self.parent.make_local_path()).mkdir(parents=True, exist_ok=True)
                with open(newLocation, mode='wb') as f:
                    f.write(res.content)
            else:
                print(f"failed to get {url}, code: {res.status_code}")
        except: 
            #requests.exceptions.InvalidSchema:
            #Try to treat the uri as a local address instead
            Path(self.parent.make_local_path()).mkdir(parents=True, exist_ok=True)
            if url[0] == '.':#relative file path
                l = self.project.filename.split('/')[1:-1]
                l.append("".join(url[2:].split('.')[:-1]))
                uri = '/'.join(l)
            else:
                uri = ".".join(self.uri.split('.')[:-1])+'.'+ext
            try:
                shutil.copy(uri, newLocation)
            except Exception as e:
                print(f"failed copy of {uri} : {e}")
                success = False
        if success and ext == "mtl":
            self.scrape_mtl(newLocation)
        if success:
            self.uri = self.make_local_path()

    def make_local(self, doChildren=True, doSiblings=True):
        if self.uri is not None and self.uri != "":
            fn = self.uri.split('.')
            ext = fn[-1]
            if not (self.skipUDS and ext =='uds'):
                #process textures for objs
                oldurl = self.uri
                self.download_resource_local(self.uri, None)
                if fn[-1] == "obj":
                    with open(self.uri,'r') as obj:
                        for line in obj:
                            if line.find('mtllib') !=-1:
                                url = '/'.join(oldurl.split('/')[:-1])+'/'+line.split(' ')[-1]
                                print(f"processing mtl: {url}...")
                                self.download_resource_local(url, ext='mtl')

                    #ext = "mtl"
                    #url = '.'.join(self.uri.split('.')[:-1]) + "." + ext
                    #self.download_resource_local(url, ext=ext)
            else:
                print(f"Skipping UDS file {self.uri}")

        description = self.GetMetadataString("description", None)
        #This handles images embedded in markdown: TODO refactor this into a call to download
        if description is not None:
            import re
            exp = re.compile('!\[(.*?)\]\((.*?)\)')
            searchInd = 0
            newDescription = []
            while searchInd < len(description):
                match = exp.search(description, searchInd)
                if match is None:
                    newDescription.append(description[searchInd:])
                    break
                newDescription.append(description[searchInd:match.start()])
                Path(self.make_local_path()).mkdir(parents=True, exist_ok=True)
                newPath = self.make_local_path() + '/' + match.group(2).replace('\\','/').split('/')[-1]
                try:
                    res = requests.get(match.group(2))
                    if res.status_code == 200:
                        with open(newPath) as f:
                            f.write(res.content)
                    else:
                        print(f"failed to get embedded image {match.group(2)}")
                except:# requests.exceptions.InvalidSchema:
                    #try:
                    shutil.copy(match.group(2), newPath)
                    #except:
                        #print(f"failed to copy embedded image {match.group(2)} to {newPath}")
                newEntry = f'![{match.group(1)}]({newPath})'
                searchInd = match.end()
                newDescription.append(newEntry)
            print("".join(newDescription))
            self.SetMetadataString("description", "".join(newDescription))


        if self.firstChild is not None and doChildren:
            firstChild = self.firstChild
            firstChild.__class__ = self.__class__
            firstChild.skipUDS = self.skipUDS
            firstChild.make_local()
        if self.nextSibling is not None and doSiblings:
            nextSibling = self.nextSibling
            nextSibling.__class__ = self.__class__
            nextSibling.skipUDS = self.skipUDS
            nextSibling.make_local()


def download_project(project:udSDKProject.udProject, newFilename:str, skipUDS=False):
    project.SaveToFile(newFilename)
    rootNode = project.GetProjectRoot()
    rootNode.__class__ = ProjectDownloader
    rootNode.skipUDS = skipUDS

    rootNode.newDir = "/".join(newFilename.split("/")[:-1])
    rootNode.absPath = "/".join(newFilename.split("/")[:-1])
    rootNode.make_local()
    project.Save()


if __name__ == "__main__":

    usageStr = f"""
    ************************************************************
    Usage: {argv[0]} username password projectUuid [skipUDS] [server] [apikey]


    ************************************************************
    sharecode:    Share code of project to be copied (e.g. euclideon:project/ZFsVZv1bEE614qE1tnfQJw/euclideon/wwgGSKacEe2wDAENV2uyg), or path to local .udjson file
    outputPath:   Output name of the project to be downloaded/ copied, additional files will be copied to a new content folder in the same directory
    skipUDS:      (optional) Skip copying of any UDS files (1=True, other=False)
    server:       (optional) udCloud server to use for licencing and to download the project from, defaults to https://udcloud.euclideon.com
    apikey:       (optional) key to be used when logging in to the server. If not set interactive log in through browser will be used
    ************************************************************
            """
    if len(argv) < 3 or len(argv) > 6:
        print(usageStr)
        exit(1)

    posAppName = 0
    posShareCode = 1
    posOutputPath = 2
    posSkipUDS = 3
    posServerPath = 4
    posAPIKey = 5 # if not provided then use interactive log in instead

    if(argv[posSkipUDS] == '1'):
        skipUDS = True
    else:
       skipUDS = False


    if len(argv) > posServerPath - 1:
        serverPath = argv[posServerPath]
    else:
        serverPath = "https://udcloud.euclideon.com"

    if len(argv) > posAPIKey - 1:
        apiKey = argv[posAPIKey]
    else:
        apiKey = None

    context = udSDK.udContext()
    if apiKey is None:
        context.log_in_interactive(serverPath, "Python Downloader", "0.2")
    else:
        context.connect_with_key(apiKey, serverPath, "Python Downloader", '0.2')

    projectCode = argv[posShareCode].split(':')[-1].split('/')
    uuid = projectCode[0]
    groupID = projectCode[1] + '/' + projectCode[2]
    project = udSDKProject.udProject()
    project.LoadFromServer(uuid, groupID)
    download_project(project, argv[posOutputPath], skipUDS)
