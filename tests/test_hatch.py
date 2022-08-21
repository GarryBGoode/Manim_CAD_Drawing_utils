from manim import *
from manim_cad_drawing_utils import *


class test_hatch(Scene):
    def construct(self):
        mob1 = Star().scale(2)
        hatch1 = Hatch_lines(mob1,angle=PI/6,stroke_width=2)
        hatch2 = Hatch_lines(mob1,angle=PI/6+PI/2,stroke_width=2)
        self.add(mob1,hatch1,hatch2)

# with tempconfig({"quality": "medium_quality", "disable_caching": True}):
#     scene = test()
#     scene.render()