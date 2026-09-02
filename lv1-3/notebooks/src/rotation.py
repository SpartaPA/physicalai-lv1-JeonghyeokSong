from __future__ import annotations
from src.vectors import skew, normalize, reject, det
import numpy as np



def rodrigues(axis, theta):
    w = normalize(axis)
    s = np.sin(theta)
    c = np.cos(theta)
    I = np.eye(3)

    return (I + (s*skew(w))) + ((1-c)*(skew(w)@skew(w)))



def rot_x(theta):
    t = theta
    c = np.cos(t)
    s = np.sin(t)
    return np.array([[1.0, 0.0, 0.0],
                    [0.0, c, -s],
                    [0.0, s, c]])


def rot_y(theta):
    t = theta
    c = np.cos(t)
    s = np.sin(t)
    return np.array([[c, 0.0, s],
                    [0.0, 1.0, 0.0],
                    [-s,0.0 , c]])


def rot_z(theta):
    t = theta
    c = np.cos(t)
    s = np.sin(t)
    return np.array([[c, -s, 0.0],
                    [s, c, 0.0],
                    [0.0,0.0,1.0]])

def orthogonality_error(M) -> float :

    M = M.copy().astype(float)
    R = M.T@M - np.eye(3)
    sum = 0.0
    for v in R:
        for i in v:
            sum+=(i*i)
    return sum**0.5


def gram_schmidt(M):

    R = M.copy()
    row = len(R)
    R[0] = normalize(R[0])
    for r in range(1,row):
        v = R[r]
        for i in range(r):
            v = reject(v, R[i])
        R[r] = normalize(v)
     
    return R
        
def is_rotation(M, eps = 1e-14):
    if orthogonality_error(M) < eps and np.abs(1-det(M)) < eps:
        return True
    else :
        return False

def axis_angle_from_matrix():
    return NotImplemented

def quaternion_from_axis_angle():
    return NotImplemented