# -*- coding: utf-8 -*-
""" read pointcloud """
import laspy
import numpy as np

def read_pointcloud(filename: str) :
    """ Reads a LAS pointcloud file and extracts point coordinates (X, Y, Z)
    Parameters:
    - filename (str) : Path to the LAS file

    Returns:
    - input_points (np.ndarray) : Numpy array containing point coordinates (X, Y, Z)
    """
    # Read pointcloud
    LAS = laspy.read(filename)
    input_points = np.vstack((LAS.x, LAS.y, LAS.z)).transpose()

    return input_points