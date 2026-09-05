import numpy as np
import pytest

from src.rotation import rot_x, rot_y, rot_z
from src.transform import (inv_T, inv_T_batch, least_squares_normal_equation, make_T, rmse,
                           to_homogeneous, transform_direction, transform_point,
                           transform_points)
from src.vectors import det

rng = np.random.default_rng(0)

ANGLES = [0.0, 0.3, 0.7, np.pi / 4, np.pi / 2, np.pi, -1.2]


def make_random_T(seed):
    r = np.random.default_rng(seed)
    R = rot_z(r.uniform(-np.pi, np.pi)) @ rot_y(r.uniform(-np.pi, np.pi)) @ rot_x(r.uniform(-np.pi, np.pi))
    return make_T(R, r.standard_normal(3))


TRANSFORMS = [make_random_T(s) for s in range(20)]


@pytest.mark.parametrize("T", TRANSFORMS)
def test_inv_T_is_inverse(T):
    assert np.allclose(T @ inv_T(T), np.eye(4))
    assert np.allclose(inv_T(T) @ T, np.eye(4))


@pytest.mark.parametrize("T", TRANSFORMS)
def test_inv_T_equals_general_inverse(T):
    assert np.allclose(inv_T(T), np.linalg.inv(T))


@pytest.mark.parametrize("T", TRANSFORMS)
def test_inv_T_formula(T):
    R = T[:3, :3]
    t = T[:3, 3]
    Ti = inv_T(T)
    assert np.allclose(Ti[:3, :3], R.T)
    assert np.allclose(Ti[:3, 3], -R.T @ t)
    assert np.allclose(Ti[3], [0, 0, 0, 1])


@pytest.mark.parametrize("theta", ANGLES)
def test_make_T_structure(theta):
    R = rot_z(theta)
    t = np.array([1.0, -2.0, 3.0])
    T = make_T(R, t)
    assert np.allclose(T[:3, :3], R)
    assert np.allclose(T[:3, 3], t)
    assert np.allclose(T[3], [0, 0, 0, 1])
    assert np.isclose(det(T[:3, :3]), 1.0)


@pytest.mark.parametrize("T", TRANSFORMS)
def test_point_vs_direction(T):
    R = T[:3, :3]
    t = T[:3, 3]
    v = np.array([1.0, 2.0, -0.5])
    p_out = transform_point(T, v)
    d_out = transform_direction(T, v)
    assert np.allclose(p_out, R @ v + t)
    assert np.allclose(d_out, R @ v)
    assert np.allclose(p_out - d_out, t)
    assert np.isclose(np.linalg.norm(d_out), np.linalg.norm(v))


def test_to_homogeneous_w():
    v = [1.0, 0.0, 0.0]
    assert np.allclose(to_homogeneous(v, 1.0), [1, 0, 0, 1])
    assert np.allclose(to_homogeneous(v, 0.0), [1, 0, 0, 0])


@pytest.mark.parametrize("T", TRANSFORMS[:5])
def test_transform_points_matches_loop(T):
    P = rng.standard_normal((30, 3))
    batch = transform_points(T, P)
    loop = np.array([transform_point(T, p) for p in P])
    assert batch.shape == P.shape
    assert np.allclose(batch, loop)


def test_inv_T_batch_matches_single():
    Ts = np.stack([make_random_T(s) for s in range(50)])
    out = inv_T_batch(Ts)
    assert out.shape == Ts.shape
    assert np.allclose(out, np.linalg.inv(Ts))
    assert np.allclose(out, np.array([inv_T(t_) for t_ in Ts]))


def test_least_squares_matches_lstsq():
    A = rng.standard_normal((60, 6))
    x_true = rng.standard_normal(6)
    b = A @ x_true + 1e-3 * rng.standard_normal(60)
    x_hat, r = least_squares_normal_equation(A, b)
    x_ref = np.linalg.lstsq(A, b, rcond=None)[0]
    assert np.allclose(x_hat, x_ref)
    assert np.allclose(r, b - A @ x_hat)
    assert np.allclose(A.T @ r, 0.0, atol=1e-8)


def test_rmse():
    r = np.array([3.0, 4.0])
    assert np.isclose(rmse(r), np.sqrt((9 + 16) / 2))
