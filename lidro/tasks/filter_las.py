# -*- coding: utf-8 -*-
""" PDAL pipeline for filtering pointcloud """
import pdal
import numpy as np

def read_point_cloud(filename: str, classes: list, spatial_ref: str) :
    """ Reads a LAS pointcloud file, filter for keeping only ground,and extracts point coordinates (X, Y, Z)
    Parameters:
    - filename (str) : Path to the LAS file
    - classes (list): List of classes to use for the filtering
    - spatial_ref (str): spatial reference of the input LAS file

    Returns:
    - points (np.ndarray) : Numpy array containing point coordinates (X, Y, Z) .
    - metadata (dict) : Metadata extracted from the LAS file
    """
    # Read pointcloud
    if not isinstance(classes, list):
         raise TypeError("This function's parameter is not good caracter")
    elif not isinstance(spatial_ref, str):
         raise TypeError("This function's parameter is not good caracter")
    else:
        pipeline = pdal.Reader.las(filename=filename, override_srs=spatial_ref, nosrs=True)
        if classes: # filter by classes
                pipeline |= pdal.Filter.range(limits=",".join(f"Classification[{c}:{c}]" for c in classes))
        pipeline.execute()
        arrays = pipeline.arrays[0]
        points = np.vstack((arrays['X'], arrays['Y'], arrays['Z'])).T
        return points # returns coordinates points