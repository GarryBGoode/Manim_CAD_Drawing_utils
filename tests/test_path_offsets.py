import numpy as np
from manim import *
from manim_cad_drawing_utils import *



class test_offset(Scene):
    def construct(self):
        vt = ValueTracker(0)
        multipliers = [1,2,3]
        ref_mob = Arc(radius=1,start_angle=PI/4,angle=PI/2,color=BLUE,num_components=3).shift(DOWN*2)
        # ref_mob.points[-1,:] = ref_mob.points[-1:,:] + 0.2 * UP
        # ref_mob.points[0, :] = ref_mob.points[0, :] + 0.2 * UP
        Ofs_grp = VGroup()
        ofs_func_list = []

        def ofs_func1(s):
            return - 1 * vt.get_value()

        def ofs_func2(s):
            return - 2 * vt.get_value()

        def ofs_func3(s):
            return - 3 * vt.get_value()

        func_arry = [ofs_func1,ofs_func2,ofs_func3]

        for k in range(3):
            offset_mob = Path_Offset_Mobject(ref_mob,num_of_samples=20, ofs_func=func_arry[k],color=BLUE)
            Ofs_grp.add(offset_mob)
        for k in range(len(Ofs_grp)):
            Ofs_grp[k].add_updater(Ofs_grp[k].default_updater)
        Ofs_grp.update()
        self.play(Create(ref_mob))
        self.add(Ofs_grp)
        self.play(vt.animate.set_value(0.4),run_time=1)

class test_bulge(Scene):
    def construct(self):
        mob1 = round_corners(Square().scale(3),radius=1).shift(DOWN*0)
        vt = ValueTracker(0)

        def ofs_func(t):
            x = 30 * (t-vt.get_value())
            x2 = 30 * (t - vt.get_value()-1)
            x3 = 30 * (t - vt.get_value()+1)
            return 0.02 + 0.4 * (np.exp(-(x)**2) + np.exp(-(x3)**2) + np.exp(-(x2)**2))
        ofspath = Path_Offset_Mobject(mob1,ofs_func,fill_color=RED,fill_opacity=0,stroke_opacity=0)
        ofspath2 = Path_Offset_Mobject(mob1.copy().reverse_direction(), ofs_func, fill_color=RED, fill_opacity=0, stroke_opacity=0)
        bulge = VMobject(stroke_opacity=1,fill_opacity=1)

        def ofs_updater(mob):
            curve1 = mob.generate_offset_paths(gen_ref_curve=False, gen_ofs_point=True)
            mob['ofs_mobj'].points = curve1

        ofspath.add_updater(ofs_updater)
        ofspath2.add_updater(ofs_updater)

        def bulge_updater(mob:VMobject):
            point_list = np.concatenate((ofspath['ofs_mobj'].points,ofspath2['ofs_mobj'].points),axis=0)
            mob.points=point_list
        bulge.add_updater(bulge_updater)

        c = Circle(radius=0.05)

        debugdots = VGroup(*[Circle(arc_center=ofspath['ofs_mobj'].points[p,:],radius=0.01,
                                    stroke_opacity=0,fill_opacity=1,fill_color=TEAL) for p in range((ofspath['ofs_mobj'].points.shape)[0])])
        debugdots.set_color(TEAL)
        def asdasd(mob):
            for p in range((ofspath2['ofs_mobj'].points.shape)[0]):
                mob.submobjects[p].move_to(ofspath2['ofs_mobj'].points[p, :])

        debugdots.add_updater(asdasd)

        self.add(ofspath,ofspath2,debugdots,bulge)
        # mob1.set_stroke(opacity=0)
        self.play(vt.animate.set_value(0.5),run_time=6)
        self.wait(0.5)
        self.play(vt.animate.set_value(0.65), run_time=6)
        self.wait(0.5)
        self.play(vt.animate.set_value(1.2), run_time=6,rate_func=rate_functions.ease_in_out_back)
        self.wait(0.5)
        self.play(vt.animate.set_value(0), run_time=6)
        self.wait(0.5)


with tempconfig({"quality": "medium_quality", "disable_caching": True}):
    scene = test_offset()
    scene.render()