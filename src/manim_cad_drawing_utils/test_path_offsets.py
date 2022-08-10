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

        def ofs_func(t):
            x = 30 * (t-vt.get_value())
            x2 = 30 * (t - vt.get_value()-1)
            x3 = 30 * (t - vt.get_value()+1)
            return 0.02 + 0.3* (np.exp(-(x)**2) + np.exp(-(x3)**2) + np.exp(-(x2)**2))
        ofspath = Path_Offset_Mobject(mob1,ofs_func,fill_color=RED,fill_opacity=1,stroke_opacity=0)

        def ofs_updater(mob):
            curve1, curve2 = mob.generate_offset_paths()
            mob['ofs_mobj'].points = curve1.points
            curve2.reverse_direction()
            mob['ofs_mobj'].points = np.append(mob['ofs_mobj'].points, curve2.points, axis=0)


        ofspath.add_updater(ofs_updater)
        # ofspath.update()
        c = Circle(radius=0.05)
        c2 = c.copy()
        # pather1 = Path_mapper(mob1)
        # def asdater(mob):
        #     a = vt.get_value()
        #     p = pather1.path.point_from_proportion(a)
        #     v = pather1.get_tangent_unit_vector(a*pather1.get_path_length())*2
        #     mob.move_to(p+v)
        # c.add_updater(asdater)
        # c2.add_updater(lambda mob: mob.move_to(mob1.point_from_proportion(vt.get_value())))
        # dash1.add_updater(lambda mob: dash1['dashes']=)
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

#
# with tempconfig({"quality": "medium_quality", "disable_caching": True}):
#     scene = test()
#     scene.render()