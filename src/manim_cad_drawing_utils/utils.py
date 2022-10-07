import numpy as np
from manim import *

__all__ = ["angle_between_vectors_signed",
           "Bezier_Handlebars"]

def angle_between_vectors_signed(v1,v2):
    '''
    Get signed angle between vectors according to right hand rule.
    :param v1: first vector
    :param v2: second vector
    :return: angle of rotation that rotates v1 to be co-linear with v2. Range: -PI...+PI
    '''
    cval = np.dot(v1, v2)
    sval = (np.cross(v1, v2))[2]
    return np.arctan2(sval, cval)

class Bezier_Handlebars(VDict):
    '''
    Creates circles (dots) and lines on the points of another mobject.
    Used for visualizing bezier control points and handles, helps debugging.
    '''
    def __init__(self,target_mobject:VMobject, **kwargs):
        super().__init__(**kwargs)
        self.target = target_mobject
        self.generate_circles(0.03)
        self.generate_lines()


    def generate_circles(self,r):
        DotGroup = VGroup(*[
            Circle(radius=r,
                   arc_center=p,
                   color=TEAL,
                   fill_opacity=1,
                   stroke_opacity=0,
                   num_components=4)
            for p in self.target.points])
        self['dots'] = DotGroup

    def move_circles(self):
        for zipthing in zip(self['dots'],self.target.points):
            zipthing[0].move_to(zipthing[1])

    def generate_lines(self):
        pointlist = zip(self.target.points[0::4, :], self.target.points[1::4, :], self.target.points[2::4, :],
                        self.target.points[3::4, :])
        LineGroup = VGroup(*[VGroup(*[
            Line(p[0],p[1],color=TEAL, stroke_width=2),Line(p[2],p[3],color=TEAL, stroke_width=2)]
                                    ) for p in pointlist])
        self['lines'] = LineGroup

    def move_lines(self):
        pointlist = zip(self.target.points[0::4, :], self.target.points[1::4, :], self.target.points[2::4, :],
                        self.target.points[3::4, :])
        for zipthing in zip(self['lines'],pointlist):
            # Line.put_start_and_end_on()
            zipthing[0][0].put_start_and_end_on(zipthing[1][0],zipthing[1][1])
            zipthing[0][1].put_start_and_end_on(zipthing[1][2], zipthing[1][3])