from manim import *
from .utils import angle_between_vectors_signed
from .round_corners import *

class Pointer_Label_Free(VDict):
    def __init__(self,point, text:str, offset_vector=(RIGHT+DOWN),**kwargs):
        text_buff = 0.1
        if not 'stroke_width' in kwargs:
            kwargs['stroke_width'] = DEFAULT_STROKE_WIDTH
        super().__init__(**kwargs)
        self.add({'arrow': Arrow(start=point + offset_vector, end=point, buff=0, **kwargs)})

        if isinstance(text,str):
            textmob = Text(text,**kwargs)
        elif isinstance(text,Mobject):
            textmob = text
        else:
            textmob = Text('A',**kwargs)
        self.add({'text': textmob})


        self.twidth = (self['text'].get_critical_point(RIGHT)-self['text'].get_critical_point(LEFT))[0]
        self.twidth = self.twidth + text_buff * 2
        self.add({'line':Line(start=point+offset_vector,
                              end=point+offset_vector+self.twidth*np.sign(offset_vector[0]*RIGHT))})

        theight = (self['text'].get_critical_point(UP)-self['text'].get_critical_point(DOWN))[1]
        self['text'].move_to(self['line'].get_center()+UP*theight*0.75)


    def update_point(self, point, offset_vector=(RIGHT+DOWN)):
        self['arrow'].put_start_and_end_on(start=point+offset_vector, end=point)
        self['line'].put_start_and_end_on(start=point+offset_vector,
                                          end=point + offset_vector + self.twidth * np.sign(offset_vector[0] * RIGHT))
        # self['arrow'].add_tip(self['arrow'].start_tip, at_start=True)

        theight = (self['text'].get_critical_point(UP)-self['text'].get_critical_point(DOWN))[1]
        self['text'].move_to(self['line'].get_center()+UP*theight*0.75)


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
            main_line = Arrow(start=startpoint, end=endpoint, buff=0,
                              max_tip_length_to_length_ratio=1,
                              max_stroke_width_to_length_ratio=1000,
                              tip_length=tip_len,
                              **kwargs)
            main_line.add_tip(at_start=True,tip_length=tip_len)
        else:
            main_line = Line(start=startpoint, end=endpoint,**kwargs)
            arrow_line1 = Arrow(end=startpoint,
                                start=startpoint+tip_len*3*(normalize(startpoint-endpoint)),
                                buff=0,
                                max_tip_length_to_length_ratio=1,
                                max_stroke_width_to_length_ratio=1000,
                                tip_length=tip_len,
                                **kwargs
                               )
            arrow_line2 = Arrow(end=endpoint,
                                start=endpoint-tip_len*3*(normalize(startpoint-endpoint)),
                                buff=0,
                                max_tip_length_to_length_ratio=1,
                                max_stroke_width_to_length_ratio=1000,
                                tip_length=tip_len,
                                **kwargs
                               )
            main_line.add(arrow_line1)
            main_line.add(arrow_line2)

        self.add({'main_line': main_line})
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


class Angle_Dimension_3point(VGroup):
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
        self.add(line1,line2)

        if not outside_arrow:

            base_arc.add_tip(tip_length=tip_len)
            base_arc.add_tip(tip_length=tip_len,at_start=True)
            self.add(base_arc)
        else:
            angle_ext = tip_len*3/radius * np.sign(angle_1)
            ext_arc_1 = Arc(radius=radius,
                            start_angle=angle_0-angle_ext,
                            angle=+angle_ext,
                            arc_center=arc_center,
                            **kwargs)
            ext_arc_2 = Arc(radius=radius,
                            start_angle=(angle_0 + angle_1 + angle_ext)%TAU,
                            angle=-angle_ext,
                            arc_center=arc_center,
                            **kwargs)
            ext_arc_1.add_tip(tip_length=tip_len)
            ext_arc_2.add_tip(tip_length=tip_len)
            base_arc.add(ext_arc_1,ext_arc_2)
            self.add(base_arc)

        if isinstance(text,str):
            textmob = Text(text)
        elif isinstance(text,Mobject):
            textmob = text
        else:
            textmob = Text(f"{abs(angle_1/DEGREES):.2f}",**kwargs)

        pos_text = base_arc.point_from_proportion(0.5)
        angle_text = (angle_of_vector(base_arc.point_from_proportion(0.5+1e-6) -
                                      (base_arc.point_from_proportion(0.5-1e-6))) + PI / 2) % PI - PI / 2
        if abs(angle_text+PI/2)<1e-8:
            angle_text=PI/2
        self.text_h = textmob.height
        textmob.rotate(angle_text)
        textmob.move_to(pos_text + rotate_vector(UP,angle_text)*self.text_h)
        self.add(textmob)






