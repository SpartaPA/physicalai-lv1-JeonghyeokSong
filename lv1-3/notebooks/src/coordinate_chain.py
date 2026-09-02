from __future__ import annotations
import numpy as np

from src.rotation import rot_x, rot_y, rot_z
from src.transform import make_T, inv_T, transform_points

class CoordinateChain:
    def __init__(self, root="base"):
        return None

    def add(self, parent, child, T):
        return NotImplementedError

    def get(self, parent, child):
        return NotImplementedError

    def T_from_root(self, frame):
        return NotImplementedError

    def T(self, a, b):
        return NotImplementedError

    def transform(self, a, b, pts):
        return NotImplementedError

def default_chain():
    chain = CoordinateChain()
    return chain

def camera_point_to_base(p_cam, chain):
    raise NotImplementedError

def base_point_to_camera(p_base, chain):
    raise NotImplementedError
