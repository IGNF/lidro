import numpy as np

from lidro.create_virtual_point.stats.calculate_stat import (
    calculate_median,
    calculate_quartile,
)


def test_calculate_quartile_25():
    points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])
    assert calculate_quartile(points, 25) == 6.0


def test_calculate_quartile_50():
    points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])
    assert calculate_quartile(points, 50) == 9.0


def test_calculate_quartile_75():
    points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])
    assert calculate_quartile(points, 75) == 12.0


def test_calculate_quartile_100():
    points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])
    assert calculate_quartile(points, 100) == 15.0


def test_calculate_quartile_invalid_q():
    points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])
    try:
        calculate_quartile(points, 110)
    except ValueError:
        pass
    else:
        assert False, "ValueError non levée pour q=110"


def test_calculate_quartile_negative_q():
    points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])
    try:
        calculate_quartile(points, -10)
    except ValueError:
        pass
    else:
        assert False, "ValueError non levée pour q=-10"


def test_calculate_median():
    points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])
    assert calculate_median(points) == 9.0
