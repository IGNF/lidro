# -*- coding: utf-8 -*-
""" KNN """
import numpy as np
from sklearn.neighbors import NearestNeighbors


def find_k_nearest_neighbors(points_skeleton: np.array, points_ground_3d: np.array, k: int) -> np.array:
    """Finds the K nearest neighbors of a given point from a list of 3D points

    Args:
        points_skeleton (np.array): a single point representing the skeleton Hydro
                                    an array of 2D point [x, y]
        points_ground_3d (np.array): ground's points from LIDAR.
                                    an array of 3D points [x, y, z]
        k (int): the number of nearest neighbors to find

    Returns:
        numpy.ndarray: an array of the K nearest 3D points [x, y, z]
    """
    # Extract 2D coordinates (x, y) from the 3D points
    points_ground_2d = points_ground_3d[:, :2]

    # Convert point_2d to nump.array
    points_skeleton_array = np.array(points_skeleton).reshape(1, -1)

    # Initialize and fit the NearestNeighbors model
    nbrs = NearestNeighbors(n_neighbors=k, algorithm="auto").fit(points_ground_2d)

    # Find the distances and indices of the nearest neighbors
    indices = nbrs.kneighbors(points_skeleton_array, return_distance=False)

    # Retrieve the points corresponding to the indices
    # Use indices  to retrieve the closest 3D points
    k_nearest_points = points_ground_3d[indices[0]]
    # = points_3d[indices.flatten()]

    return k_nearest_points
