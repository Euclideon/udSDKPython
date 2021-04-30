import udSDK
import numpy as np
from camera import Camera
import random
udSDK.LoadUdSDK("")
from sys import argv
import matplotlib.pyplot as plt


class Sensor():
    pass

class LocalMap():
    def __init__(self, path):

        self.udContext = udContext
        self.renderContext = udSDK.udRenderContext(self.udContext)
        self.renderTarget = udSDK.udRenderTarget(renderContext=self.renderContext,context=self.udContext)
        self.camera = Camera(self.renderTarget)
        #self.camera = Camera(self.renderTarget)

        self.model = udSDK.udPointCloud(context=self.udContext, path=path)
        self.renderInstance = udSDK.udRenderInstance(self.model)
        self.renderInstance.set_transform_default()

    def do_render(self, pose):
        self.camera.position = pose[:3]
        settings = udSDK.udRenderSettings()
        settings.flags = udSDK.udRenderContextFlags.BlockingStreaming
        self.renderContext.Render(self.renderTarget, [self.renderInstance], renderSettings=settings)
        self.renderContext.Render(self.renderTarget, [self.renderInstance], renderSettings=settings)
        self.renderContext.Render(self.renderTarget, [self.renderInstance], renderSettings=settings)

    def make_estimate_depth(self, pose):
        """Given an estimated position, return the expected depth map for that pose"""
        self.do_render(pose)
        a = np.array(self.renderTarget.depthBuffer)
        a.resize([self.renderTarget.height, self.renderTarget.width])
        return a

    def make_estimate_colour(self, pose):
        """Given an estimated position, return the expected depth map for that pose"""
        self.do_render(pose)
        a = np.array(self.renderTarget.rgb_colour_buffer(), dtype=np.uint8)
        a.resize([self.renderTarget.height,self.renderTarget.width, 3])
        return a

class PoseEstimate():
    def __init__(self, position, rotation):
        self.position = tuple(position)
        self.rotation = tuple(rotation)
        self.score = None

    def evaluate_score(self, localMap, other:np.array):
        """
        basic difference comparison between a hypothesised location render and the data
        """
        im = abs(localMap.make_estimate_depth(self.position) - other)
        self.score = sum(sum(im))


class ParticleFilter():
    """Implementation of a particle filter for determining a submarine's pose
    Focus is on sensitivity to pitch due to pertubation by waves
    """
    def __init__(self, localMap:LocalMap, nGuesses:int):
        self.localMap = localMap
        #Initialise the filter as having a uniform distribution over the bounding box
        #of the localMap:
        self.localMap.camera.set_projection_perspective(far=200, near=0.1)
        self.poseEstimates = []
        #bboxMax = [(localMap.model.header.boundingBoxExtents[i] + localMap.model.header.boundingBoxCenter[i]) * localMap.model.header.scaledRange for i in range(3)]
        #bboxMin = [(localMap.model.header.boundingBoxExtents[i] - localMap.model.header.boundingBoxCenter[i]) * localMap.model.header.scaledRange for i in range(3)]
        bboxMax = [(localMap.model.header.boundingBoxExtents[i] +localMap.model.header.boundingBoxCenter[i]) * localMap.model.header.scaledRange + localMap.model.header.baseOffset[i] for i in range(3)]
        bboxMin = [(-localMap.model.header.boundingBoxExtents[i] +localMap.model.header.boundingBoxCenter[i]) * localMap.model.header.scaledRange + localMap.model.header.baseOffset[i] for i in range(3)]
        print(f"range: {bboxMin} - {bboxMax} ")
        for i in range(nGuesses):
            position = [random.uniform(bboxMin[i], bboxMax[i]) for i in range(3)]
            rotation = [0, 0, 0]
            self.poseEstimates.append(PoseEstimate(position, rotation))


    def anneal(self, imOther:np.array, nsteps = 5, sigmaStart=50):
        """Crude simulated annealing whereby estimates are updated according to a normal distribution about the best 50% of
        estimates ranked by score. Variance of the normal distributions are reduced each step such that consecutive guesses
        are closer to the """
        for iter in range(nsteps):
            sigma = sigmaStart/(iter+1)
            self.evaluate_scores(imOther)
            self.poseEstimates.sort(key=lambda x: x.score, reverse=False)
            print(f"best:{self.poseEstimates[0].position} score= {self.poseEstimates[0].score}")
            for i in range(len(self.poseEstimates)//2):
                #create a new estimate based on the top half of guesses
                position = [random.normalvariate(self.poseEstimates[i].position[ind], sigma) for ind in range(3)]
                self.poseEstimates[i+len(self.poseEstimates)//2] = PoseEstimate(position,(0,0,0))


    def update(self, sensorInput):
        pass

    def evaluate_scores(self, imOther:np.array):
        i=0
        for hypothesis in self.poseEstimates:
            #print(f"Processing guess {i}")
            i = i+1
            hypothesis.evaluate_score(localMap=self.localMap, other=imOther)

    def show_guesses(self):
        import matplotlib.pyplot as plt
        for guess in self.poseEstimates:
            #print(f"guess: {guess.position}")
            im = self.localMap.make_estimate_colour(guess.position)
            plt.imshow(im)
            plt.show()



class Agent():
    def __init__(self):
        self.accel = [0] * 6
        self.velocities = [0] * 6
        self.positions = [0] * 6

    def update_position(self, dt):
        dx = [v * dt for v in self.velocities]
        self.positions = [self.positions[i] + dx[i] for i in range(len(self.positions))]

    def update_velocities(self, dt):
        dv = [a * dt for a in self.accel]
        self.velocities = [self.positions[i] + dv[i] for i in range(len(self.positions))]


if __name__ == "__main__":

    _, username, password, server = argv
    udContext = udSDK.udContext()
    try:
        udContext.try_resume(username=username, applicationName="slamtestPython", url=server)
    except Exception as e:
        udContext.Connect(username=username, password=password,
                          applicationName="slamtestPython", url=server)

    #pose = [435238.310013, 6305902.369212, 168.763207,0,-25.40*np.pi/180, -43.43*np.pi/180 ]
    #pose = [0,0,0]
    #plt.imshow(im1)
    #plt.show()
    #original.renderTarget.plot_view()

    """
    pose = [435238.310013, 6305902.369212, 168.763207,0,0,0]
    original = LocalMap("Z:/MineGeoTech/All Working Datasets/Open Pit Mine 1/N_Wall_F1_1cm.uds")
    original.do_render(pose)
    im1 = original.make_estimate_depth(pose)
    new = LocalMap("Z:/MineGeoTech/All Working Datasets/Open Pit Mine 1/N_Wall_F2_1cm.uds")
    new.do_render(pose)
    im2 = new.make_estimate_depth(pose)
    """
    testChangeView = False
    if testChangeView:
        pose = [435360.173423, 6305988.331001,190.225068 ,0,0,0]
        original = LocalMap("Z:/MineGeoTech/All Working Datasets/Open Pit Mine 2/F5_March_2019_1cm.uds")
        original.do_render(pose)
        im1 = original.make_estimate_depth(pose)
        plt.imshow(im1)
        plt.show()
        new = LocalMap("Z:/MineGeoTech/All Working Datasets/Open Pit Mine 2/F5_October_2019_1cm.uds")
        new.do_render(pose)
        im2 = new.make_estimate_depth(pose)
        plt.imshow(im2)
        plt.show()
        comparison = (im2 - im1) / im1.mean()
        plt.imshow(comparison)
        plt.show()
        plt.hist(comparison)
        plt.show()

    random.seed(1234)
    #pose = [435360.173423, 6305988.331001, 190.225068, 0, 0, 0]
    #pose = [435372.604583, 6306060.431642, 173.295680, 0, 0, 0]
    pose = [435454.013167, 6306043.445617, 210.896315]
    map = LocalMap("Z:/MineGeoTech/All Working Datasets/Open Pit Mine 2/F5_March_2019_1cm.uds")
    #map = LocalMap("C:/git/udSDKSamples/features/convertcustomdata/DirCube.uds")
    particleFilter = ParticleFilter(map,100)
    imOther = map.make_estimate_depth(pose)
    particleFilter.evaluate_scores(imOther)
    particleFilter.poseEstimates.sort(key=lambda x: x.score, reverse=False)
    particleFilter.anneal(imOther, 50, sigmaStart=50)
    best = particleFilter.poseEstimates[0]
    print(f"best:{best.position} score= {particleFilter.poseEstimates[0].score}")
    print(f"worst:{particleFilter.poseEstimates[-1].position} score= {particleFilter.poseEstimates[-1].score}")
    print(f"true value: {pose}")
    print(f"Residual error = {((best.position[0]-pose[0])**2+(best.position[1]-pose[1])**2+(best.position[2]-pose[2])**2)**0.5}m")

    plt.figure(1)
    plt.subplot()
    plt.imshow(map.make_estimate_colour(best.position))
    plt.show()
    #particleFilter.show_guesses()
    #from scipy import signal
    #res =signal.correlate2d(im1,im2)



    #plt.imshow(im1)
    #plt.show()
    pass
    #new = LocalMap("Z:/MineGeoTech/All Working Datasets/Open Pit Mine 1/N_Wall_F2_1cm.uds")
    #fig = plt.