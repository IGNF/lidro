# -*- coding: utf-8 -*-
""" Calculates statistics from np.array (ex. pointcloud) """
import numpy as np


def calculate_quartile(points: np.array, q: int) -> float:
    """
    Calculates the quartile of the value (ex. altitude from z-coordinate) of points.

    Parameters:
        - points (numpy.ndarray): An array of 3D points [x, y, z]
        - q (int): Percentage or sequence of percentages for the percentiles to compute.
                   Values must be between 0 and 100 inclusive.


    Returns:
        - float: The quartile of the value (ex. z-coordinates).
    """
    altitudes = points[:, 2]  # Extract the altitude column
    n_quartile = round(np.percentile(altitudes, q), 2)

    return n_quartile


def calculate_median(points: np.array) -> float:
    """
    Calculates the median of the value (ex. altitude from z-coordinate) of points.

    Parameters:
        - points (numpy.ndarray): An array of 3D points [x, y, z]


    Returns:
        - float: The median of the value (ex. z-coordinates).
    """
    altitudes = points[:, 2]  # Extract the altitude column
    n_median = round(np.median(altitudes), 2)

    return n_median
