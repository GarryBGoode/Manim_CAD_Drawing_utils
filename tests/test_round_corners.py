from manim import *
from manim_cad_drawing_utils import *

class Test_chamfer(Scene):
    def construct(self):
        mob1 = RegularPolygon(n=4,radius=1.5,color=PINK).rotate(PI/4)
        mob2 = Triangle(radius=1.5,color=TEAL)
        crbase = Rectangle(height=0.5,width=3)
        mob3 = Union(crbase.copy().rotate(PI/4),crbase.copy().rotate(-PI/4),color=BLUE)
        mob4 = Circle(radius=1.3)
        mob2.shift(2.5*UP)
        mob3.shift(2.5*DOWN)
        mob1.shift(2.5*LEFT)
        mob4.shift(2.5*RIGHT)

        mob1 = Chamfer_Corners(mob1, 0.25)
        mob2 = Chamfer_Corners(mob2,0.25)
        mob3 = Chamfer_Corners(mob3, 0.25)
        self.add(mob1,mob2,mob3,mob4)

class Test_round(Scene):
    def construct(self):
        mob1 = RegularPolygon(n=4,radius=1.5,color=PINK).rotate(PI/4)
        mob2 = Triangle(radius=1.5,color=TEAL)
        crbase = Rectangle(height=0.5,width=3)
        mob3 = Union(crbase.copy().rotate(PI/4),crbase.copy().rotate(-PI/4),color=BLUE)
        mob4 = Circle(radius=1.3)
        mob2.shift(2.5*UP)
        mob3.shift(2.5*DOWN)
        mob1.shift(2.5*LEFT)
        mob4.shift(2.5*RIGHT)

        mob1 = Round_Corners(mob1, 0.25)
        mob2 = Round_Corners(mob2, 0.25)
        mob3 = Round_Corners(mob3, 0.25)
        self.add(mob1,mob2,mob3,mob4)


class Patrick(Scene):
    def construct(self):
        mob1 = Star(outer_radius=4)
        # randomize handles
        mob1.points[1::4,:] = mob1.points[1::4,:]+rotate_vector(UP*(0.4*np.random.random()+0.2),np.random.random()*TAU)
        mob1.points[2::4, :] = mob1.points[2::4, :] + rotate_vector(UP * (0.4*np.random.random()+0.2), np.random.random() * TAU)

        pat = Round_Corners(mob1,radius=0.35)
        pat.set_fill(color=RED_C,opacity=1)


        self.add(pat)
