import numpy as np

__all__ = ["angle_between_vectors_signed"]

def angle_between_vectors_signed(v1,v2):
    '''
    Get signed angle between vectors according to right hand rule.
    :param v1: first vector
    :param v2: second vector
    :return: angle of rotation that rotates v1 to be co-linear with v2. Range: -PI...+PI
    '''
    cval = np.dot(v1, v2)
    sval = (np.cross(v1, v2))[2]
    return np.arctan2(sval, cval)