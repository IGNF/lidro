# -*- coding: utf-8 -*-
""" this function flattens the Z of the river
"""
import geopandas as gpd
import numpy as np

from lidro.create_virtual_point.vectors.intersect_points_by_line import (
    return_points_by_line,
)


def flatten_little_river(points: gpd.GeoDataFrame, line: gpd.GeoDataFrame, crs: str):
    """This function flattens the Z of the little rivers, because of
        regression model doesn't work for these type of rivers.

    Args:
        points (gpd.GeoDataFrame): A GeoDataFrame containing points along Hydro's Skeleton
        line (gpd.GeoDataFrame): A GeoDataFrame containing each line from Hydro's Skeleton
        crs (str): a pyproj CRS object used to create the output GeoJSON file

    Returns:
        float: Z of the river
    """
    # Inputs
    gdf_points = return_points_by_line(points, line)

    # Merge points and remove duplicates
    all_points_knn = np.vstack(gdf_points["points_knn"].values)
    unique_points_knn = np.unique(all_points_knn, axis=0)

    # Calculate the 1st quartile of all points
    first_quartile = np.percentile(unique_points_knn, 25, axis=0)
    z_first_quartile = first_quartile[-1]

    return z_first_quartile
