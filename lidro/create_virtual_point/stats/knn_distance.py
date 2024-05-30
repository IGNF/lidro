# -*- coding: utf-8 -*-
""" KNN """
import numpy as np
from shapely.geometry import Point
from sklearn.neighbors import NearestNeighbors


def point_to_numpy(point: Point) -> np.array:
    """Converts a 3D shapely.geometry Point to a numpy array

    Args:
        point (shapely.geometry.Point): A 3D point with x, and y coordinates

    Returns:
        numpy.ndarray: An array of the K nearest 3D point [x, y, z].
                       By default [z] is '0' meters
    """
    return np.array([point.x, point.y, 0])


def find_k_nearest_neighbors(point: Point, points_array: np.array, k: int) -> np.array:
    """Finds the K nearest neighbors of a given point from a list of 3D points

    Args:
        point (Point): The reference 2D point
        points_array (np.array): An array of 3D points [x, y, z]
        k (int): The number of nearest neighbors to find

    Returns:
        numpy.ndarray: An array of the K nearest 3D points [x, y, z]
    """
    # Convert the point to a numpy array
    point_coords = point_to_numpy(point).reshape(1, -1)

    # Initialize and fit the NearestNeighbors model
    nbrs = NearestNeighbors(n_neighbors=k).fit(points_array)

    # Find the distances and indices of the nearest neighbors
    distances, indices = nbrs.kneighbors(point_coords)

    # Retrieve the points corresponding to the indices
    k_nearest_points = points_array[indices[0]]

    return k_nearest_points
