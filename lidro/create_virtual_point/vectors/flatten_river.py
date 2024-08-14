# -*- coding: utf-8 -*-
""" this function flattens the Z of the river
"""
import logging

import geopandas as gpd
import numpy as np

from lidro.create_virtual_point.vectors.intersect_points_by_line import (
    return_points_by_line,
)


def flatten_little_river(points: gpd.GeoDataFrame, line: gpd.GeoDataFrame):
    """This function flattens the Z of the little rivers, because of
        regression model doesn't work for these type of rivers.

    Args:
        points (gpd.GeoDataFrame): A GeoDataFrame containing points along Hydro's Skeleton
        line (gpd.GeoDataFrame): A GeoDataFrame containing each line from Hydro's Skeleton

    Returns:
        float: Z of the river
    """
    # Inputs
    gdf_points = return_points_by_line(points, line)

    # Extract points_knn and drop NaNs
    points_knn_values = gdf_points["points_knn"].dropna().values

    # Check if points_knn_values is empty
    if points_knn_values.size == 0:
        logging.warning("For little river : no valid points found, returning default Z quartile as 0")
        z_first_quartile = 0
        return z_first_quartile

    # Merge points and remove duplicates
    try:
        all_points_knn = np.vstack(points_knn_values)
    except ValueError as e:
        logging.error(f"Error during stacking points: {e}")
        z_first_quartile = 0
        return z_first_quartile

    unique_points_knn = np.unique(all_points_knn, axis=0)

    # Calculate the 1st quartile of all points
    first_quartile = np.percentile(unique_points_knn, 25, axis=0)
    z_first_quartile = first_quartile[-1]

    return z_first_quartile
