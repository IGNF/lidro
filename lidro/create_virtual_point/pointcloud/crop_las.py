# -*- coding: utf-8 -*-
""" Crop filtered pointcloud """
from typing import List

import numpy as np
import pdal
from shapely.geometry import MultiPolygon


def crop_pointcloud_by_points(input_points: str, geom: MultiPolygon, classes: List[int:int]) -> np.array:
    """Crop filtered pointcloud :
    1. Filter pointcloud for keeping only classe "GROUND"
    2. Crop filtered pointcloud by "Mask HYDRO + buffer"

    Args:
        input_points (str): Path to the input LAS/LAZ file
        geom (MultiPolygon):  An array of WKT or GeoJSON 2D MultiPolygon (Mask Hydro with buffer)
        classes (list): List of classes to use for the filtering

    Returns:
        np.array : Numpy array containing point coordinates (X, Y, Z) after filtering and croping
    """
    # Crop pointcloud by point
    pipeline = (
        pdal.Reader.las(filename=input_points, nosrs=True)
        | pdal.Filter.range(
            limits=f"Classification{classes}",
        )
        | pdal.Filter.crop(
            polygon=geom,
        )
    )
    pipeline.execute()
    # extract points
    cropped_points = pipeline.arrays[0]

    return np.array([cropped_points["X"], cropped_points["Y"], cropped_points["Z"]]).T
