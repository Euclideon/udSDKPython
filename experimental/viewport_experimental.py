"""
module containing experimental features relating to extending viewports
"""
from pygletExample import *

class UDViewPort3D(UDViewPort):
    """
    Viewport quad with 3D faces, used for constructing ViewPrisms
    """
    def __init__(self, width, height, centreX, centreY, parent, horizontalDirection = [1,0,0], verticalDirection = [0,1,0]):
        self._width = width
        self._height = height
        self._centre = [centreX, centreY, 0]
        self.parent = parent
        self.vec1 = horizontalDirection
        self.vec2 = verticalDirection
        #self.vec1 = [0.707, -0.707,0.01]
        #self.vec2 = [0.707, 0.707,0.01]
        super(UDViewPort3D, self).__init__(width, height, centreX, centreY, parent)

    def orient(self, centre, vec1, vec2):
        #position the plane such that it is parallel to vectors 1 and 2 and centred at centre:
        # these are the vertices at the corners of the quad, each line is the pixel coordinates of the
        self._vertex_list.vertices = \
            [
                # bottom left
                centre[0] - vec1[0] * self._width / 2 - vec2[0] * self._height / 2,
                centre[1] - vec1[1] * self._width / 2 - vec2[1] * self._height / 2,
                centre[2] - vec1[2] * self._width / 2 - vec2[2] * self._height / 2,
                # bottom right
                centre[0] + vec1[0] * self._width / 2 - vec2[0] * self._height / 2,
                centre[1] + vec1[1] * self._width / 2 - vec2[1] * self._height / 2,
                centre[2] + vec1[2] * self._width / 2 - vec2[2] * self._height / 2,
                #top right
                centre[0] + vec1[0] * self._width/2 + vec2[0] * self._height/2,
                centre[1] + vec1[1] * self._width / 2 + vec2[1] * self._height / 2,
                centre[2] + vec1[2] * self._width / 2 + vec2[2] * self._height / 2,
                # top left
                centre[0] - vec1[0] * self._width / 2 + vec2[0] * self._height / 2,
                centre[1] - vec1[1] * self._width / 2 + vec2[1] * self._height / 2,
                centre[2] - vec1[2] * self._width / 2 + vec2[2] * self._height / 2,
                ]
        #position the camera such that it is a fixed distance from the
        import numpy as np
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        normal = np.cross(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2))
        normal = normal.dot(np.array([
            [1, 0, 0],
            [0, 0, 1],
            [0, 1, 0],
        ]))
        self.camera.look_at([0, 0, 0], normal)
        #self._camera.set_view(normal[0], normal[1], normal[2])

    def make_vertex_list(self):
        self._vertex_list = pyglet.graphics.vertex_list(4,'v3f/stream','t2f/static')
        self._vertex_list.tex_coords = \
            [
                0, 1,
                1, 1,
                1, 0,
                0, 0,
            ]
        self.orient(self._centre, self.vec1, self.vec2)


class UDViewPrism:
    """
    Class representing a sectional view of a model
    it is a rectangular prism with a UD view for each face
    """
    def __init__(self, width, height, depth):
        self.height = height
        self.width = width
        self.depth = depth

        self.viewPorts = []
