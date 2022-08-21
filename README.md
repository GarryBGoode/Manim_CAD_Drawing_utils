# Manim CAD drawing utils

This is a collecion of various functions and utilities that help creating manimations that look like CAD drawings.
Also some other stuff that just looks cool.

Features:
- Round corners
- Chamfer corners
- Dimensions
- Dashed line, dashed mobject
- Path offset mapping


## Installation
`manim-CAD_Drawing_Utils` is a package on pypi, and can be directly installed using pip:
```
pip install manim-CAD_Drawing_Utils
```
Note: `CAD_Drawing_Utils` uses, and depends on SciPy and Manim.

## Usage
Make sure include these two imports at the top of the .py file
```py
from manim import *
from manim_cad_drawing_utils import *
```

# Examples

## rounded corners 

```py
class Test_round(Scene):
    def construct(self):
        mob1 = RegularPolygon(n=4,radius=1.5,color=PINK).rotate(PI/4)
        mob2 = Triangle(radius=1.5,color=TEAL)
        # making a cross
        crbase = Rectangle(height=0.5,width=3)
        mob3 = Union(crbase.copy().rotate(PI/4),crbase.copy().rotate(-PI/4),color=BLUE)
        mob4 = Circle(radius=1.3)
        mob2.shift(2.5*UP)
        mob3.shift(2.5*DOWN)
        mob1.shift(2.5*LEFT)
        mob4.shift(2.5*RIGHT)

        mob1 = round_corners(mob1, 0.25)
        mob2 = round_corners(mob2, 0.25)
        mob3 = round_corners(mob3, 0.25)
        self.add(mob1,mob2,mob3,mob4)
```
![rounded_corners](/media/examples/round_corners.png)

## cut off corners

```py
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

        mob1 = chamfer_corners(mob1, 0.25)
        mob2 = chamfer_corners(mob2,0.25)
        mob3 = chamfer_corners(mob3, 0.25)
        self.add(mob1,mob2,mob3,mob4)

```
![cutoff_corners](/media/examples/cutoff_corners.png)

## pointer

```py
class test_dimension_pointer(Scene):
    def construct(self):
        mob1 = round_corners(Triangle().scale(2),0.3)
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


```
![cutoff_corners](/media/examples/pointer_triangel.gif)


## dimension

```py
class test_dimension_base(Scene):
    def construct(self):
        mob1 = round_corners(Triangle().scale(2),0.3)
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


```
![cutoff_corners](/media/examples/dimension.png)

## hatching

```py
class test_hatch(Scene):
    def construct(self):
        mob1 = Star().scale(2)
        hatch1 = Hatch_lines(mob1,angle=PI/6,stroke_width=2)
        hatch2 = Hatch_lines(mob1,angle=PI/6+PI/2,stroke_width=2)
        self.add(mob1,hatch1,hatch2)


```
![cutoff_corners](/media/examples/hatches.png)
