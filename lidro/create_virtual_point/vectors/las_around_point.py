# -*- coding: utf-8 -*-
""" Extract a list of N "ground" points closest to the N points of the hydro skeleton
"""
from typing import List

import numpy as np
from shapely.geometry import Point

from lidro.create_virtual_point.stats.knn_distance import find_k_nearest_neighbors


def filter_las_around_point(points_skeleton: List, points_clip: np.array, k: int) -> List:
    """Extract a list of N "ground" points closest to the N points of the hydro skeleton

    Args:
        points_skeleton (list) : points every N meters (by default: 2) along skeleton Hydro
        points_clip (np.array): Numpy array containing point coordinates (X, Y, Z) after filtering and croping
        k (int): The number of nearest neighbors to find

    Returns:
        List : Result {'geometry': Point 2D on skeleton, 'points_knn': List of LIDAR points from}
    """
    # Finds the K nearest neighbors of a given point from a list of 3D points
    points_knn_list = [
        ({"geometry": Point(point), "points_knn": find_k_nearest_neighbors(point, points_clip, k)})
        for point in points_skeleton
    ]

    return points_knn_list
