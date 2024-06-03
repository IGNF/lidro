# -*- coding: utf-8 -*-
""" KNN """
import numpy as np
from sklearn.neighbors import NearestNeighbors


def find_k_nearest_neighbors(point_2d: np.array, points_3d: np.array, k: int) -> np.array:
    """Finds the K nearest neighbors of a given point from a list of 3D points

    Args:
        point_2d (np.array): An array of 3D point [x, y, 0]
        points_3D (np.array): An array of 3D points [x, y, z]
        k (int): The number of nearest neighbors to find

    Returns:
        numpy.ndarray: An array of the K nearest 3D points [x, y, z]
    """
    # Convert point_2d to nump.arrat
    point_2d_array = np.array(point_2d).reshape(1, -1)

    # Initialize and fit the NearestNeighbors model
    nbrs = NearestNeighbors(n_neighbors=k, algorithm="auto").fit(points_3d)

    # Find the distances and indices of the nearest neighbors
    indices = nbrs.kneighbors(point_2d_array, return_distance=False)

    # Retrieve the points corresponding to the indices
    # Use indices  to retrieve the closest 3D points
    k_nearest_points = points_3d[indices[0]]
    # = points_3d[indices.flatten()]

    return k_nearest_points
