# -*- coding: utf-8 -*-
""" Create mask non hydro from pointcloud filtering
"""
from typing import List, Tuple

import numpy as np
import scipy.ndimage

from lidro.create_mask_hydro.pointcloud.filter_las import filter_pointcloud
from lidro.create_mask_hydro.pointcloud.io import get_pointcloud_origin
from lidro.create_mask_hydro.pointcloud.read_las import read_pointcloud


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
    bins = bins > 0  # binarize map
    return bins


def detect_hydro_by_tile(filename: str, tile_size: int, pixel_size: float, classes: List[int], dilation_size: int):
    """ "Detect hydrographic surfaces in a tile from the classified points of the input pointcloud
    An hydrographic surface is define as a surface where there is no points from any class different from water

    Args:
        filename (str): input pointcloud
        tile_size (int): size of the raster grid (in meters)
        pixel_size (float): distance between each node of the raster grid (in meters)
        classes (List[int]): List of classes to use for the binarisation (points with other
                    classification values are ignored)
        dilatation_size (int): size for dilatation raster

    Returns:
        smoothed_water (np.array):  2D binary array (x, y) of the water presence from the point cloud
        pcd_origin (list): top left corner of the tile containing the point cloud
        (infered from pointcloud bounding box and input tile size)
    """
    # Read pointcloud, and extract coordinates (X, Y, Z, and classification) of all points
    array, crs = read_pointcloud(filename)

    # Extracts parameters for binarisation
    pcd_origin = get_pointcloud_origin(array, tile_size)

    # Filter pointcloud by classes: keep only points from selected classes that are not water
    array_filter = filter_pointcloud(array, classes)

    # create occupancy map (2D)
    occupancy = create_occupancy_map(array_filter, tile_size, pixel_size, pcd_origin)

    # Revert occupancy map to keep pixels where there is no point of the selected classes
    detected_water = np.logical_not(occupancy)

    # Apply a mathematical morphology operations: DILATATION
    # / ! \ NOT "CLOSING", due to the reduction in the size of hydro masks, particularly at the tile borders.
    # / ! \ WITH "CLOSING" => Masks Hydro are no longer continuous, when they are merged
    water_mask = scipy.ndimage.binary_dilation(detected_water, structure=np.ones((dilatation_size, dilatation_size))).astype(np.uint8)

    return morphology_bins, pcd_origin
