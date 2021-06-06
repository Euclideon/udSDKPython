"""
Due to scope creep this tool should really be called project copy/ downlaod as this handles both
local and web hosted files.

Not all objects will be supported, currently the project is traversed and:
    -all udProjectNodes with uris are copied and redirected to a relative location to the download folder
    -the .mtl files associated with an obj are downloaded, the .mtl is then parsed for certain (not necessarily all) textures and downloaded
    -images within projecNode descriptions are downloaded and redirected (though general links are preserved as is)

Currently if a file is referenced multiple times in a project then a copy of this file is made in the
output folder structure for each reference: an improvement would be to

"""

from pathlib import Path

import udSDK
import udSDKProject
from sys import argv, exit
import shutil

import requests

downloadedFiles = {}
class ProjectDownloader(udSDKProject.udProjectNode):
    """
    specialised version of udProjectNode
    """
    newDir = ''
    skipUDS = True
    absPath = ""
    madeLocal = False
    # @uri.setter
    # def uri(self, uri):
    #     super.uri = uri
    #     self.madeLocal = True

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
    def scrape_mtl(self, fileName, url):
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
                            url = "/".join(url.split('/')[:-1]) + '/' + texName
                            try:
                                print(url)
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

        print(f"Copying {url} to {newLocation}")
        #case for web requests:
        success = True
        try:
            print(url)
            print("1st uri:", self.uri)
            res = requests.get(url)
            if res.status_code == 200:
                Path(self.parent.make_local_path()).mkdir(parents=True, exist_ok=True)
                with open(newLocation, mode='wb') as f:
                    f.write(res.content)
            else:
                print(f"failed to get {url}, code: {res.status_code}")
        except: #requests.exceptions.InvalidSchema:
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
            self.scrape_mtl(newLocation, url)
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
                                url = '/'.join(oldurl.split('/')[:-1])+'/'+line.split(' ')[-1].rstrip('\n')
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
    if len(argv) < 5:
        print(f"""
************************************************************
Usage: {argv[0]} username password projectUuid[skipUDS]
 

************************************************************
username:     Your Euclideon username
password:     Your Euclideon password
inputPath:    This can be a local path or UUID e.g. b8bda426-a3b1-4359-8eed-d8d692928c2e
outputPath:   The directory to save the project package to
skipUDS:      (optional) Skip copying of any UDS files
************************************************************
        """)
        exit(0)
    print(__file__)
    udSDK.LoadUdSDK("./udSDK")
    context = udSDK.udContext()
    #serverURL = "https:/stg-ubu18.euclideon.com"
    serverURL = "https://udstream.euclideon.com"
    try:
        context.try_resume(serverURL,"pythonProjectDownloader", argv[1])
    except udSDK.UdException:
        context.Connect(serverURL, "pythonProjectDownloader", argv[1], argv[2])
    project = udSDKProject.udProject(context)
    uuid = argv[3]
    ext = uuid.split('.')[-1]
    if(ext=='json' or ext == 'udjson'):
        project.LoadFromFile(uuid)
    else:
        project.LoadFromServer(uuid)
    filename = f"{argv[4]}/downloadedProject.json"
    print(f"{argv}, {len(argv)}")
    if len(argv) > 5:
        skipUDS = True
    else:
        skipUDS = False
    download_project(project, filename, skipUDS)
    pass