import numpy as np
from manim import *
from .utils import angle_between_vectors_signed
from .round_corners import *

class Path_mapper(VMobject):
    def __init__(self,path_source:VMobject,num_of_path_points=100,**kwargs):
        super().__init__(**kwargs)
        self.num_of_path_points = num_of_path_points
        self.path= path_source
        self.generate_length_map()

    def generate_length_map(self):
        norms = np.array(0)
        for k in range(self.path.get_num_curves()):
            norms = np.append(norms, self.path.get_nth_curve_length_pieces(k,sample_points=11))
        # add up length-pieces in array form
        self.pathdata_lengths  = np.cumsum(norms)
        self.pathdata_alpha = np.linspace(0, 1, self.pathdata_lengths.size)

    def cubic_to_quads(self, cubic_points):
        # based on https://ttnghia.github.io/pdf/QuadraticApproximation.pdf
        q_points = np.empty((0,3))
        gamma = 0.5
        q1 = cubic_points[0,:] + 3/2*gamma * (cubic_points[1,:]-cubic_points[0,:])
        q3 = cubic_points[3,:] + 3/2*(1-gamma) * (cubic_points[2,:]-cubic_points[3,:])
        q2 = (1-gamma)*q1 + gamma * q3
        q0 = cubic_points[0,:]
        q4 = cubic_points[3,:]
        q_points = np.append(q_points,(q0,q1,q2,q2,q3,q4),axis=0)
        return q_points

    def calc_len_bezier_quad(self,points):
        a = points[0, :]
        b = points[1, :]
        c = points[2, :]

        B = b-a
        F = c-b
        A = F-B
        nF = np.linalg.norm(F)
        nA = np.linalg.norm(A)
        nB = np.linalg.norm(B)
        if nA>1e-8:
            L = (nF * np.dot(A, F) - nB * np.dot(A, B)) / (nA ** 2) + (nA ** 2 * nB ** 2 - np.dot(A, B) ** 2) / \
                (nA ** 3) * (np.log(nA * nF + np.dot(A, F)) - np.log(nA * nB + np.dot(A, B)))
            return L
        else:
            return np.linalg.norm(a-c)

    def calc_len_with_quads(self):
        L = 0
        for k in range(self.path.get_num_curves()):
            points = self.path.get_nth_curve_points(k)
            quads = self.cubic_to_quads(points)
            L0 = self.calc_len_bezier_quad(quads[:3, :])
            L1 = self.calc_len_bezier_quad(quads[3:, :])
            L += L0+L1
        return L

    def get_path_length(self):
        return self.pathdata_lengths[-1]

    def alpha_from_length(self,s):
        if hasattr(s, '__iter__'):
            return [np.interp(t, self.pathdata_lengths, self.pathdata_alpha) for t in s]
        else:
            return np.interp(s, self.pathdata_lengths, self.pathdata_alpha)

    def length_from_alpha(self,a):
        if hasattr(a, '__iter__'):
            return [np.interp(t, self.pathdata_alpha, self.pathdata_lengths) for t in a]
        else:
            return np.interp(a, self.pathdata_alpha, self.pathdata_lengths)

    def equalize_alpha(self, a):
        'used for inverting the alpha behavior'
        return self.alpha_from_length(a*self.get_path_length())

    def equalize_rate_func(self, rate_func):
        '''
        Specifically made to be used with Create() animation.
        :param rate_func: rate function to be equalized
        :return: callable new rate function
        Example:
        class test_path_mapper_anim(Scene):
            def construct(self):
                mob1 = round_corners(Triangle(fill_color=TEAL,fill_opacity=0).scale(3),0.5)
                PM = Path_mapper(mob1)
                mob2 = mob1.copy()
                mob1.shift(LEFT * 2.5)
                mob2.shift(RIGHT * 2.5)

                self.play(Create(mob1,rate_func=PM.equalize_rate_func(smooth)),Create(mob2),run_time=5)
                self.wait()
        '''
        def eq_func(t:float):
            return self.equalize_alpha(rate_func(t))
        return eq_func

    def point_from_proportion(self, alpha: float) -> np.ndarray:
        '''
         Override original implementation.
         Should be the same, except it uses pre calculated length table and should be faster a bit.
        '''
        if hasattr(alpha, '__iter__'):
            values = self.alpha_from_length(alpha * self.get_path_length())
            ret = np.empty((0,3))
            for a in values:
                if a == 1:
                    index = self.path.get_num_curves() - 1
                    remainder = 1
                else:
                    index = int(a * self.path.get_num_curves() // 1)
                    remainder = (a * self.path.get_num_curves()) % 1
                p = self.path.get_nth_curve_function(index)(remainder)
                ret = np.concatenate([ret,np.reshape(p,(1,3))],axis=0)
            return ret
        else:
            a = self.alpha_from_length(alpha*self.get_path_length())
            if a==1:
                index = self.path.get_num_curves()-1
                remainder = 1
            else:
                index = int(a * self.path.get_num_curves() // 1)
                remainder = (a * self.path.get_num_curves()) % 1
            return self.path.get_nth_curve_function(index)(remainder)

    def get_length_between_points(self,b,a):
        '''
        Signed arc length between to points.
        :param b: second point
        :param a: first point
        :return: length (b-a)
        '''
        return self.length_from_alpha(b)-self.length_from_alpha(a)

    def get_length_between_points_wrapped(self,b,a):
        ''' This function wraps around the length between two points similar to atan2 method.
        Useful for closed mobjects.
        Returns distance value between -L/2...L/2 '''
        AB = self.get_length_between_points(b,a)
        L = self.get_path_length()
        return (AB%L-L/2)%L-L/2

    def get_length_between_points_tuple(self,b,a):
        ''' Function to get the 2 absolute lengths between 2 parameters on closed mobjects.
        Useful for closed mobjects.
        :returns tuple (shorter, longer)'''

        AB = abs(self.get_length_between_points(b,a))
        L = self.get_path_length()
        if AB>L/2:
            return (L - AB), AB
        else:
            return AB, (L - AB)

    def get_bezier_index_from_length(self,s):
        a = self.alpha_from_length(s)
        nc = self.path.get_num_curves()
        indx = int(a * nc // 1)
        bz_a = a * nc % 1
        if indx==nc:
            indx = nc-1
            bz_a=1
        return (indx,bz_a)

    def get_tangent_unit_vector(self,s):
        # diff_bez_points = 1/3*(self.path.points[1:,:]-self.path.points[:-1,:])
        indx, bz_a = self.get_bezier_index_from_length(s)
        points = self.path.get_nth_curve_points(indx)
        dpoints = (points[1:,:]-points[:-1,:])/3
        bzf = bezier(dpoints)
        point = bzf(bz_a)
        return normalize(point)

    def get_tangent_angle(self,s):
        tv = self.get_tangent_unit_vector(s)
        return angle_of_vector(tv)

    def get_normal_unit_vector(self,s):
        tv = self.get_tangent_unit_vector(s)
        return rotate_vector(tv,PI/2)

    def get_curvature_vector(self,s):
        indx, bz_a = self.get_bezier_index_from_length(s)
        points = self.path.get_nth_curve_points(indx)
        dpoints = (points[1:, :] - points[:-1, :]) * 3
        ddpoints = (dpoints[1:, :] - dpoints[:-1, :]) * 2
        deriv = bezier(dpoints)(bz_a)
        dderiv = bezier(ddpoints)(bz_a)
        curv = np.cross(deriv, dderiv) / (np.linalg.norm(deriv)**3)
        return curv

    def get_curvature(self,s):
        return np.linalg.norm(self.get_curvature_vector(s))

# DashedVMobject

class Dashed_line_mobject(VDict):
    def __init__(self,target_mobject:VMobject,
                 num_dashes=15,
                 dashed_ratio=0.5,
                 dash_offset=0.0,
                 **kwargs):
        super().__init__(**kwargs)
        self.path = Path_mapper(target_mobject,num_of_path_points=10*target_mobject.get_num_curves())
        # self.path.add_updater(lambda mob: mob.generate_length_map())

        dshgrp = self.generate_dash_mobjects(
            **self.generate_dash_pattern_dash_distributed(num_dashes,dash_ratio = dashed_ratio,offset=dash_offset)
        )
        self.add({'dashes':dshgrp})
        self['dashes'].match_style(target_mobject)

    def generate_dash_pattern_metric(self,dash_len,space_len, num_dashes, offset=0):
        ''' generate dash pattern in metric curve-length space'''
        period = dash_len + space_len
        n = num_dashes
        full_len = self.path.get_path_length()
        dash_starts = [(i * period + offset) for i in range(n)]
        dash_ends = [(i * period + dash_len + offset) for i in range(n)]
        k=0
        while k<len(dash_ends):
            if dash_ends[k]<0:
                dash_ends.pop(k)
                dash_starts.pop(k)
            k+=1

        k = 0
        while k < len(dash_ends):
            if dash_starts[k] > full_len:
                dash_ends.pop(k)
                dash_starts.pop(k)
            k+=1
        return {'dash_starts':dash_starts,'dash_ends':dash_ends}

    def generate_dash_pattern_dash_distributed(self,num_dashes,dash_ratio = 0.5,offset=0.0):
        full_len = self.path.get_path_length()
        period = full_len / num_dashes
        dash_len = period * dash_ratio
        space_len = period * (1-dash_ratio)
        n = num_dashes+2

        return self.generate_dash_pattern_metric(dash_len, space_len, n, offset=(offset-1)*period)

    def generate_dash_mobjects(self,dash_starts=[0],dash_ends=[1]):
        ref_mob = self.path.path
        a_list = self.path.alpha_from_length(dash_starts)
        b_list = self.path.alpha_from_length(dash_ends)
        ret=[]
        for i in range(len(dash_starts)):
            mobcopy = VMobject().match_points(ref_mob)
            ret.append(mobcopy.pointwise_become_partial(mobcopy,a_list[i],b_list[i]))
        return VGroup(*ret)


class DashDot_mobject(Dashed_line_mobject):
    def __init__(self,
                 target_mobject: VMobject,
                 num_dashes=15,
                 dashed_ratio=0.35,
                 dash_offset=0.0,
                 dot_scale=1,
                 **kwargs):
        super().__init__(target_mobject,
                         num_dashes,
                         dashed_ratio,
                         dash_offset,
                         **kwargs)
        dot = Circle(radius=target_mobject.get_stroke_width()/100*dot_scale,
                     fill_opacity=1,
                     stroke_opacity=0,
                     num_components=6,
                     fill_color=target_mobject.get_stroke_color())
        dash_marks = self.generate_dash_pattern_dash_distributed(num_dashes,dashed_ratio,dash_offset)

        full_len = self.path.get_path_length()
        if dash_marks['dash_starts'][0]<dash_marks['dash_ends'][0]:
            dot_marks = np.array((np.array(dash_marks['dash_starts'])[1:] + np.array(dash_marks['dash_ends'])[:-1])) / 2
        else:
            dot_marks = np.array((np.array(dash_marks['dash_starts']) + np.array(dash_marks['dash_ends']))) / 2


        dot_marks = dot_marks%full_len
        dots=VGroup(*[dot.copy().move_to(self.path.point_from_proportion(m / full_len)) for m in dot_marks])
        self['dots']=dots





class Path_Offset_Mobject(VMobject):
    def __init__(self,
                 target_mobject,
                 ofs_func,
                 ofs_func_kwargs={},
                 num_of_samples=100,
                 discontinuities=[],
                 **kwargs):
        super().__init__(**kwargs)
        self.ofs_func_kwargs = ofs_func_kwargs
        self.PM = Path_mapper(target_mobject)
        self.PM.add_updater(lambda mob: mob.generate_length_map())
        self.discontinuities = discontinuities

        self.t_range = np.linspace(0, 1, num_of_samples)
        if discontinuities:
            t_disc = np.sort(
                np.concatenate((np.array(self.discontinuities) + 1e-7, np.array(self.discontinuities) - 1e-7)))
            self.t_range=np.sort(np.concatenate((self.t_range,t_disc)))
        self.ofs_func = ofs_func
        self.s_scaling_factor = 1/self.PM.get_path_length()
        self.points = self.generate_offset_paths()

    # this can be useful in lambdas for updaters
    def set_ofs_function_kwargs(self,ofs_func_kwargs):
        self.ofs_func_kwargs = ofs_func_kwargs

    def generate_bezier_points(self, input_func,t_range, Smoothing=True):
        # generate bezier 4-lets with numerical difference
        out_data = []
        for k in range(len(t_range)-1):
            t = t_range[k]
            t2 = t_range[k+1]
            val1 = input_func(t)
            val2 = input_func(t2)
            p1 = val1
            p4 = val2
            if Smoothing:
                diff1 = (input_func(t + 1e-6) - input_func(t)) / 1e-6
                diff2 = (input_func(t2) - input_func(t2 - 1e-6)) / 1e-6
                p2 = val1 + diff1 * (t2 - t) / 3
                p3 = val2 - diff2 * (t2 - t) / 3
            else:
                p2 = (val1 * 2 + val2) / 3
                p3 = (val1 + val2 * 2) / 3
            out_data.append([p1,p2,p3,p4])
        return out_data


    def generate_ref_curve(self):
        self.ref_curve = VMobject()
        bez_point = self.generate_bezier_points(self.PM.point_from_proportion,self.t_range)
        for point in bez_point:
            self.ref_curve.append_points(point)
        self.ref_curve_path = Path_mapper(self.ref_curve)

    def generate_offset_func_points(self,Smoothing=True):
        points = self.generate_bezier_points(lambda t: self.ofs_func(t,**self.ofs_func_kwargs),self.t_range,Smoothing=Smoothing)
        return points

    def generate_normal_vectors(self):
        s_range = self.t_range*self.PM.get_path_length()
        # generate normal vectors from tangent angles and turning them 90°
        # the angles can be interpolated with bezier, unit normal vectors would not remain 'unit' under interpolation
        angles = self.generate_bezier_points(self.PM.get_tangent_angle,s_range)
        out = []
        for angle in angles:
            out.append([np.array([-np.sin(a),np.cos(a),0])for a in angle])
        return out

    def generate_offset_paths(self,gen_ofs_point=True, gen_ref_curve=True):
        if gen_ref_curve:
            self.generate_ref_curve()
            self.norm_vectors = self.generate_normal_vectors()
        if gen_ofs_point:
            self.ofs_points = self.generate_offset_func_points()

        n = self.ref_curve.get_num_curves()
        ofs_vectors = np.empty((n*4,3))
        for k in range(len(self.ofs_points)):
            for j in range(len(self.ofs_points[k])):
                ofs_vectors[k*4+j,:] = self.norm_vectors[k][j] * self.ofs_points[k][j]

        return self.ref_curve.points + ofs_vectors

    def default_updater(self,gen_ofs_point=True, gen_ref_curve=True):
        self.points = self.generate_offset_paths(gen_ofs_point,gen_ref_curve)


class Curve_Warp(VMobject):
    def __init__(self,warp_source:VMobject,warp_curve:VMobject,anchor_point=0.5, **kwargs):

        self.warp_curve = warp_curve
        self.warp_source = warp_source
        self.PM = Path_mapper(self.warp_curve)
        self.anchor_point = anchor_point
        super().__init__(**kwargs)
        self.match_style(warp_source)

    def generate_points(self):

        s0 = self.PM.length_from_alpha(self.anchor_point)
        x_points = self.warp_source.points[:, 0] + s0
        y_points = self.warp_source.points[:, 1]
        L = self.PM.get_path_length()

        if self.warp_curve.is_closed():
            #if the curve is closed, out-of-bound x values can wrap around to the beginning
            x_points = x_points % L
            x_curve_points = self.PM.point_from_proportion(x_points/L)
            nv = [self.PM.get_normal_unit_vector(x) for x in x_points]
            y_curve_points = np.array( [tuplie[0] * tuplie[1] for tuplie in zip(nv,y_points)])
            self.points = x_curve_points + y_curve_points
        else:
            self.points = np.empty((0,3))
            for x,y in zip(x_points,y_points):
                if 0 < x <= L:
                    p = self.PM.point_from_proportion(x / L) + self.PM.get_normal_unit_vector(x)*y
                    self.points = np.append(self.points,np.reshape(p,(1,3)),axis=0)
                elif x>L:
                    endpoint = self.PM.point_from_proportion(1)
                    tanv = self.PM.get_tangent_unit_vector(L)
                    nv = rotate_vector(tanv,PI/2)
                    x_1 = x-L
                    p = endpoint + x_1 * tanv + y * nv
                    self.points = np.append(self.points, np.reshape(p,(1,3)), axis=0)
                else:
                    startpoint = self.PM.point_from_proportion(0)
                    tanv = self.PM.get_tangent_unit_vector(0)
                    nv = rotate_vector(tanv, PI / 2)
                    x_1 = x
                    p = startpoint + x_1 * tanv + y * nv
                    self.points = np.append(self.points, np.reshape(p, (1, 3)), axis=0)