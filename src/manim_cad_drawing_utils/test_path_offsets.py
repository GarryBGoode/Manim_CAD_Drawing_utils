import numpy as np
from manim import *
from path_mapper import *
from round_corners import *

class test(Scene):
    def construct(self):
        # mob1 = Triangle().scale(2)
        # mob1 = FunctionGraph(lambda t: t**5,[-1,1,0.1],color=WHITE)
        # mob1 = Line(start=LEFT,end=LEFT*0.5)
        # mob1.add_line_to(RIGHT).scale(4)
        # mob1 = Circle(radius=3)
        mob1 = round_corners(Square().scale(3),radius=1).shift(DOWN*0)
        vt = ValueTracker(0)

        def ofs_func(t):
            x = 30 * (t-vt.get_value())
            x2 = 30 * (t - vt.get_value()-1)
            x3 = 30 * (t - vt.get_value()+1)
            return 0.02 + 0.4 * (np.exp(-(x)**2) + np.exp(-(x3)**2) + np.exp(-(x2)**2))
        ofspath = Path_Offset_Mobject(mob1,ofs_func,fill_color=RED,fill_opacity=1,stroke_opacity=0)

        def ofs_updater(mob):
            curve1, curve2 = mob.generate_offset_paths(gen_ref_curve=False, gen_norm_v=False,gen_ofs_point=True)
            mob['ofs_mobj'].points = curve1.points
            curve2.reverse_direction()
            mob['ofs_mobj'].points = np.append(mob['ofs_mobj'].points, curve2.points, axis=0)

        ofspath.add_updater(ofs_updater)

        c = Circle(radius=0.05)

        debugdots = VGroup(*[Circle(arc_center=ofspath['ofs_mobj'].points[p,:],radius=0.01,
                                    stroke_opacity=0,fill_opacity=1,fill_color=TEAL) for p in range((ofspath['ofs_mobj'].points.shape)[0])])
        debugdots.set_color(TEAL)
        def asdasd(mob):
            for p in range((ofspath['ofs_mobj'].points.shape)[0]):
                mob.submobjects[p].move_to(ofspath['ofs_mobj'].points[p, :])

        debugdots.add_updater(asdasd)

        self.add(ofspath)
        # mob1.set_stroke(opacity=0)
        self.play(vt.animate.set_value(0.5),run_time=6)
        self.wait(0.5)
        self.play(vt.animate.set_value(0.65), run_time=6)
        self.wait(0.5)
        self.play(vt.animate.set_value(1.2), run_time=6,rate_func=rate_functions.ease_in_out_back)
        self.wait(0.5)
        self.play(vt.animate.set_value(0), run_time=6)
        self.wait(0.5)


# with tempconfig({"quality": "medium_quality", "disable_caching": True}):
#     scene = test()
#     scene.render()