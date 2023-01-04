from manim import *
from manim_cad_drawing_utils import *


class test_hatch(Scene):
    def construct(self):
        mob1 = Star().scale(2)
        # 1 hatch object creates parallel lines
        # 2 of them create rectangles
        hatch1 = Hatch_lines(mob1, angle=PI / 6, stroke_width=2)
        hatch1.add_updater(lambda mob: mob.become(Hatch_lines(mob1, angle=PI / 6, stroke_width=2)))
        hatch2 = Hatch_lines(mob1, angle=PI / 6 + PI / 2, offset=0.5, stroke_width=2)
        hatch2.add_updater(lambda mob: mob.become(Hatch_lines(mob1, angle=PI / 6 + PI / 2, offset=0.5, stroke_width=2)))

        self.add(hatch1,hatch2,mob1)
        self.play(Transform(mob1,Triangle()),run_time=2)
        self.wait()
        self.play(Transform(mob1, Circle()), run_time=2)
        self.wait()
        self.play(Transform(mob1,  Star().scale(2)), run_time=2)
        self.wait()

if __name__=="__main__":
    with tempconfig({"quality": "medium_quality", "disable_caching": True}):
        scene = test_hatch()
        scene.render()
