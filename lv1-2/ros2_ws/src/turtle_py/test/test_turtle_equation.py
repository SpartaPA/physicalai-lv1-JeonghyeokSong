import math
import pytest
from turtle_equation import distance, normalize_angle, reached


@pytest.mark.parametrize("dist, tol, expected", [
    (0.2, 0.3, True),    # 정상: 안쪽
    (0.3, 0.3, True),    # 경계: 딱 같을 때 (포함?)
    (0.31, 0.3, False),  # 정상: 바깥
])
def test_reached(dist, tol, expected):

    assert reached(dist, tol) == expected

def test_reached_negative_tol_raises():
    with pytest.raises(ValueError):
        reached(0.1, -1.0)

# --- distance ---
def test_distance():
    assert distance(0, 0, 3, 4) == pytest.approx(5.0) 
    assert distance(2, 2, 2, 2) == pytest.approx(0.0) 

# --- normalize_angle (직접 채우세요) ---
def test_normalize_angle():
    # TODO: π, -π, 3π/2→-π/2, 2π→0 등 경계 케이스
    assert normalize_angle(math.pi) == pytest.approx(math.pi)
    assert normalize_angle(-math.pi) == pytest.approx(-math.pi)
    assert normalize_angle(3*math.pi/2) == pytest.approx(-math.pi/2)
    assert normalize_angle(2*math.pi) == pytest.approx(0.0)
    assert normalize_angle(-3*math.pi/2) == pytest.approx(math.pi/2)