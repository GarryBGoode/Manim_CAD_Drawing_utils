from manim import *
from manim_cad_drawing_utils import *

class test_dimension_pointer(Scene):
    def construct(self):
        mob1 = Round_Corners(Triangle().scale(2),0.3)
        p = ValueTracker(0)
        dim1 = Pointer_To_Mob(mob1,p.get_value(),r'triangel')
        dim1.add_updater(lambda mob: mob.update_mob(mob1,p.get_value()))
        dim1.update()
        PM = Path_mapper(mob1)
        self.play(Create(mob1),rate_func=PM.equalize_rate_func(smooth))
        self.play(Create(dim1))
        self.play(p.animate.set_value(1),run_time=10)
        self.play(Uncreate(mob1,rate_func=PM.equalize_rate_func(smooth)))
        self.play(Uncreate(dim1))
        self.wait()

class test_dimension_base(Scene):
    def construct(self):
        mob1 = Round_Corners(Triangle().scale(2),0.3)
        dim1 = Linear_Dimension(mob1.get_critical_point(UP),
                                mob1.get_critical_point(DOWN),
                                direction=RIGHT,
                                offset=3,
                                color=RED)
        dim2 = Linear_Dimension(mob1.get_critical_point(RIGHT),
                                mob1.get_critical_point(LEFT),
                                direction=UP,
                                offset=-3,
                                color=RED)

        self.add(mob1,dim1,dim2)

class test_dimension(Scene):
    def construct(self):
        mob1 = Round_Corners(Triangle().scale(2),0.3)
        p = ValueTracker(0)
        dim2 = Linear_Dimension(mob1.point_from_proportion(0),mob1.point_from_proportion(0.2),
                                direction=UP,
                                offset=-0,
                                color=RED)

        self.play(Create(mob1))
        self.play(Create(dim2))
        self.wait(2)
        self.play(Uncreate(mob1), Uncreate(dim2))


class test_angle(Scene):
    def construct(self):
        mob1 = Triangle().scale(2)
        dim3 = Angle_Dimension_3point(mob1.get_nth_curve_points(1)[0],
                                      mob1.get_nth_curve_points(0)[0],
                                      mob1.get_nth_curve_points(2)[0],
                                      offset=-1.5,
                                      outside_arrow=True,
                                      color=RED)
        self.add(mob1,dim3)

# with tempconfig({"quality": "medium_quality", "disable_caching": True}):
#     scene = test_dimension()
#     scene.render()