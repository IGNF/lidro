# -*- coding: utf-8 -*-
""" Extract a Z elevation value every N meters along the hydrographic skeleton
"""
from typing import List

import numpy as np
from shapely.geometry import Point

from lidro.create_virtual_point.stats.calculate_stat import calculate_quartile
from lidro.create_virtual_point.stats.knn_distance import find_k_nearest_neighbors


def filter_las_around_point(points_skeleton: List, points_clip: np.array, k: int) -> List:
    """Extract a Z elevation value every N meters along the hydrographic skeleton

    Args:
        points_skeleton (list) : points every N meters (by default: 2) along skeleton Hydro
        points_clip (np.array): Numpy array containing point coordinates (X, Y, Z) after filtering and croping
        k (int): The number of nearest neighbors to find

    Returns:
        List : Result {'geometry': Point 3D, 'z_q1': points KNN}
    """
    # Finds the K nearest neighbors of a given point from a list of 3D points
    points_knn_list = [
        ({"geometry": Point(point), "points_knn": find_k_nearest_neighbors(point, points_clip, k)})
        for point in points_skeleton
    ]

    # Calcule Z "Q1" for each points every N meters along skeleton hydro
    results = [
        ({"geometry": p["geometry"], "z_q1": calculate_quartile(p["points_knn"], 10)})
        for p in points_knn_list
        if not np.all(np.isnan(p["points_knn"]))
    ]

    return results
