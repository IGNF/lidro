# -*- coding: utf-8 -*-
""" read pointcloud and extracts points (X, Y, Z, classification) and crs"""
import laspy
import numpy as np


def read_pointcloud(las_file: str):
    """Reads a LAS pointcloud file and extracts point coordinates (X, Y, Z, classification)

    Args:
        las_file (str): Path to the LAS file

    Returns:
        input_point (np.ndarray) : Numpy array containing point coordinates and classification
        (X, Y, Z, classification)
        crs (dict): a pyproj CRS object
    """
    # Read pointcloud
    with laspy.open(las_file) as f:
        las = f.read()

    output_points = np.vstack((las.x, las.y, las.z, las.classification)).transpose()
    crs = las.header.parse_crs()

    return output_points, crs
