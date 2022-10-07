from manim import *
from manim_cad_drawing_utils import *

class test(Scene):
    def construct(self):
        mob1 = Round_Corners(Square().scale(3),radius=0.8).shift(DOWN*0)
        vt = ValueTracker(0)
        dash1 = Dashed_line_mobject(mob1,num_dashes=36,dashed_ratio=0.5,dash_offset=0)
        def dash_updater(mob):
            offset = vt.get_value()%1
            dshgrp = mob.generate_dash_mobjects(
                **mob.generate_dash_pattern_dash_distributed(36, dash_ratio=0.5, offset=offset)
            )
            mob['dashes'].become(dshgrp)
        dash1.add_updater(dash_updater)

        self.add(dash1)
        self.play(vt.animate.set_value(2),run_time=6)
        self.wait(0.5)

class test_ddot(Scene):
    def construct(self):
        # mob1 = ParametricFunction(lambda t: [t,np.sin(t),0], t_range=[-PI,PI],stroke_opacity=0.3)
        # mob1 = Circle(stroke_opacity=1)
        mob1 = Line(LEFT*6,RIGHT*6)
        dash2 = DashDot_mobject(mob1)
        self.add(dash2)

# with tempconfig({"quality": "medium_quality", "disable_caching": True}):
#     scene = test_ddot()
#     scene.render()