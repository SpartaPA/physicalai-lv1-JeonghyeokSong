import math

def distance (ax, ay, bx, by):
    return math.hypot(bx - ax, by - ay)

def normalize_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))

def reached(dist, tolerance):
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    return dist < tolerance

