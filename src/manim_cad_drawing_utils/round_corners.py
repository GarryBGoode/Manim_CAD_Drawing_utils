import numpy as np
from manim import *
from scipy.optimize import fsolve
from scipy.optimize import root
from scipy.optimize import root_scalar
from utils import angle_between_vectors_signed

__all__ = [
    "round_corner_param",
    "round_corners",
    "chamfer_corner_param",
    "chamfer_corners"
]


def round_corner_param(radius,curve_points_1,curve_points_2):
    bez_func_1 = bezier(curve_points_1)
    diff_func_1 = bezier((curve_points_1[1:, :] - curve_points_1[:-1, :]) / 3)
    bez_func_2 = bezier(curve_points_2)
    diff_func_2= bezier((curve_points_2[1:, :] - curve_points_2[:-1, :]) / 3)

    def find_crossing(p1,p2,n1,n2):
        t = fsolve(lambda t: p1[:2]+n1[:2]*t[0]-(p2[:2]+n2[:2]*t[1]),[0,0])
        return t, p1+n1*t[0]

    def rad_cost_func(t):
        angle_sign = np.sign( angle_between_vectors_signed(diff_func_1(t[0]),diff_func_2(t[1])))
        p1 = bez_func_1((t[0]))
        n1 = normalize(rotate_vector(diff_func_1(t[0]),angle_sign* PI / 2))
        p2 = bez_func_2((t[1]))
        n2 = normalize(rotate_vector(diff_func_2(t[1]), angle_sign* PI / 2))
        d = (find_crossing(p1, p2, n1, n2))[0]
        # 2 objectives for optimization:
        #  - the normal distances should be equal to each other
        #  - the normal distances should be equal to the target radius
        # I'm hoping that in this form at least a tangent circle will be found (first goal),
        # even if there is no solution at the desired radius. I don't really know, fsolve() and roots() is magic.
        return ((d[0])-(d[1])),((d[1])+(d[0])-2*radius)

    k = root(rad_cost_func,np.asarray([0.5,0.5]),method='hybr')['x']

    p1 = bez_func_1(k[0])
    n1 = normalize(rotate_vector(diff_func_1(k[0]), PI / 2))
    p2 = bez_func_2(k[1])
    n2 = normalize(rotate_vector(diff_func_2(k[1]), PI / 2))
    d, center = find_crossing(p1, p2, n1, n2)
    r = abs(d[0])
    start_angle = np.arctan2((p1-center)[1],(p1-center)[0])
    cval = np.dot(p1-center,p2-center)
    sval = (np.cross(p1-center,p2-center))[2]
    angle = np.arctan2(sval,cval)

    out_param = {'radius': r, 'arc_center': center, 'start_angle': start_angle, 'angle': angle}

    return out_param, k


def round_corners(mob:VMobject,radius=0.2):
    i=0
    while i < mob.get_num_curves() and i<1e5:
        ind1 = i % mob.get_num_curves()
        ind2 = (i+1) % mob.get_num_curves()
        curve_1 = mob.get_nth_curve_points(ind1)
        curve_2 = mob.get_nth_curve_points(ind2)
        handle1 = curve_1[-1,:]-curve_1[-2,:]
        handle2 = curve_2[1, :] - curve_2[0, :]
        # angle_test = (np.cross(normalize(anchor1),normalize(anchor2)))[2]
        angle_test = angle_between_vectors_signed(handle1,handle2)
        if abs(angle_test)>1E-6:
            params, k = round_corner_param(radius,curve_1,curve_2)
            cut_curve_points_1 = partial_bezier_points(curve_1, 0, k[0])
            cut_curve_points_2 = partial_bezier_points(curve_2, k[1], 1)
            loc_arc = Arc(**params,num_components=5)
            # mob.points = np.delete(mob.points, slice((ind1 * 4), (ind1 + 1) * 4), axis=0)
            # mob.points = np.delete(mob.points, slice((ind2 * 4), (ind2 + 1) * 4), axis=0)
            mob.points[ind1 * 4:(ind1 + 1) * 4, :] = cut_curve_points_1
            mob.points[ind2 * 4:(ind2 + 1) * 4, :] = cut_curve_points_2
            mob.points = np.insert(mob.points,ind2*4,loc_arc.points,axis=0)
            i=i+loc_arc.get_num_curves()+1
        else:
            i=i+1

        if i==mob.get_num_curves()-1 and not mob.is_closed():
            break

    return mob



def chamfer_corner_param(offset,curve_points_1,curve_points_2):
    # this is ugly, I know, don't judge
    if hasattr(offset,'iter'):
        ofs = [offset[0], offset[1]]
    else:
        ofs = [offset, offset]
    bez_func_1 = bezier(curve_points_1)
    bez_func_2 = bezier(curve_points_2)

    #copied from vectorized mobject length stuff
    def get_norms_and_refs(curve):
        sample_points = 10
        refs = np.linspace(0, 1, sample_points)
        points = np.array([curve(a) for a in np.linspace(0, 1, sample_points)])
        diffs = points[1:] - points[:-1]
        norms = np.cumsum(np.apply_along_axis(np.linalg.norm, 1, diffs))
        norms = np.insert(norms,0,0)
        return norms,refs

    norms1,refs1 = get_norms_and_refs(bez_func_1)
    norms2,refs2 = get_norms_and_refs(bez_func_2)
    a1 = (np.interp(norms1[-1]-ofs[0], norms1, refs1))
    a2 = (np.interp(ofs[1], norms2, refs2))
    p1 = bez_func_1(a1)
    p2 = bez_func_2(a2)
    param = {'start':p1,'end':p2}

    return param, [a1,a2]


def chamfer_corners(mob:VMobject,offset=0.2):
    i=0
    while i < mob.get_num_curves() and i<1e5:
        ind1 = i % mob.get_num_curves()
        ind2 = (i+1) % mob.get_num_curves()
        curve_1 = mob.get_nth_curve_points(ind1)
        curve_2 = mob.get_nth_curve_points(ind2)
        handle1 = curve_1[-1,:]-curve_1[-2,:]
        handle2 = curve_2[1, :] - curve_2[0, :]
        # angle_test = (np.cross(normalize(anchor1),normalize(anchor2)))[2]
        angle_test = angle_between_vectors_signed(handle1,handle2)
        if abs(angle_test)>1E-6:
            params, k = chamfer_corner_param(offset,curve_1,curve_2)
            cut_curve_points_1 = partial_bezier_points(curve_1, 0, k[0])
            cut_curve_points_2 = partial_bezier_points(curve_2, k[1], 1)
            loc_line = Line(**params)
            # mob.points = np.delete(mob.points, slice((ind1 * 4), (ind1 + 1) * 4), axis=0)
            # mob.points = np.delete(mob.points, slice((ind2 * 4), (ind2 + 1) * 4), axis=0)
            mob.points[ind1 * 4:(ind1 + 1) * 4, :] = cut_curve_points_1
            mob.points[ind2 * 4:(ind2 + 1) * 4, :] = cut_curve_points_2
            mob.points = np.insert(mob.points,ind2*4,loc_line.points,axis=0)
            i=i+loc_line.get_num_curves()+1
        else:
            i=i+1

        if i==mob.get_num_curves()-1 and not mob.is_closed():
            break

    return mob





# with tempconfig({"quality": "medium_quality", "disable_caching": True}):
#     scene = Test_corners()
#     scene.render()