# -*- coding: utf-8 -*-
""" Create mask non hydro from pointcloud filtering
"""
from typing import Tuple, List
import numpy as np
import scipy.ndimage

from lidro.pointcloud.read_las import read_pointcloud
from lidro.pointcloud.filter_las import filter_pointcloud
from lidro.utils.get_pointcloud_origin import get_pointcloud_origin


def create_mask(
    filename: str,
    pixel_size: float,
    nb_pixels: Tuple[int, int] = (1000, 1000),
    classes: List[int] = [0, 1, 2, 3, 4, 5, 6, 17, 66 ]
    ):
    """Create 2d binary occupancy map from points coordinates:
    boolean 2d map with 1 where at least one point falls in the pixel, 0 everywhere else.

    Args:
        filename(str): input pointcloud
        pixel_size (float): pixel size (in meters) of the output map
        nb_pixels (float, optional): number of pixels on each axis in format (x, y). Defaults to (1000, 1000).

    Returns:
        np.array: Boolean output map
    """
    # Read pointcloud, and extract vector of X / Y coordinates of all points 
    points = read_pointcloud(filename) 
    # Extract spatial coordinate of the upper-left corner of the raster (center of the upper-left pixel)
    x_min, y_max = get_pointcloud_origin(points)

    # Filter pointcloud by classes [0, 1, 2, 3, 4, 5, 6, 17, 66 ] 
    points_filter = filter_pointcloud(filename, classes) 
    x = points_filter[:, 0]
    y = points_filter[:, 1]

    # numpy array is filled with (y, x) instead of (x, y)
    grid = np.zeros((nb_pixels[1], nb_pixels[0]), dtype=bool)

    for x, y in zip(x, y):
        grid_x = min(int((x - (x_min - pixel_size / 2)) / pixel_size), nb_pixels[0] - 1)  # x_min is left pixel center
        grid_y = min(int(((y_max + pixel_size / 2) - y) / pixel_size), nb_pixels[1] - 1)  # y_max is upper pixel center
        grid[grid_y, grid_x] = True
    
    # Apply a mathematical morphology operations: clonsg (dilation + erosion)
    output = scipy.ndimage.binary_closing(grid)

    return output

