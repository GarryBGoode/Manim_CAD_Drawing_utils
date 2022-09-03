import numpy as np
from manim import *
from manim_cad_drawing_utils import *




class test_offset(Scene):
    def construct(self):
        vt = ValueTracker(0)
        ref_mob = Arc(radius=1,start_angle=0,angle=PI,color=BLUE,num_components=6).shift(DOWN)
        ref_mob.points[-1,:] = ref_mob.points[-1:,:] + 0.5 * LEFT
        ref_mob.points[0, :] = ref_mob.points[0, :] + 0.5 * RIGHT
        Ofs_grp = VGroup()

        def ofs_function(s,gain=1):
            return - gain * vt.get_value()

        for k in range(3):
            offset_mob = Path_Offset_Mobject(ref_mob,num_of_samples=20, ofs_func=ofs_function, ofs_func_kwargs={'gain':k},color=BLUE)
            Ofs_grp.add(offset_mob)
        for k in range(len(Ofs_grp)):
            Ofs_grp[k].add_updater(Ofs_grp[k].default_updater)
        Ofs_grp.update()
        self.play(Create(ref_mob))
        self.add(Ofs_grp)
        self.wait()
        self.play(vt.animate.set_value(1),run_time=1)
        self.wait()
        self.play(vt.animate.set_value(0.5), run_time=1)
        self.wait()
        self.play(vt.animate.set_value(-0.2), run_time=1)
        self.wait()
        self.play(vt.animate.set_value(0), run_time=1)
        self.wait()
        self.remove(Ofs_grp)
        self.play(Uncreate(ref_mob))
        self.wait()



class test_bulge(Scene):
    def construct(self):
        mob1 = Round_Corners(Square().scale(3),radius=1).shift(DOWN*0)
        vt = ValueTracker(0)
        gt = ValueTracker(1)

        def ofs_func(t,gain=1):
            x = 30 * (t-vt.get_value())
            x2 = 30 * (t - vt.get_value()-1)
            x3 = 30 * (t - vt.get_value()+1)
            return 0.02 + gain*0.4 * (np.exp(-(x)**2) + np.exp(-(x3)**2) + np.exp(-(x2)**2))
        ofspath = Path_Offset_Mobject(mob1,ofs_func, ofs_func_kwargs={'gain':gt.get_value()},fill_color=RED,fill_opacity=0,stroke_opacity=0)
        ofspath2 = Path_Offset_Mobject(mob1, ofs_func, ofs_func_kwargs={'gain':-gt.get_value()},fill_color=RED, fill_opacity=0, stroke_opacity=0)
        bulge = VMobject(stroke_opacity=1,fill_opacity=1)

        def ofs_updater(mob):
            curve1 = mob.generate_offset_paths(gen_ref_curve=False, gen_ofs_point=True)
            mob.points = curve1

        ofspath.add_updater(ofs_updater)
        ofspath2.add_updater(ofs_updater)
        ofspath.add_updater(lambda mob: mob.set_ofs_func_kwargs({'gain': gt.get_value()}))
        ofspath2.add_updater(lambda mob: mob.set_ofs_func_kwargs({'gain': -gt.get_value()}))

        def bulge_updater(mob:VMobject):
            point_list = np.concatenate((ofspath.points,ofspath2.reverse_points().points),axis=0)
            mob.points=point_list
        bulge.add_updater(bulge_updater)


        debugdots = VGroup(*[Circle(arc_center=ofspath.points[p,:],radius=0.01,
                                    stroke_opacity=0,fill_opacity=1,fill_color=TEAL) for p in range((ofspath.points.shape)[0])])
        debugdots.set_color(TEAL)
        def asdasd(mob):
            for p in range((ofspath2.points.shape)[0]):
                mob.submobjects[p].move_to(ofspath2.points[p, :])

        debugdots.add_updater(asdasd)

        self.add(ofspath,ofspath2,bulge)
        # mob1.set_stroke(opacity=0)
        self.play(vt.animate.set_value(0.5),run_time=6)
        self.wait(0.5)
        self.play(vt.animate.set_value(0.65), run_time=6)
        self.play(gt.animate.set_value(0), rate_func=rate_functions.there_and_back)
        self.wait(0.5)
        self.play(vt.animate.set_value(1.2), run_time=6,rate_func=rate_functions.ease_in_out_back)
        self.wait(0.5)
        self.play(gt.animate.set_value(0),rate_func=rate_functions.there_and_back)
        # self.play(gt.animate.set_value(1))
        self.play(vt.animate.set_value(0), run_time=6)
        self.wait(0.5)

class Test_warp(Scene):
    def construct(self):
        mob = Triangle(fill_opacity=1,fill_color=TEAL).scale(0.2).rotate(-PI/2).move_to(ORIGIN)
        ref = Arc(radius=2,angle=PI)
        arrowhead = Curve_Warp(mob,ref,anchor_point=0.5)
        arrowhead.add_updater(lambda mob: mob.generate_points())


        self.add(NumberPlane(),ref,mob,arrowhead)
        self.play(mob.animate.stretch(5,0))
        self.wait()
        self.play(mob.animate.stretch(2, 1))
        self.wait()
        self.play(Rotate(mob, PI / 2), run_time=2)
        self.wait()
        self.play(Rotate(mob, PI / 2), run_time=2)
        self.wait()
        self.play(Rotate(mob, PI / 2), run_time=2)
        self.wait()
        self.play(Rotate(mob, PI / 2), run_time=2)
        self.wait()
        self.play(mob.animate.stretch(1/2, 1))
        self.play(mob.animate.stretch(1/5,0))


# with tempconfig({"quality": "medium_quality", "disable_caching": True}):
#     scene = Test_warp()
#     scene.render()