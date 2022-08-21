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
        mob1 = round_corners(Square().scale(3),radius=0.8).shift(DOWN*0)
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
        # mob1.set_stroke(opacity=0)
        self.play(vt.animate.set_value(2),run_time=6)
        self.wait(0.5)