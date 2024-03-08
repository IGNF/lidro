# -*- coding: utf-8 -*-
""" Filter pointcloud """
import numpy as np

def filter_pointcloud(input_points: np.array, classes: list) :
    """Filter pointcloud and extracts point coordinates (X, Y, Z)

    Args:
        input_points (np.array): Numpy array containing point coordinates (X, Y, Z, classification)
        classes (list): List of classes to use for the filtering

    Returns:
        filtered_points (np.ndarray) : Numpy array containing point coordinates (X, Y, Z) filtering
    """        
    # Filter pointcloud by classe(s)
    points_mask = np.isin(input_points[:, -1], classes)  
    filtered_points = input_points[points_mask, :]

    return filtered_points # returns coordinates points filtering 

