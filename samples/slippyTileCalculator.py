# utility for calculating the approximate number of slippy tiles to cover a N/E oriented uds

import udSDK
import math
import os

udSDK.LoadUdSDK("")

context = udSDK.udContext()
context.log_in("username", "password", serverPath="https://udstream.euclideon.com", appName="areaCalculator")
z54Base = "M:/ELVIS/z54_towns_colour/"
z55Base = "M:/ELVIS/z55_towns_colour/"


def calculateApproxTileNumber(baseDirs):
  lat = 25
  zoomLevel = 19
  C = 40075016.686 # circumference of earth
  tileWidth = C * math.cos(lat * math.pi/180) / (2**zoomLevel)
  tileArea = tileWidth**2
  totalArea = 0
  for dir in baseDirs:
    for f in os.listdir(dir,):
      pc = udSDK.udPointCloud(dir + f, context)
      size = [0, 0, 0]
      for i in range(3):
        size[i] = pc.header.boundingBoxExtents[i] * pc.header.scaledRange
      totalArea += size[0] * size[1]
  return totalArea/tileArea

print(calculateApproxTileNumber([z54Base, z55Base]))


