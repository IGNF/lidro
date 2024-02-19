# -*- coding: utf-8 -*-
""" Create mask non hydro from pointcloud filtering
"""
from typing import Tuple, List
import numpy as np
import scipy.ndimage

from lidro.pointcloud.read_las import read_pointcloud
from lidro.pointcloud.filter_las import filter_pointcloud
from lidro.utils.get_pointcloud_origin import get_pointcloud_origin



def binarisation(points: np.array, tile_size: int, pixel_size: float, origin: Tuple[int, int]):
    """ Binarisation
            
    Args:
        - points (np.array): array from pointcloud
        - tile_size (int): tile of the raster grid (in meters)
                - pixel_size (float): distance between each node of the raster grid (in meters)
        - origin (Tuple[int, int]): spatial coordinate of the upper-left corner of the raster
                    (center of the upper-left pixel)

    Returns:
        - bins (np.array): bins
    """
    # Compute number of points per bin
    bins_x = np.arange(origin[0], origin[0] + tile_size + pixel_size, pixel_size)
    bins_y = np.arange(origin[1] - tile_size, origin[1] + pixel_size, pixel_size)
    _bins, _, _ = np.histogram2d(points[:, 1], points[:, 0], bins=[bins_y, bins_x])
    bins = np.flipud(_bins)
    bins = np.where(bins > 0, 0, 1)
            
    return bins
        

def morphology_math_closing(input):
    """ Apply a mathematical morphology operations: closing (dilation + erosion)

    Args:
        - input(np.array): bins array
            
    Returns:
        - output(np.array): bins array with closing
    """
    output = scipy.ndimage.binary_closing(input, structure=np.ones((5,5))).astype(np.uint8)

    return output


def detect_hydro_by_tile(filename: str, tile_size: int, pixel_size: float, classes: List[int]):
    """Detect hydrographic surfaces by LIDAR tile

    Args:
        - filename(str): input pointcloud
        - tile_size (int): tile of the raster grid (in meters)
        - pixel_size (float): distance between each node of the raster grid (in meters)
        - classes (List[int]): List of classes to use for the binarisation (points with other
                    classification values are ignored).

    Returns:
        - bins (np.array): array from pointcloud
    """
    # Read pointcloud, and extract coordinates (X, Y, Z, and classification) of all points 
    array, crs = read_pointcloud(filename) 

    # Extracts parameters for binarisation
    pcd_origin_x, pcd_origin_y = get_pointcloud_origin(array, tile_size)
    pcd_origin = (pcd_origin_x, pcd_origin_y)

    # Filter pointcloud by classes : [0, 1, 2, 3, 4, 5, 6, 17, 66 ] 
    array_filter = filter_pointcloud(array, classes) 

    # Binarisation
    _bins = binarisation(array_filter, tile_size, pixel_size, pcd_origin)

    # Apply a mathematical morphology operations: clonsing 
    closing_bins = morphology_math_closing(_bins)

    return closing_bins

