import numpy as np
import pytest

from lidro.create_virtual_point.stats.calculate_stat import (
    calculate_median,
    calculate_percentile,
)


def test_calculate_percentile_25():
    points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])
    assert calculate_percentile(points, 25) == 6.0


def test_calculate_percentile_50():
    points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])
    assert calculate_percentile(points, 50) == 9.0


def test_calculate_percentile_75():
    points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])
    assert calculate_percentile(points, 75) == 12.0


def test_calculate_percentile_100():
    points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])
    assert calculate_percentile(points, 100) == 15.0


def test_calculate_percentile_invalid_q():
    with pytest.raises(ValueError):
        points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])
        calculate_percentile(points, 110)


def test_calculate_percentile_negative_q():
    with pytest.raises(ValueError):
        points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])
        calculate_percentile(points, -10)


def test_calculate_median():
    points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])
    assert calculate_median(points) == 9.0
