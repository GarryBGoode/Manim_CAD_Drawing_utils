from manim import *
from dimensions import *
from round_corners import *
from path_mapper import *

class test_path_mapper_anim(Scene):
    def construct(self):
        mob1 = round_corners(Triangle(fill_color=TEAL,fill_opacity=0).scale(3),0.5)
        PM = Path_mapper(mob1)
        mob2 = mob1.copy()
        mob1.shift(LEFT * 2.5)
        mob2.shift(RIGHT * 2.5)

        self.play(Create(mob1,rate_func=PM.equalize_rate_func(smooth)),Create(mob2),run_time=5)
        self.wait()


class test_path_mapper_curve(Scene):
    def construct(self):
        mob1 = round_corners(Triangle().scale(3),0.5)
        PM = Path_mapper(mob1)
        vt = ValueTracker(0)

        mob2 = Circle(radius=0.1)
        def mob2_update(mob):
            a = vt.get_value()
            p = mob1.point_from_proportion(a)
            # s = PM.length_from_alpha(a)
            s = a*PM.get_path_length()
            ofs = PM.get_normal_unit_vector(s) * PM.get_curvature_vector(s)[2]
            mob.move_to(p+ofs)
        mob2.add_updater(mob2_update)

        curve_t = Text('0')
        def t_updater(mob):
            val = PM.get_curvature_vector(vt.get_value() * PM.get_path_length())[2]
            mob.become(Text(f'{val:.3}').next_to(mob1))
        curve_t.add_updater(t_updater)

        curve_t.next_to(mob1)

        self.play(Create(mob1,rate_func=PM.equalize_rate_func(smooth)))
        self.play(Create(mob2))
        self.add(curve_t)
        self.wait()
        self.play(vt.animate.set_value(1),run_time=20,rate_func=linear)
        self.wait()

#
with tempconfig({"quality": "medium_quality", "disable_caching": True}):
    scene = test_path_mapper_curve()
    scene.render()