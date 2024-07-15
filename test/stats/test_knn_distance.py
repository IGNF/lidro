import numpy as np

from lidro.create_virtual_point.stats.knn_distance import find_k_nearest_neighbors


def test_find_k_nearest_neighbors_default():
    points_array = np.array(
        [
            [830438.91, 6290854.32, 2.56],
            [830721.84, 6290447.79, 2.23],
            [830861.04, 6290242.06, 2.78],
            [830867.61, 6290202.62, 2.89],
        ]
    )
    point = np.array([[830574.89, 6290648.53]])
    k = 3

    result = find_k_nearest_neighbors(point, points_array, k)

    assert isinstance(result, np.ndarray) is True
    assert result.ndim == [
        [830438.91, 6290854.32, 2.56],
        [830721.84, 6290447.79, 2.23],
        [830861.04, 6290242.06, 2.78],
    ]
