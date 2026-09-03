from __future__ import annotations
import numpy as np

from src.rotation import rot_x, rot_y, rot_z
from src.transform import make_T, inv_T, transform_points

class CoordinateChain:
    def __init__(self, root="base"):
        self.root = root
        self.edges = {}
        self.parent = {}
        return None

    def add(self, parent, child, T):
        self.parent[child] = parent
        self.edges[parent,child] = T

    def get(self, parent, child):
        return self.edges[parent,child]

    def T_from_root(self, frame):
        T = np.eye(4)
        node = frame
        while node != self.root:
            p = self.parent[node]
            T = self.get(p, node) @T
            node = p
        return T

    def T(self, a, b):
        return inv_T(self.T_from_root(a)) @ self.T_from_root(b)
        
    def transform(self, a, b, pts):
        pts = np.asarray(pts)
        single = pts.ndim == 1

        P = np.atleast_2d(pts)

        out = transform_points(self.T(a,b), P)
        # print(out)
        return out[0] if single else out
        

def default_chain():
    chain = CoordinateChain()

    R_00 = rot_z(np.deg2rad(30))
    T_00 = np.array([0.3,0.0,0.4])
    T_bl = make_T(R_00, T_00)
    chain.add("base", "link", T_bl)

    R_10 = rot_y(np.rad2deg(-20))
    R_11 = rot_x(np.rad2deg(90))
    T_10 = np.array([0.1, 0.05, 0.15])
    T_lc = make_T(R_11@R_10, T_10)
    chain.add("link", "camera", T_lc)                
    
    return chain

def camera_point_to_base(p_cam, chain):
    return chain.transform("base", "camera", p_cam)

def base_point_to_camera(p_base, chain):
    return chain.transform("camera", "base", p_base)
    raise NotImplementedError
