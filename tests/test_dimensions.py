from manim import *
from dimensions import *
from round_corners import *

class test_dimension_pointer(Scene):
    def construct(self):
        mob1 = round_corners(Triangle().scale(2),0.3)
        p = ValueTracker(0)
        dim1 = Pointer_To_Mob(mob1,p.get_value(),r'triangel')
        dim1.add_updater(lambda mob: mob.update_mob(mob1,p.get_value()))
        dim1.update()

        dim2 = Linear_Dimension(mob1.point_from_proportion(0),mob1.point_from_proportion(0.2),
                                direction=UP,
                                offset=-0,
                                color=RED)
        # dim3 = Linear_Dimension(mob1.point_from_proportion(2/3),mob1.point_from_proportion(1/3),
        #                         direction=DOWN,color=RED,
        #                         outside_arrow=True)



        # self.add(mob1,dim1)
        self.play(Create(mob1))
        self.play(Create(dim1))
        self.play(p.animate.set_value(1),run_time=10)
        self.play(Uncreate(mob1),Uncreate(dim1))
        self.wait()

class test_dimension(Scene):
    def construct(self):
        mob1 = round_corners(Triangle().scale(2),0.3)
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