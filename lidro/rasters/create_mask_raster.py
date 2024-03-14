# -*- coding: utf-8 -*-
""" Create mask non hydro from pointcloud filtering
"""
from typing import List, Tuple

import numpy as np
import scipy.ndimage

from lidro.pointcloud.filter_las import filter_pointcloud
from lidro.pointcloud.io import get_pointcloud_origin
from lidro.pointcloud.read_las import read_pointcloud


def create_occupancy_map(points: np.array, tile_size: int, pixel_size: float, origin: Tuple[int, int]):
    """Create a binary image to extract water surfaces

    Args:
        points (np.array): array from pointcloud
        tile_size (int): size of the raster grid (in meters)
        pixel_size (float): distance between each node of the raster grid (in meters)
        origin (Tuple[int, int]): Coordinates of the top left corner of the top-left pixel

    Returns:
        bins (np.array): 2D binary array (x, y) with 1 for if there is at least one point of the input cloud
        in the corresponding pixel, 0 otherwise
    """
    # Compute number of points per bin
    bins_x = np.arange(origin[0], origin[0] + tile_size + pixel_size, pixel_size)
    bins_y = np.arange(origin[1] - tile_size, origin[1] + pixel_size, pixel_size)
    _bins, _, _ = np.histogram2d(points[:, 1], points[:, 0], bins=[bins_y, bins_x])
    bins = np.flipud(_bins)
    bins = np.where(bins > 0, 0, 1)

    return bins


def detect_hydro_by_tile(filename: str, tile_size: int, pixel_size: float, classes: List[int]):
    """ "Detect hydrographic surfaces in a tile from the classified points of the input pointcloud

    Args:
        filename (str): input pointcloud
        tile_size (int): size of the raster grid (in meters)
        pixel_size (float): distance between each node of the raster grid (in meters)
        classes (List[int]): List of classes to use for the binarisation (points with other
                    classification values are ignored)

    Returns:
        bins (np.array):  2D binary array (x, y) of the water presence from the point cloud
        pcd_origin (list): top left corner of the tile containing the point cloud
        (infered from pointcloud bounding box and input tile size)
    """
    # Read pointcloud, and extract coordinates (X, Y, Z, and classification) of all points
    array, crs = read_pointcloud(filename)

    # Extracts parameters for binarisation
    pcd_origin = get_pointcloud_origin(array, tile_size)

    # Filter pointcloud by classes
    array_filter = filter_pointcloud(array, classes)

    # create occupancy map (2D)
    _bins = create_occupancy_map(array_filter, tile_size, pixel_size, pcd_origin)

    # Apply a mathematical morphology operations: clonsing
    closing_bins = scipy.ndimage.binary_closing(_bins, structure=np.ones((5, 5))).astype(np.uint8)

    return closing_bins, pcd_origin
