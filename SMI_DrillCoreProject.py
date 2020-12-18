import udSDK
import udSDKProject
import sys
from sys import argv
import requests
import os
import csv
import numpy as np

sys.setrecursionlimit(5000)



def make_places_project(boreholes:dict):
    project = udSDKProject.udProject(context)
    outFilePath = "./SMICustomTestsmall.json"
    if os.path.exists(outFilePath):
        os.remove(outFilePath)
    #project.CreateInFile("test", outFilePath)
    project.LoadFromFile()
    # placeFolder = surveyFolder.create_child("Folder", "Place test")
    placeLayer = project.rootNode.create_child("SMI", "Starra")
    project.rootNode.SetMetadataInt("projectcrs", 28354)
    project.rootNode.SetMetadataInt("defaultcrs", 28354)
    placeLayer.__class__ = SMIBoreholeMarkerLayer
    placeLayer.on_cast()
    placeLayer.pin = "D:/git/vaultsdkpython/drill_hole.jpg"
    placeLayer.SetGeometry(udSDKProject.udProjectGeometryType.udPGT_Point,)
    # placeLayer.model.url = "D:/git/vaultsdkpython/2.T-Rex.obj"
    for hole in boreholes.values():
        print(f"making collar place: {hole.name}")
        if not hole.lineCalculated:
            hole.calculate_points()
        placeLayer.add_item(hole.name, hole.linePoints, 1)
    print("done adding places")
    project.Save()


class BoreholeMarker(udSDKProject.ProjectArrayItem):
    def __init__(self, parent:udSDKProject.PlaceLayerNode, index:int, nPoints=1):
        super().__init__(parent, index, arrayName="bh")
        self.nPoints = nPoints

    @property
    def coordinates(self):
        return tuple([self.get_property(f"crds[{i}]" for i in range(self.nPoints * 3))])
    @coordinates.setter
    def coordinates(self, coordinates):
        self.nPoints = len(coordinates)//3
        self.set_property("n",self.nPoints,type=int)
        for i in range(len(coordinates)):
            self.set_property(f"crds[{i}]", coordinates[i], type=float)



class SMIBoreholeMarkerLayer(udSDKProject.ArrayLayerNode):
    def __init__(self, parent):
        super().__init__(parent, BoreholeMarker)


    def add_item(self, name, coordinates, count):
        place = BoreholeMarker(self, len(self))
        place.count = count
        place.name = name
        place.coordinates = coordinates
        self._arrLength += 1
        #self.places.append(place)

    def on_cast(self):
        self.arrayItemType = BoreholeMarker

class Borehole:
    def __init__(self, name:str, collarPosition:tuple, finalDepth):
        self.depths = []
        self.finalDepth = finalDepth
        self.dips = []
        self.azimuths = []
        self.name = name
        self.collar = collarPosition
        self.linePoints = []
        for c in collarPosition:
            self.linePoints.append(c)
        self.lineCalculated = False

    def calculate_points(self):
        self.depths.append(self.finalDepth)
        for i in range(len(self.depths)-1):
            dDepth = self.depths[i+1] - self.depths[i]
            phi = np.pi/2-self.dips[i]*np.pi/180
            theta = np.pi/2-self.azimuths[i]*np.pi/180
            dx = dDepth * np.cos(theta) * np.sin(phi)
            dy = dDepth * np.sin(theta) * np.sin(phi)
            dz = dDepth * np.cos(phi)
            self.linePoints.append(self.linePoints[-3]+dx)
            self.linePoints.append(self.linePoints[-3]+dy)
            self.linePoints.append(self.linePoints[-3]+dz)
        self.lineCalculated = True

class BoreholeJob:
    surveyFileName = ""
    collarFileName = ""
    def __init__(self, collarFileName:str, surveyFileName:str):
        self.surveyFileName = surveyFileName
        self.collarFileName = collarFileName
        self.boreholes = {}
        self.collarsRead = False

    def make_collar_map(self):
        """

        """
        loopCounter = 0
        with open(self.collarFileName, newline='', encoding='utf8') as f:
            collarReader = csv.DictReader(f, delimiter=',')
            for row in collarReader:
                if loopCounter > 4000:
                    break
                if not loopCounter % 100:
                    pass
                    # project.Save()
                    # collarSubFolder = surveyFolder.create_child("Folder", f"Collars {loopCounter}-{loopCounter+100}")
                    # project.Save()
                self.boreholes[row["HOLEID"]] = Borehole(row["HOLEID"],
                                                    (float(row["EAST"]), float(row["NORTH"]), float(row["RL"])),
                                                    float(row["DEPTH"]))

                # poi = collarSubFolder.create_child("POI", row["HOLEID"])
                # poi.SetGeometry(udSDKProject.udProjectGeometryType.udPGT_Point,boreholes[row["HOLEID"]].collar)
                loopCounter += 1
        self.collarsRead = True


if __name__ == "__main__":
    starraJob = BoreholeJob("D:/UQ SMI/boreholeData/Starra/STA_Collar_simp.csv",
                            "D:/UQ SMI/boreholeData/Starra/STA_Survey_simp.csv")
    cudJob = BoreholeJob("D:/UQ SMI/boreholeData/CUD5198_collar.csv",
                         "D:/UQ SMI/boreholeData/CUD5198_survey.csv")

    job = cudJob
    udSDK.LoadUdSDK("")
    context = udSDK.udContext()
    try:
        context.try_resume("https://udstream.euclideon.com", "pythonProjectDownloader", argv[1])
    except udSDK.UdException:
        context.Connect("https://udstream.euclideon.com", "pythonProjectDownloader", argv[1], argv[2])
    project = udSDKProject.udProject(context)
    #project.CreateInMemory("test")
    outFilePath = "./lineTest.json"
    if os.path.exists(outFilePath):
        os.remove(outFilePath)
    project.CreateInFile("test", outFilePath)
    rootNode = project.GetProjectRoot()
    rootNode.SetMetadataInt("projectcrs", 28354)
    rootNode.SetMetadataInt("defaultcrs", 28354)
    surveyFolder = rootNode.create_child("Folder", "Survey")
    #nextFolder = rootNode.create_child("Folder", "attempt")
    #collarFolder = surveyFolder.create_child("Folder", "Collars")
    #rootNode.create_child()
    job.make_collar_map()

    project.Save()
    ##Logic for generating lines of interest from borehole centrelines:
    doPOILines = False

    lineFolder = surveyFolder.create_child("Folder", "Survey Lines")
    with open(job.surveyFileName, newline='') as f:
        surveyReader = csv.DictReader(f, delimiter=',')
        for row in surveyReader:
            hole = job.boreholes.get(row["HOLEID"])
            if hole is None:
                continue
            hole.depths.append(float(row["DEPTH"]))
            hole.azimuths.append(float(row["AZIMUTH"]))
            hole.dips.append(float(row["DIP"]))
    number = 1
    for hole in job.boreholes.values():
        print(f"calculating points for hole {number} {hole.name}")
        number = number + 1
        hole.calculate_points()
        if doPOILines:
            line = lineFolder.create_child("POI", hole.name)
            line.SetGeometry(udSDKProject.udProjectGeometryType.udPGT_LineString, hole.linePoints)

    #places test for locating the collars:
    placesTest = True
    if placesTest:
        make_places_project(job.boreholes)
project.Save()

