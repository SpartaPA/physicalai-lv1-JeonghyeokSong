import numpy as np
import pytest

from src.rotation import gram_schmidt, rot_x, rot_y, rot_z
from src.vectors  import det

ANGLES = [0.0, 0.3, 0.7, np.pi / 4, np.pi / 2, np.pi, -1.2]
ROTATION_MATRICES = [f(a) for f in (rot_x, rot_y, rot_z) for a in ANGLES]

@pytest.mark.parametrize("M", ROTATION_MATRICES)
def test_columns_are_orthonormal(M) -> bool:
    row = len(M)
    assert np.allclose(M.T@M, np.eye(row))

@pytest.mark.parametrize("M", ROTATION_MATRICES)
def test_determinant_is_one(M, eps = 1e-12) -> bool:
    assert np.abs(1-det(M) ) < eps

@pytest.mark.parametrize("M", ROTATION_MATRICES)
def test_inverse_equals_transpose(M):
    assert np.allclose (M.T, np.linalg.inv(M))

@pytest.mark.parametrize("M", ROTATION_MATRICES)
def test_gram_schmidt_restores_orthogonality(M):
    R = gram_schmidt(M)
    row = len(R)
    assert np.allclose(R.T@R, np.eye(row))
