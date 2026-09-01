from __future__ import annotations
import numpy as np


def make_T(R,t):
    
    if type(t) != "numpy.ndarray":
        t = np.array(t)
    _r = R.copy()
    _t = t.reshape(-1,1)

    T = np.hstack((_r,_t))
    T = np.vstack((T,np.array([0,0,0,1])))
    
    return T


def inv_T(T):
    R = T.copy()[:3,:3]
    t = T.copy()[:3,3].reshape(-1,1)

    T_i = np.hstack((R.T,-R.T@t))
    T_i = np.vstack((T_i,np.array([0,0,0,1])))

    return T_i


def inv_T_batch():
    return NotImplemented


def to_homogeneous(v, w):
    _v = np.append(v.copy(),w)
    return _v


def transform_point(T,v):
    _v = to_homogeneous(v.copy(),1)
    t_p = T@_v

    return t_p[:3]
    

def transform_points():
    return NotImplemented


def transform_direction(T,v):
    _v = to_homogeneous(v.copy(),0)
    r_p = T@_v
    
    return r_p[:3]

def least_squares_normal_equation():
    return NotImplemented


def rmse():
    return NotImplemented
