import udSDK
import random
import numpy as np
import math
from camera import Camera
from PIL import Image
udSDK.LoadUdSDK("")

class LocalMap():
    def __init__(self, path):
        self.udContext = udSDK.udContext()
        url = "https://stg-ubu18.euclideon.com"
        try:
            self.udContext.try_resume(username="Username",  applicationName="imageGenerator", url=url)
        except Exception as e:
            self.udContext.Connect(username="Username", password="Password", applicationName="imageGenerator", url=url)

        self.renderContext = udSDK.udRenderContext(self.udContext)
        self.renderTarget = udSDK.udRenderTarget(renderContext=self.renderContext,context=self.udContext)
        self.camera = Camera(self.renderTarget)

        self.model = udSDK.udPointCloud(context=self.udContext, path=path)
        self.renderInstance = udSDK.udRenderInstance(self.model)
        self.renderInstance.set_transform_default()
        self.renderInstance.scaleMode = 'minDim'
    
    def do_rotate(self, waypoint, direction):
        #vec = self.camera.rotate_polar(self.camera.facingDirection, direction, 0)
        #self.camera.look_at(vec)
        self.camera.set_rotation(waypoint[0], waypoint[1], waypoint[2], 0,0, direction)

    def do_render(self, pose):
        self.camera.position = pose[:3]
        settings = udSDK.udRenderSettings()
        settings.flags = udSDK.udRenderContextFlags.BlockingStreaming
        self.renderContext.Render(self.renderTarget, [self.renderInstance], renderSettings=settings)
        self.renderContext.Render(self.renderTarget, [self.renderInstance], renderSettings=settings)
        self.renderContext.Render(self.renderTarget, [self.renderInstance], renderSettings=settings)
        self.renderContext.Render(self.renderTarget, [self.renderInstance], renderSettings=settings)
        self.renderContext.Render(self.renderTarget, [self.renderInstance], renderSettings=settings)

    def write_to_image(self, name='a.png'):
        arr = []
        #convert colour buffer from BGRA to RGBA
        #i.e. we are switching the B and R channels by bit shifting
        for pix in self.renderTarget.colourBuffer:
            pix = np.int32(pix)
            pix=(pix>>24 & 0xFF)<<24 |(pix>>16 & 0xFF)<<0 |(pix>>8 & 0xFF)<<8 | (pix&0xFF)<<16
            arr.append(pix)
        arr = np.array(arr)
        Image.frombuffer("RGBA", (self.renderTarget.width, self.renderTarget.height), arr.flatten(), "raw", "RGBA", 0, 1).save(name)

if __name__ == "__main__":
    waypoints = [(0,0,0), (1,0,0), (2,0,0)]
    map = LocalMap("https://models.euclideon.com/Melbourne_75mm.uds")
    number = 0
    # directions use pi to look left, right and center
    directions = [math.pi/2, -math.pi/2, 0]
    for waypoint in waypoints:
        number+=1
        for direction in directions:
            map.do_rotate(waypoint, direction)
            map.do_render(waypoint)
            map.write_to_image(str(number) + "_" + str(direction) + ".png")
