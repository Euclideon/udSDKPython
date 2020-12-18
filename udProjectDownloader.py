from pathlib import Path

import udSDK
import udSDKProject
from sys import argv, exit

import requests

class ProjectDownloader(udSDKProject.udProjectNode):
    """
    specialised version of udProjectNode
    """
    def make_local_path(self):
        if self.parent is None:
            return "./content"
        else:
            return f"{self.parent.make_local_path()}/{str(self.pName)[2:-1]}"
    def scrape_mtl(self, fileName):
        """
        This attempts to look for texture files located in the .mtl file included with wavefront objs
        and downloads them to the appropriate location
        """
        with open(fileName, 'r') as f:
            for line in f:
                if line.find("map_Kd") !=-1:
                    texName = line.split(" ")[-1].strip()
                    url = "/".join(str(self.pURI)[2:].split('/')[:-1]) +'/' + texName
                    res = requests.get(url)
                    print(f"Getting texture {url}...")
                    if res.status_code == 200:
                        with open(self.parent.make_local_path() + "/" + texName, mode='wb') as g:
                            g.write(res.content)

    def download_resource_local(self, url:str, ext=None):
        if ext is None:
            ext = '.' + str(self.pURI).split('.')[-1][:-1]
        print(f"Getting: {url}")
        res = requests.get(url)
        if res.status_code == 200:
            newFileName = str(self.pURI).split('/')[-1][:-5] + ext
            Path(self.parent.make_local_path()).mkdir(parents=True, exist_ok=True)
            with open(self.parent.make_local_path() + "/" + newFileName, mode='wb') as f:
                f.write(res.content)
            if ext ==".mtl":
                self.scrape_mtl(self.parent.make_local_path() + "/" + newFileName)
            self.set_uri(self.make_local_path())
        else:
            print(f"failed to get {url}, code: {res.status_code}")

    def make_local(self, doChildren=True, doSiblings=True):
        if self.pURI is not None:
            fn = str(self.pURI)[-5:-1]
            ext = fn
            url = str(self.pURI)[2:-5] + ext
            self.download_resource_local(url, fn)

            #process textures for objs
            if fn == ".obj":
                ext = ".mtl"
                url = str(self.pURI)[2:-5] + ext
                self.download_resource_local(url, ext=ext)

        if self.firstChild is not None and doChildren:
            firstChild = self.firstChild
            firstChild.__class__ = self.__class__
            firstChild.make_local()
        if self.nextSibling is not None and doSiblings:
            nextSibling = self.nextSibling
            nextSibling.__class__ = self.__class__
            nextSibling.make_local()


def download_project(project:udSDKProject.udProject, filename:str):
    project.SaveToFile(filename)
    rootNode = project.GetProjectRoot()
    rootNode.__class__ = ProjectDownloader
    rootNode.make_local()
    project.Save()


if __name__ == "__main__":
    if len(argv) != 5:
        print(f"Usage: {argv[0]} username password projectUuid")
        print("Username: Euclideon Username")
        print("Password: Euclideon Password")
        print("project projectFile: e.g. b8bda426-a3b1-4359-8eed-d8d692928c2e")
        print("download directory")
        exit(0)
    udSDK.LoadUdSDK("")
    context = udSDK.udContext()
    try:
        context.try_resume("https://udstream.euclideon.com","pythonProjectDownloader", argv[1])
    except udSDK.UdException:
        context.Connect("https://udstream.euclideon.com", "pythonProjectDownloader", argv[1], argv[2])
    project = udSDKProject.udProject(context)
    uuid = argv[3]
    ext = uuid.split('.')[-1]
    if(ext=='json' or ext == 'udjson'):
        project.LoadFromFile(uuid)
    else:
        project.LoadFromServer(uuid)
    filename = f"{argv[4]}/downloadedProject.json"
    download_project(project, filename)
    pass