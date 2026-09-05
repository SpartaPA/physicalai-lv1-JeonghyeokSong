from __future__ import annotations
import numpy as np

from src.vectors import gauss_eliminate

def make_T(R,t):
    
    if not isinstance(t,np.ndarray):
        t = np.array(t)
    _r = R.copy()
    _t = t.reshape(-1,1)

    T = np.hstack((_r,_t))
    T = np.vstack((T,np.array([0,0,0,1])))
    
    return T

def inv_T(T):
    R = T[:3,:3].copy()
    t = T[:3,3].copy().reshape(-1,1)

    T_i = np.hstack((R.T,-R.T@t))
    T_i = np.vstack((T_i,np.array([0,0,0,1])))

    return T_i

def inv_T_batch(Ts):

    R = Ts[:,:3,:3].copy()
    t = Ts[:,:3,3].copy()
    
    Rt = R.swapaxes(1, 2)
    new_t = -Rt @ t[..., None]
    new_t = new_t.squeeze(-1)

    out = np.zeros((len(Ts),4,4))
    out[:,:3,:3] = Rt
    out[:,:3,3] = new_t
    out[:,3,3] = 1
    return out

def to_homogeneous(v, w):
    if not isinstance(v,np.ndarray):
            v = np.array(v)
    _w = np.full(v.shape[:-1]+(1,), w)
    _v = np.concatenate((v.copy(),_w),axis=-1)
    return _v

def transform_point(T,v):
    _v = to_homogeneous(v.copy(),1)
    t_p = T@_v

    return t_p[:3]
    
def transform_points(T,pts):
    ph = np.hstack((pts,np.ones((len(pts),1))))
    O = ph@T.T

    return O[:,:3]  

def transform_direction(T,v):
    _v = to_homogeneous(v.copy(),0)
    r_p = T@_v
    
    return r_p[:3]

def least_squares_normal_equation(A,b):

    A = A.copy()
    AtA = A.T@A
    Ab = A.T@b

    x,_ = gauss_eliminate(AtA, Ab)
    r = b - A.copy()@x

    return x , r

def rmse(r):

    sum = 0.0
    for i in r:
        sum += i**2
        
    mean = sum / len(r)
    
    return np.sqrt(mean)