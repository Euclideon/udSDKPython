import cv2

import udSDK
import numpy as np
from camera import Camera
import random
udSDK.LoadUdSDK("")
from sys import argv
import matplotlib.pyplot as plt
import cv2 as cv
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
    def set_projection_ortho(self, viewWidth):
        viewHeight = viewWidth * self.camera.renderTarget.height / self.camera.renderTarget.width
        self.camera.set_projection_ortho(-viewWidth/2, viewWidth, viewHeight/2, -viewHeight/2, 0,500)

    def do_render(self, pose):
        #self.camera.position = pose[:3]
        if pose is not None:
            self.camera.set_rotation(*pose)
        else:
            self.camera.from_udStream()

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

    def make_estimate_canny(self, pose, blurK=9, cannyLower=100, cannyUpper=200):
        colour = self.make_estimate_colour(pose)
        #depth = self.make_estimate_depth(pose)

        grayblurred = cv.cvtColor(cv.medianBlur(colour, blurK),cv.COLOR_BGR2GRAY)
        return cv.Canny(grayblurred, cannyLower, cannyUpper)

    def make_estimate_canny_depth(self, pose, blurK=9, cannyLower=100, cannyUpper=200, minDist=130):
        depth = self.make_estimate_depth(pose)
        #grayblurred = cv.cvtColor(cv.medianBlur(depth, blurK),cv.COLOR_BGR2GRAY)
        depth = depth - np.min(depth)
        depth = depth/np.max(depth) *255
        depth = depth.astype('uint8')
        #thresh = depth * (depth > minDist)
        ret = cv.Canny(depth, cannyLower, cannyUpper)
        return ret

    def make_polygons(self, morph, colour=None):
        contours, _ = cv2.findContours(morph, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        polys = []
        #return the polys in decending order of area
        contours.sort(key = lambda a: cv2.contourArea(a), reverse=True)
        for cnt in contours:
            epsilon = 0.01 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            if colour is not None:
                cv2.drawContours(colour, [approx], 0, (255, 1, 1), 3)
            polys.append(approx)
        return polys

    def normalize_depth(self, depth, nstd=3):
        #we don't want to take values of 1 into account when analysing the depth buffer:
        a = np.where(depth==1, np.nan, depth)
        #remove outlier pixels:
        mean = np.nanmean(a)
        std = np.nanstd(a)
        dist = np.abs(a - mean)
        b = np.where(dist > nstd * std, np.nan, a)
        b = b - np.nanmin(b)
        return b/np.nanmax(b) *100


    def make_morphological_polygons(self, pose, minDist=0, maxDist=70, kernelSize=5, nstd=3, depth=None, plotAxis=plt.gca()):
        """
        generates a list of polygons from the contours of the depth buffer after applying a morphological filter
        @parameter pose: the 6DOF pose of the camera
        @parameter minDist: the minimum distance from the camera in %
        @parameter maxDist: the maximum distance from the camera in %
        @parameter kernelSize: the size of the kernel used when applying a morphological filter
        """
        if depth is None:
            depth = self.make_estimate_depth(pose)
            depth = self.normalize_depth(depth, nstd=nstd) #remove outliers and rescale depth to
        thresh = (depth > minDist) & (depth < maxDist)
        expandSelection = True
        if expandSelection:
            morph = cv2.morphologyEx(thresh.astype('uint8'), cv2.MORPH_ERODE, np.ones([kernelSize, kernelSize]))
            morph = cv2.morphologyEx(morph, cv2.MORPH_DILATE, np.ones([kernelSize+2, kernelSize+2]))
        else:
            morph = cv2.morphologyEx(thresh.astype('uint8'), cv2.MORPH_OPEN, np.ones([kernelSize, kernelSize]))
        plotMorph = True
        if plotMorph:
            #fig = plt.figure()
            #plotAxis.title = f"morph {minDist}-{maxDist}"
            plotAxis.imshow(morph)
        #colour = self.make_estimate_colour(pose)
        colour = None
        polys = self.make_polygons(morph, colour)
        pass
        return polys

    def layeredMorphPolygons(self, pose, nSteps=5, subplot=plt.gca(), depth=None):
        stepSize=100.0/nSteps
        polys = []
        for i in range(nSteps-1): #we will ignore the last step as this is mostly shadows/noise from previous layers
            minDist=i * stepSize
            maxDist=(i+1)*stepSize
            polys = polys + self.make_morphological_polygons(pose, minDist, maxDist, kernelSize=10)
        polys.sort(key = lambda a: cv2.contourArea(a), reverse=True)
        makePolyPlot = True
        if makePolyPlot:
            plt.figure()
            self.plot_polygons_colour(polys)
        return polys

    def plot_polygons_colour(self, polys, ax=plt.gca()):
        colour = self.make_estimate_colour(pose)
        for cnt in polys:
            epsilon = 0.01 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            cv2.drawContours(colour, [approx], 0, (255, 1, 1), 3)
        ax.imshow(colour)

    def create_vis(self,pose=None, nSteps=3):
        """
        creates a matplotlib window with the appropriate number of subfigures
        """
        from matplotlib.backend_tools import ToolBase
        class NewTool(ToolBase):
            def event(self, sender, event, data):
                pass
        # one for each morph level:
        fig = plt.figure()
        tm = fig.canvas.manager.toolmanager
        tm.add_tool("newtool", NewTool)
        fig.canvas.manager.toolbar.add_tool(tm.get_tool("newtool"), "toolgroup")
        self.update_figure(nSteps, pose, fig)
        # vis = LocalMap(
        # "https://storage.googleapis.com/72ac5e706bbf4b1f99acc2ced6cf454a/nsw-ausgrid-2018/NSW_Ausgrid_2018_Bondi.uds")
        #pose = [332351.701542, 6245005.938774, 417.148115, np.pi / 2, 0, 0]
    def update_figure(self, nSteps, pose = None, fig=plt.gcf()):
        nstd = 3  # number of standard deviations
        subplts = fig.subplots((nSteps) // 2 + 1, 2)
        depth = self.make_estimate_depth(pose)
        depth = self.normalize_depth(depth, nstd=nstd)  # remove outliers and rescale depth to
        stepSize = 100.0 / nSteps
        polys = []
        for i in range(nSteps - 1):  # we will ignore the last step as this is mostly shadows/noise from previous layers
            minDist = i * stepSize
            maxDist = (i + 1) * stepSize
            ax = subplts.flatten()[i]
            polys = polys + self.make_morphological_polygons(pose, minDist, maxDist, kernelSize=10, depth=depth,plotAxis=ax)
        polys.sort(key=lambda a: cv2.contourArea(a), reverse=True)
        self.plot_polygons_colour(polys, subplts.flatten()[i+1])


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

def write_polygon_file(polys):
    from array import array
    with open("C:/testoutputs/cvOut.txt", "wb") as f:
        projFloat = array('d', [*m.renderTarget.GetMatrix(udSDK.udRenderTargetMatrix.Camera),
                                *m.renderTarget.GetMatrix(udSDK.udRenderTargetMatrix.Projection),
                                m.renderTarget.width, m.renderTarget.height])
        projFloat.tofile(f)
        for poly in polys:
            for point in poly:
                f.write(f"{point[0, 0]},{point[0, 1]},".encode('utf8'))
            f.seek(-1, 2)
            f.write('\n'.encode('utf8'))
        f.write('\0'.encode('utf8'))



if __name__ == "__main__":

    _, username, password, server = argv
    udContext = udSDK.udContext()
    try:
        udContext.try_resume(username=username, applicationName="slamtestPython", url=server)
    except Exception as e:
        udContext.connect_legacy(username=username, password=password,
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
    testSceneSeg = True
    if testSceneSeg:
        m = LocalMap("https://storage.googleapis.com/72ac5e706bbf4b1f99acc2ced6cf454a/nsw-ausgrid-2018/NSW_Ausgrid_2018_Bondi.uds")
        pose = [332351.701542, 6245005.938774,417.148115,np.pi/2,0,0 ]
        ar = m.renderTarget.height/m.renderTarget.width
        m.renderTarget.width = 1000 # number of pixels horizontally
        m.renderTarget.height = ar * m.renderTarget.width
        viewWidth = 500 #width of our view in metres
        m.set_projection_ortho(viewWidth)
        #m.camera.farPlane = 150
        #m.camera.set_projection_perspective(FOV=60)
        #edges = m.make_estimate_canny(pose)
        #plt.imshow(edges)
        #plt.figure()
        #canny = m.make_estimate_canny_depth(pose)
        #polys = m.make_morphological_polygons(pose)
        polys = m.layeredMorphPolygons(pose, 5)
        write_polygon_file(polys)
        pass


    testChangeView = False
    if testChangeView:
        pose = [435360.173423, 6305988.331001, 190.225068 ,0,0,0]
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