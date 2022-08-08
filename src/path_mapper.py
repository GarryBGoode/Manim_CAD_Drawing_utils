import numpy as np
from manim import *
from utils import angle_between_vectors_signed
from round_corners import *

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

    def get_path_length(self):
        return self.pathdata_lengths[-1]

    def alpha_from_length(self,s):
        if hasattr(s, '__iter__'):
            return [np.interp(t, self.pathdata_lengths, self.pathdata_alpha) for t in s]
        else:
            return np.interp(s, self.pathdata_lengths, self.pathdata_alpha)

    def length_from_alpha(self,s):
        if hasattr(s, '__iter__'):
            return [np.interp(t, self.pathdata_alpha, self.pathdata_lengths) for t in s]
        else:
            return np.interp(s, self.pathdata_alpha, self.pathdata_lengths)

    def get_bezier_index_from_length(self,s):
        a = self.alpha_from_length(s) % 1
        nc = self.path.get_num_curves()
        indx = int(a * nc // 1)
        bz_a = a * nc % 1
        return (indx,bz_a)

    def get_tangent_unit_vector(self,s):
        # diff_bez_points = 1/3*(self.path.points[1:,:]-self.path.points[:-1,:])
        indx, bz_a = self.get_bezier_index_from_length(s)
        points = self.path.get_nth_curve_points(indx)
        dpoints = (points[1:,:]-points[:-1,:])/3
        bzf = bezier(dpoints)
        point = bzf(bz_a)
        return normalize(point)

    def get_normal_unit_vector(self,s):
        tv = self.get_tangent_unit_vector(s)
        return rotate_vector(tv,PI/2)

    def get_curvature_vector(self,s):
        indx, bz_a = self.get_bezier_index_from_length(s)
        points = self.path.get_nth_curve_points(indx)
        dpoints = (points[1:, :] - points[:-1, :]) / 3
        ddpoints = (dpoints[1:, :] - dpoints[:-1, :]) / 2
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
                 dash_offset=0.0,**kwargs):
        super().__init__(**kwargs)
        self['path'] = Path_mapper(target_mobject,num_of_path_points=10*target_mobject.get_num_curves())
        self['path'].add_updater(lambda mob: mob.generate_length_map())

        dshgrp = self.generate_dash_mobjects(
            **self.generate_dash_pattern_dash_distributed(num_dashes,dash_ratio = dashed_ratio,offset=dash_offset)
        )
        self.add({'dashes':dshgrp})

    def generate_dash_pattern_metric(self,dash_len,space_len, num_dashes, offset=0):
        ''' generate dash pattern in metric length space'''
        period = dash_len + space_len
        n = num_dashes
        full_len = self['path'].get_path_length()
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
        full_len = self['path'].get_path_length()
        period = full_len / num_dashes
        dash_len = period * dash_ratio
        space_len = period * (1-dash_ratio)
        n = num_dashes+2

        return self.generate_dash_pattern_metric(dash_len, space_len, n, offset=(offset-1)*period)

    def generate_dash_mobjects(self,dash_starts=[0],dash_ends=[1]):
        # ref_mob = VMobject()
        # ref_mob.match_points(self['path'].path)
        ref_mob = self['path'].path
        # VMobject.pointwise_become_partial()
        a_list = self['path'].alpha_from_length(dash_starts)
        b_list = self['path'].alpha_from_length(dash_ends)
        ret=[]
        for i in range(len(dash_starts)):
            mobcopy = VMobject().match_points(ref_mob)
            ret.append(mobcopy.pointwise_become_partial(mobcopy,a_list[i],b_list[i]))
        return VGroup(*ret)


class Path_Offset_Mobject(VDict):
    def __init__(self,target_mobject, ofs_func, **kwargs):
        super().__init__(**kwargs)
        self['path'] = Path_mapper(target_mobject)
        self['path'].add_updater(lambda mob: mob.generate_length_map())
        self.ofs_func = ofs_func
        self.s_scaling_factor =  1/self['path'].get_path_length()
        self.generate_ref_curve()
        # self.s_scaling_factor =  self.ref_curve_path.get_path_length()
        curve1,curve2 = self.generate_offset_paths()
        closed_path = VMobject(**kwargs)
        closed_path.points = curve1.points
        curve2.reverse_direction()
        closed_path.points = np.append(closed_path.points, curve2.points,axis=0)
        self['ofs_mobj'] = closed_path
        # self.s_scaling_factor=1

    def generate_ref_curve(self):
        self.ref_curve = VMobject()
        n=self['path'].path.get_num_curves()
        a_ref = (np.linspace(0, 1, n * 10))
        self.ref_curve.points = np.empty((0, 3))
        for k in range(len(a_ref)-1):
            p0 = np.reshape(self['path'].path.point_from_proportion(a_ref[k]), (1, 3))
            p1 = np.reshape(self['path'].path.point_from_proportion((a_ref[k]*2+a_ref[k + 1]*1)/3), (1, 3))
            p2 = np.reshape(self['path'].path.point_from_proportion((a_ref[k]*1+a_ref[k + 1]*2)/3), (1, 3))
            p3 = np.reshape(self['path'].path.point_from_proportion(a_ref[k + 1]), (1, 3))
            self.ref_curve.points = np.concatenate((self.ref_curve.points,p0,p1,p2,p3),axis=0)
        self.ref_curve.make_smooth()
        n2 = self.ref_curve.get_num_curves()
        # alpha_ref = np.linspace(0,1,n2+1)
        self.alpha_ref = np.linspace(0,1,n2+1)
        # for k in range(len(alpha_ref)-1):
        #     self.alpha_ref.extend([alpha_ref[k],alpha_ref[k],alpha_ref[k+1],alpha_ref[k+1]])
        self.ref_curve_path = Path_mapper(self.ref_curve)

    def generate_offset_bezier_points(self):
        points = np.empty(0)
        for k in range(len(self.alpha_ref)-1):
            a = self.alpha_ref[k]
            a2 = self.alpha_ref[k+1]
            s = self.ref_curve_path.length_from_alpha(a) * self.s_scaling_factor
            s2 = self.ref_curve_path.length_from_alpha(a2) * self.s_scaling_factor
            ds = 1e-3
            diff = (self.ofs_func(s + ds) - self.ofs_func(s - ds)) / 2 / ds
            diff2 = (self.ofs_func(s2 + ds) - self.ofs_func(s2 - ds)) / 2 / ds
            p0 = self.ofs_func(s)
            p1 = p0 + diff*(s2-s)*1/3
            p3 = self.ofs_func(s2)
            p2 = p3 - diff2*(s2-s)*1/3

            points=np.append(points,[p0,p1,p2,p3])

        return points

    def generate_offset_paths(self):
        curve1 = VMobject()
        curve1.points = np.empty((0, 3))
        curve2 = VMobject()
        curve2.points = np.empty((0, 3))
        ofs_points = self.generate_offset_bezier_points()
        ofs_vectors =np.empty((0,3))

        for k in range(len(self.alpha_ref)-1):
            a = self.alpha_ref[k]
            s = self.ref_curve_path.length_from_alpha(a)
            nv = np.reshape(self.ref_curve_path.get_normal_unit_vector(s), (1, 3))
            a2 = self.alpha_ref[k+1]
            s2 = self.ref_curve_path.length_from_alpha(a2)
            nv2 = np.reshape(self.ref_curve_path.get_normal_unit_vector(s2), (1, 3))
            # ofs_v_1 = np.reshape(ofs_points[k]*nv, (1, 3))
            # ofs_v_2 = np.reshape(ofs_points[k+1] * nv, (1, 3))
            # ofs_v_3 = np.reshape(ofs_points[k+2] * nv2, (1, 3))
            # ofs_v_4 = np.reshape(ofs_points[k+3] * nv2, (1, 3))
            ofs_vectors = np.concatenate([ofs_vectors,nv,nv,nv2,nv2],axis=0)

        for k in range(len(ofs_points)):
            ofs_vectors[k,:] = ofs_vectors[k,:] * ofs_points[k]
        # ofs_vectors = np.prod([ofs_vectors,ofs_points],axis=1)
        curve1.points = self.ref_curve.points + ofs_vectors
        curve2.points = self.ref_curve.points - ofs_vectors
        # curve1.make_smooth()
        # curve2.make_smooth()
        return (curve1,curve2)




class test(Scene):
    def construct(self):
        # mob1 = Triangle().scale(2)
        # mob1 = FunctionGraph(lambda t: t**5,[-1,1,0.1],color=WHITE)
        # mob1 = Line(start=LEFT,end=LEFT*0.5)
        # mob1.add_line_to(RIGHT).scale(4)
        # mob1 = Circle(radius=3)
        mob1 = round_corners(Square().scale(3),radius=0.8).shift(DOWN*0)
        vt = ValueTracker(0)
        dash1 = Dashed_line_mobject(mob1,num_dashes=36,dashed_ratio=0.5,dash_offset=0)
        def dash_updater(mob):
            offset = 1/mob['path'].get_path_length()*36*vt.get_value()%1
            dshgrp = mob.generate_dash_mobjects(
                **mob.generate_dash_pattern_dash_distributed(36, dash_ratio=0.5, offset=offset)
            )
            # mob.remove('dashes')
            # mob.add({'dashes':dshgrp})
            mob['dashes'].become(dshgrp)

        # dash1.add_updater(dash_updater)
        def ofs_func(t):
            x = 30 * (t-vt.get_value())
            x2 = 30 * (t - vt.get_value()-1)
            x3 = 30 * (t - vt.get_value()+1)
            return 0.02 + 0.3* (np.exp(-(x)**2) + np.exp(-(x3)**2) + np.exp(-(x2)**2))
        ofspath = Path_Offset_Mobject(mob1,ofs_func,fill_color=RED,fill_opacity=1,stroke_opacity=0)

        def ofs_updater(mob):
            curve1, curve2 = mob.generate_offset_paths()
            mob['ofs_mobj'].points = curve1.points
            curve2.reverse_direction()
            mob['ofs_mobj'].points = np.append(mob['ofs_mobj'].points, curve2.points, axis=0)
            # mob['ofs_mobj'].make_smooth()

        ofspath.add_updater(ofs_updater)
        # ofspath.update()
        c = Circle(radius=0.05)
        c2 = c.copy()
        # pather1 = Path_mapper(mob1)
        # def asdater(mob):
        #     a = vt.get_value()
        #     p = pather1.path.point_from_proportion(a)
        #     v = pather1.get_tangent_unit_vector(a*pather1.get_path_length())*2
        #     mob.move_to(p+v)
        # c.add_updater(asdater)
        # c2.add_updater(lambda mob: mob.move_to(mob1.point_from_proportion(vt.get_value())))
        # dash1.add_updater(lambda mob: dash1['dashes']=)
        debugdots = VGroup(*[Circle(arc_center=ofspath['ofs_mobj'].points[p,:],radius=0.01,
                                    stroke_opacity=0,fill_opacity=1,fill_color=TEAL) for p in range((ofspath['ofs_mobj'].points.shape)[0])])
        debugdots.set_color(TEAL)
        def asdasd(mob):
            for p in range((ofspath['ofs_mobj'].points.shape)[0]):
                mob.submobjects[p].move_to(ofspath['ofs_mobj'].points[p, :])

        debugdots.add_updater(asdasd)

        self.add(ofspath)
        # mob1.set_stroke(opacity=0)
        self.play(vt.animate.set_value(1),run_time=6)
        self.play(vt.animate.set_value(0), run_time=6)

#
# with tempconfig({"quality": "medium_quality", "disable_caching": True}):
#     scene = test()
#     scene.render()