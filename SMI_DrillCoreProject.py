import udSDK
import udSDKProject
import sys
from sys import argv
import requests
import os
import csv
import numpy as np

sys.setrecursionlimit(3000)

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

class BoreholeJob:
    surveyFileName = ""
    collarFileName = ""
    def __init__(self, collarFileName:str, surveyFileName:str):
        self.surveyFileName = surveyFileName
        self.collarFileName = collarFileName


if __name__ == "__main__":
    starraJob = BoreholeJob("D:/UQ SMI/boreholeData/Starra/STA_Collar_simp.csv",
                            "D:/UQ SMI/boreholeData/Starra/STA_Survey_simp.csv")
    cudJob = BoreholeJob("D:/UQ SMI/boreholeData/CUD5198_collar.csv",
                         "D:/UQ SMI/boreholeData/CUD5198_survey.csv")

    job = starraJob
    udSDK.LoadUdSDK("")
    context = udSDK.udContext()
    try:
        context.try_resume("https://udstream.euclideon.com", "pythonProjectDownloader", argv[1])
    except udSDK.UdException:
        context.Connect("https://udstream.euclideon.com", "pythonProjectDownloader", argv[1], argv[2])
    project = udSDKProject.udProject(context)
    #project.CreateInMemory("test")
    outFilePath = "./lineTestSibling.json"
    if os.path.exists(outFilePath):
        os.remove(outFilePath)
    project.CreateInFile("test", outFilePath)
    rootNode = project.GetProjectRoot()
    rootNode.SetMetadataInt("projectcrs", 28354)
    rootNode.SetMetadataInt("defaultcrs", 28354)
    surveyFolder = rootNode.create_child("Folder", "Survey")
    nextFolder = rootNode.create_child("Folder", "attempt")
    #collarFolder = surveyFolder.create_child("Folder", "Collars")
    #rootNode.create_child()
    loopCounter = 0
    boreholes = {}
    with open(job.collarFileName, newline='', encoding='utf8') as f:
        collarReader = csv.DictReader(f, delimiter=',')
        for row in collarReader:
            if loopCounter>100:
                break
            if not loopCounter % 100:
                pass
                #project.Save()
                #collarSubFolder = surveyFolder.create_child("Folder", f"Collars {loopCounter}-{loopCounter+100}")
                #project.Save()
            boreholes[row["HOLEID"]] = Borehole(row["HOLEID"], (float(row["EAST"]), float(row["NORTH"]),float(row["RL"])), float(row["DEPTH"]) )

            #poi = collarSubFolder.create_child("POI", row["HOLEID"])
            #poi.SetGeometry(udSDKProject.udProjectGeometryType.udPGT_Point,boreholes[row["HOLEID"]].collar)
            loopCounter += 1

    project.Save()

    lineFolder = surveyFolder.create_child("Folder", "Survey Lines")
    with open(job.surveyFileName, newline='') as f:
        surveyReader = csv.DictReader(f, delimiter=',')
        for row in surveyReader:
            hole = boreholes.get(row["HOLEID"])
            if hole is None:
                continue
            hole.depths.append(float(row["DEPTH"]))
            hole.azimuths.append(float(row["AZIMUTH"]))
            hole.dips.append(float(row["DIP"]))
    number = 1
    for hole in boreholes.values():
        print(f"calculating points for hole {number} {hole.name}")
        number = number + 1
        hole.calculate_points()
        line = lineFolder.create_child("POI", hole.name)
        line.SetGeometry(udSDKProject.udProjectGeometryType.udPGT_LineString, hole.linePoints)
project.Save()
