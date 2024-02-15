# -*- coding: utf-8 -*-
""" Filter pointcloud """
import numpy as np
import laspy 

def filter_pointcloud(filename: str, classes: list) :
    """ Reads a LAS pointcloud file, filter (parameters),and extracts point coordinates (X, Y, Z)
    Parameters:
    - filename (str) : Path to the LAS file
    - classes (list): List of classes to use for the filtering

    Returns:
    - points (np.ndarray) : Numpy array containing point coordinates (X, Y, Z)
    """
    if not isinstance(classes, list):
         raise TypeError("This function's parameter is not good caracter")
    else:
        # Read pointcloud
        LAS = laspy.read(filename)
        # Filter pointcloud by classe(s)
        filter_las = [i for i, c in enumerate(LAS.classification) if c in classes]

        points =  np.vstack((LAS.x[filter_las], LAS.y[filter_las], LAS.z[filter_las])).transpose()
        return points # returns coordinates points

