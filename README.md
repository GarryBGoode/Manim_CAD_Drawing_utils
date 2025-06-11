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

## pointer

```py
class test_dimension_pointer(Scene):
    def construct(self):
        mob1 = Round_Corners(Triangle().scale(2),0.3)
        p = ValueTracker(0)
        dim1 = Pointer_To_Mob(mob1,p.get_value(),r'triangel', pointer_offset=0.2)
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
![pointer](/media/examples/pointer_triangel.gif)


## dimension

```py
class test_dimension(Scene):
    def construct(self):
        mob1 = Round_Corners(Triangle().scale(2),0.3)
        dim1 = Angle_Dimension_Mob(mob1,
                                   0.2,
                                   0.6,
                                   offset=-4,
                                   ext_line_offset=1,
                                   color=RED)
        dim2 = Linear_Dimension(mob1.get_critical_point(RIGHT),
                                mob1.get_critical_point(LEFT),
                                direction=UP,
                                offset=2.5,
                                outside_arrow=True,
                                ext_line_offset=-1,
                                color=RED)
        self.play(Create(mob1))
        self.play(Create(dim1), run_time=3)
        self.play(Create(dim2), run_time=3)
        self.wait(3)
        self.play(Uncreate(mob1), Uncreate(dim2))

```
![dimension](/media/examples/test_dimension.gif)

## hatching

```py
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
```
![hatching](/media/examples/hatches.gif)


## Dashed lines
```py
class test_dash(Scene):
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
```
![hatching](/media/examples/dashes.gif)

## rounded corners 

```py
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

        mob1 = Chamfer_Corners(mob1, 0.25)
        mob2 = Chamfer_Corners(mob2,0.25)
        mob3 = Chamfer_Corners(mob3, 0.25)
        self.add(mob1,mob2,mob3,mob4)

```
![cutoff_corners](/media/examples/cutoff_corners.png)