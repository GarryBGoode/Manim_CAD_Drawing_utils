from manim import *
from .utils import angle_between_vectors_signed
from .round_corners import *
from .path_mapper import *

class Pointer_Label_Free(VDict):
    def __init__(self,point, text:str, offset_vector=(RIGHT+DOWN),**kwargs):
        text_buff = 0.1
        if not 'stroke_width' in kwargs:
            kwargs['stroke_width'] = DEFAULT_STROKE_WIDTH
        super().__init__(**kwargs)

        if isinstance(text,str):
            textmob = Text(text,**kwargs)
        elif isinstance(text,Mobject):
            textmob = text
        else:
            textmob = Text('A',**kwargs)
        self.add({'text': textmob})
        self.twidth = (self['text'].get_critical_point(RIGHT)-self['text'].get_critical_point(LEFT))[0]
        self.twidth = self.twidth + text_buff * 2

        # self.add({'arrow': Arrow(start=point + offset_vector, end=point, buff=0, **kwargs)})

        dim_line = VMobject(**kwargs).set_points_as_corners([point,
                                                             point + offset_vector,
                                                             point+offset_vector +
                                                             self.twidth*np.sign(offset_vector[0])*RIGHT])
        self.add({'line':dim_line})
        self.add({'arrow':CAD_ArrowHead(self['line'],anchor_point=0,**kwargs)})
        self['arrow'].arrowhead.rotate(PI,about_point=ORIGIN)
        self['arrow'].add_updater(self['arrow'].default_updater)
        theight = (self['text'].get_critical_point(UP)-self['text'].get_critical_point(DOWN))[1]
        self['text'].move_to(self['line'].points[3,:]+UP*theight*0.75,aligned_edge=LEFT*np.sign(offset_vector[0]))


    def update_point(self, point, offset_vector=(RIGHT+DOWN)):
        # self['arrow'].put_start_and_end_on(start=point+offset_vector, end=point)
        # self['line'].put_start_and_end_on(start=point+offset_vector,
        #                                   end=point + offset_vector + self.twidth * np.sign(offset_vector[0] * RIGHT))
        # self['arrow'].add_tip(self['arrow'].start_tip, at_start=True)

        self['line'].set_points_as_corners([point,
                                            point + offset_vector,
                                            point + offset_vector +
                                            self.twidth * np.sign(offset_vector[0]) * RIGHT])

        theight = (self['text'].get_critical_point(UP)-self['text'].get_critical_point(DOWN))[1]
        self['text'].move_to(self['line'].points[3,:]+UP*theight*0.75,aligned_edge=LEFT*np.sign(offset_vector[0]))


class Pointer_To_Mob(Pointer_Label_Free):
    def __init__(self, mob:Mobject, proportion,  text:str, dist=1, **kwargs):
        point = mob.point_from_proportion(proportion)

        # if the mob center and point happens to be the same, it causes problems
        # it can happen if all the mob is 1 point
        offset_ref = point - mob.get_center()
        if np.linalg.norm(offset_ref)>1e-6:
            offset = normalize(point - mob.get_center())*dist
        else:
            # I had no better idea to handle this than to go upright
            offset = normalize(RIGHT+UP)*dist
        super().__init__(point,text, offset_vector=offset,**kwargs)

    def update_mob(self,mob, proportion, dist=1):
        point = mob.point_from_proportion(proportion)
        # if the mob center and point happens to be the same, it causes problems
        # it can happen if all the mob is 1 point
        offset_ref = point - mob.get_center()
        if np.linalg.norm(offset_ref) > 1e-6:
            offset = normalize(point - mob.get_center()) * dist
        else:
            # I had no better idea to handle this than to go upright
            offset = normalize(RIGHT + UP) * dist
        super().update_point(point,offset)


class Linear_Dimension(VDict):
    def __init__(self, start,end, text=None,direction=ORIGIN, outside_arrow=False, offset=2, **kwargs):
        super().__init__(**kwargs)
        diff_vect = end-start
        norm_vect = normalize(rotate_vector(diff_vect,PI/2))
        if not any(direction!=0):
            ofs_vect = norm_vect * offset
            ofs_dir = norm_vect
        else:
            ofs_vect = direction * offset
            ofs_dir = direction
        if not 'stroke_width' in kwargs:
            kwargs['stroke_width'] = DEFAULT_STROKE_WIDTH

        startpoint = start + ofs_dir * np.dot(end-start,ofs_dir)/2+ofs_vect
        endpoint = end - ofs_dir * np.dot(end - start, ofs_dir) / 2 + ofs_vect

        tip_len=0.2

        if not outside_arrow:
            main_line = Line(start=startpoint, end=endpoint,**kwargs)
            arrow1 = CAD_ArrowHead(main_line,anchor_point=1, arrow_size=tip_len, reversed_arrow=False)
            arrow2 = CAD_ArrowHead(main_line, anchor_point=0, arrow_size=tip_len, reversed_arrow=True)
        else:
            extension = tip_len*3*(normalize(endpoint-startpoint))
            main_line = Line(start=startpoint-extension,
                             end=endpoint+extension,
                             **kwargs)
            arrow1 = CAD_ArrowHead(main_line, anchor_point=1, arrow_size=tip_len, reversed_arrow=True)
            arrow1.arrowhead.shift(extension*RIGHT)
            arrow1.default_updater(0)
            arrow2 = CAD_ArrowHead(main_line, anchor_point=0, arrow_size=tip_len, reversed_arrow=False)
            arrow2.arrowhead.shift(-extension * RIGHT)
            arrow2.default_updater(0)

        self.add({'main_line': main_line})
        self.add({'arrow1': arrow1})
        self.add({'arrow2': arrow2})
        self.add({'ext_line_1': Line(start=start,
                                     end=startpoint + 0.25 * (normalize(startpoint-start)),
                                     **kwargs)})
        self.add({'ext_line_2': Line(start=end,
                                     end=endpoint + 0.25 * (normalize(endpoint-end)),
                                     **kwargs)})

        if isinstance(text,str):
            textmob = Text(text)
        elif isinstance(text,Mobject):
            textmob = text
        else:
            dist = np.linalg.norm(main_line.start-main_line.end)
            textmob = Text(f"{dist:.2}",**kwargs)

        angle = (main_line.get_angle()+PI/2)%PI-PI/2
        if abs(angle+PI/2)<1e-8:
            angle=PI/2
        self.text_h = textmob.height
        textmob.rotate(angle)
        textmob.move_to(self.submobjects[0].get_center() + rotate_vector(UP,angle)*self.text_h)
        self.add({'text': textmob})


class Angle_Dimension_3point(VDict):
    def __init__(self,start,end, arc_center,offset=2,text=None, outside_arrow=False,**kwargs):
        super().__init__(**kwargs)
        if not 'stroke_width' in kwargs:
            kwargs['stroke_width'] = DEFAULT_STROKE_WIDTH

        self.angle = angle_between_vectors_signed(start-arc_center,end-arc_center)
        radius = (np.linalg.norm(start-arc_center)+np.linalg.norm(end-arc_center))/2 + offset
        angle_0 = angle_of_vector(start-arc_center)
        angle_1 = angle_between_vectors_signed(start-arc_center,end-arc_center)

        tip_len = 0.2
        base_arc = Arc(radius=radius,
                       start_angle=angle_0,
                       arc_center=arc_center,
                       angle=angle_1,
                       **kwargs)
        arc_p0 = base_arc.point_from_proportion(0)
        arc_p1 = base_arc.point_from_proportion(1)
        line1 = Line(start=start,
                     end=arc_p0 + normalize(arc_p0-start)*tip_len,
                     **kwargs
        )
        line2 = Line(start=end,
                     end=arc_p1 + normalize(arc_p1-end)*tip_len,
                     **kwargs
                     )
        # self.add(line1,line2)
        self.add({'ext_line_1': line1})
        self.add({'ext_line_2': line2})
        if not outside_arrow:

            # base_arc.add_tip(tip_length=tip_len)
            # base_arc.add_tip(tip_length=tip_len,at_start=True)
            arrow1 = CAD_ArrowHead(base_arc, anchor_point=1,reversed_arrow=False)
            arrow2 = CAD_ArrowHead(base_arc, anchor_point=0, reversed_arrow=True)
            self.add({'base_arc':base_arc})
            self.add({'arrow_1':arrow1})
            self.add({'arrow_2': arrow2})
        else:
            extension = tip_len*3 * np.sign(angle_1)
            angle_ext = extension/radius
            # ext_arc_1 = Arc(radius=radius,
            #                 start_angle=angle_0-angle_ext,
            #                 angle=+angle_ext,
            #                 arc_center=arc_center,
            #                 **kwargs)
            # ext_arc_2 = Arc(radius=radius,
            #                 start_angle=(angle_0 + angle_1 + angle_ext)%TAU,
            #                 angle=-angle_ext,
            #                 arc_center=arc_center,
            #                 **kwargs)
            # ext_arc_1.add_tip(tip_length=tip_len)
            # ext_arc_2.add_tip(tip_length=tip_len)
            # base_arc.add(ext_arc_1,ext_arc_2)
            base_arc = Arc(radius=radius,
                           start_angle=angle_0-angle_ext,
                           angle=+self.angle + angle_ext * 2,
                           arc_center=arc_center,
                           **kwargs)
            arrow1 = CAD_ArrowHead(base_arc, anchor_point=1, arrow_size=tip_len, reversed_arrow=True)
            arrow1.arrowhead.shift(extension * RIGHT)
            arrow1.default_updater(0)
            arrow2 = CAD_ArrowHead(base_arc, anchor_point=0, arrow_size=tip_len, reversed_arrow=False)
            arrow2.arrowhead.shift(-extension * RIGHT)
            arrow2.default_updater(0)
            self.add({'base_arc': base_arc})
            self.add({'arrow_1': arrow1})
            self.add({'arrow_2': arrow2})

        if isinstance(text,str):
            textmob = Text(text)
        elif isinstance(text,Mobject):
            textmob = text
        else:
            textmob = Text(f"{abs(angle_1/DEGREES):.0f}",**kwargs)

        pos_text = base_arc.point_from_proportion(0.5)
        angle_text = (angle_of_vector(base_arc.point_from_proportion(0.5+1e-6) -
                                      (base_arc.point_from_proportion(0.5-1e-6))) + PI / 2) % PI - PI / 2
        if abs(angle_text+PI/2)<1e-8:
            angle_text=PI/2
        self.text_h = textmob.height
        textmob.rotate(angle_text)
        textmob.move_to(pos_text + rotate_vector(UP,angle_text)*self.text_h)
        self.add({'text': textmob})



class CAD_ArrowHead(Curve_Warp):
    def __init__(self,
                 target_curve: VMobject,
                 anchor_point=1,
                 arrow_size=DEFAULT_ARROW_TIP_LENGTH,
                 reversed_arrow=False,
                 **kwargs):

        # set default value
        self.__reversed_arrow = False
        self.arrowhead = VMobject()
        self.arrowhead.set_points_as_corners([(LEFT*2+UP),
                                              ORIGIN,
                                              LEFT*2+DOWN])


        # set input value
        self.reversed_arrow = reversed_arrow
        self.set_arrow_size(arrow_size)
        self.arrowhead.match_style(target_curve)

        super().__init__(self.arrowhead,target_curve,anchor_point=anchor_point,**kwargs)


    def default_updater(self,mob):
        self.PM.generate_length_map()
        self.generate_points()

    def get_tip_pos(self):
        ''' By convention, the tip of the arrow should be the right-most point of the shape, unless it's reversed'''
        if self.__reversed_arrow:
            return self.arrowhead.get_critical_point(LEFT)[0]
        else:
            return self.arrowhead.get_critical_point(RIGHT)[0]

    def set_arrow_size(self,arrow_size):
        act_size = (self.arrowhead.get_critical_point(RIGHT)-self.arrowhead.get_critical_point(LEFT))[0]
        if act_size!=0:
            self.arrowhead.shift(-self.get_tip_pos()*RIGHT)
            self.arrowhead.points *= arrow_size/act_size
            self.arrowhead.shift(+self.get_tip_pos() * RIGHT)

    def flip_arrow(self):
        self.arrowhead.flip()

    @property
    def reversed_arrow(self):
        return self.__reversed_arrow

    @reversed_arrow.setter
    def reversed_arrow(self, rev):
        if rev != self.__reversed_arrow:
            self.flip_arrow()
        self.__reversed_arrow = rev
