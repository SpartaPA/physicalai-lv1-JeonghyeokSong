from __future__ import annotations
import numpy as np


def rad2deg(rad) -> float:
    return rad * (180.0 /  np.pi)

def deg2rad(deg) -> float:
    return deg * (np.pi / 180.0)

def vector_check(v):
    l = len(v)
    if l > 3 or l < 3 :
        raise ValueError(f"{v}는 Vector3 이 아닙니다.")

def dot(a, b) -> float:
    """내적"""
    ax = a[0]
    ay = a[1]
    az = a[2]

    bx = b[0]
    by = b[1]
    bz = b[2]
    
    return ax*bx + ay*by + az*bz

def norm(v) -> float:
    """노름"""
    vx = v[0]
    vy = v[1]
    vz = v[2]

    return (vx*vx + vy*vy + vz*vz)**0.5


def normalize(v, eps=1e-12) -> np.array:
    """정규화"""

    vx = v[0]
    vy = v[1]
    vz = v[2]
    n = norm(v)

    if n < eps:
    
        raise ValueError("길이가 0인 벡터는 Nomalize 할 수 없습니다.")
    else:
        return np.array([vx/n,vy/n,vz/n])


def angle_between(a, b, degrees=True) -> float:
    """사이각"""
    na = normalize(a)
    nb = normalize(b)
    _dot = np.clip(dot(na, nb),-1.0,1.0)
    arc = np.arccos(_dot)
    
    if degrees :  
        return rad2deg(arc)
    else :
        return arc


def project(a, b) -> np.array:
    """정사영"""
    _fracx = dot(b,b)
    _fracy = dot(a,b)
    return np.array((_fracy/_fracx)*b)


def reject(a, b, eps=1e-12) -> np.array:
    """수직성분"""
    proj = project(a,b)
    v = a - proj
    return v


def cross(a, b) -> np.array:

    ax = a[0]
    ay = a[1]
    az = a[2]

    bx = b[0]
    by = b[1]
    bz = b[2]

    return np.array([ay*bz - az*by, az*bx - ax*bz, ax*by - ay*bx])

def skew(a) -> np.array:
    """반대칭행렬"""
    ax = a[0]
    ay = a[1]
    az = a[2]

    return np.array([[0,-az,ay],
                    [az,0,-ax],
                    [-ay,ax,0]])

def plane_normal(p1, p2, p3):
    """평면법선"""
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)
    p3 = np.asarray(p3, dtype=float)
    
    u1 = p2 - p1
    u2 = p3 - p1

    return normalize(cross(u1,u2))

def row_echelon(M, eps = 1e-9) -> np.array:
    """행사다리꼴"""
    row, col = np.shape(M)
    M = M.copy()
    swap = 0
    
    for r, m in enumerate(M):
        target_r = r + np.argmax(np.abs(M[r:,r]))
        if target_r > r:
            temp_m = M[target_r].copy()
            M[target_r] = M[r]
            M[r] = temp_m
            swap += 1
        
        for i in range(row):
            if i > r:
                x = m[r]
                nx = M[i,r]
                if nx != 0 :
                    
                    frac = nx/x
                    M[i] = M[i] - M[r]*frac

    pivot = np.array([])
    for r, m in enumerate(M):
        index = np.where(np.abs(m) > eps)
        if len(index[0]) != 0:
            pivot = np.append(pivot,m[index[0][0]])
    
    return M, pivot, swap

def rank(M):
    """랭크"""
    _, pivot, _ = row_echelon(M)
    return len(pivot)

def det(M) -> int:
    """행렬식"""
    _, pivot, swap = row_echelon(M)

    if len(pivot) < len(M) :
        return 0
    else:
        if swap%2 :
            return np.prod(pivot) * -1
        else :
            return np.prod(pivot)

def gauss_eliminate(a, b, pivoting=True, verbose=True):
    row, col = np.shape(a)
    M = np.hstack((a.copy(),b.reshape(-1,1)))
    steps = [M.copy()]

    for r, m in enumerate(M):
        target_r = r + np.argmax(np.abs(M[r:,r]))
        if pivoting :
            if target_r > r:
                temp_m = M[target_r].copy()
                M[target_r] = M[r]
                M[r] = temp_m
            
        for i in range(row):
            if i > r:
                x = m[r]
                nx = M[i,r]
                if nx != 0 :
                    frac = nx/x
                    M[i] = M[i] - M[r]*frac

        steps.append(M.copy())

    ans = np.array([])
    for i in range(row):
        r = row-1-i
        m = M[r]

        a = M[r,r]
        b = M[r,-1]

        for j in range(len(ans)):
            xb = M[r,(row-1-j)] * ans[j]
            b -= xb
        
        ans = np.append(ans, b/a)

    return ans[::-1], steps

def inverse_gauss_jordan(A, pivoting = True):
    row = len(A)
    A = A.copy()
    I = np.eye(row)

    for r in range(row):
        if pivoting :
            target_r = r + np.argmax(np.abs(A[r:,r]))
            if target_r != r:
                temp_m = A[target_r].copy()
                A[target_r] = A[r]
                A[r] = temp_m

                temp_i = I[target_r].copy()
                I[target_r] = I[r]
                I[r] = temp_i

        pivot = A[r,r]
        A[r] = A[r]/pivot
        I[r] = I[r]/pivot

        for i in range(row):
            if i != r :
                factor = A[i,r]
                A[i] = A[i] - factor*A[r]
                I[i] = I[i] - factor*I[r]
        
    return I
