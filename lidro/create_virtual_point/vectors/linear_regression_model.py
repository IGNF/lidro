# -*- coding: utf-8 -*-
""" This function calculates a linear regression line
in order to read the Zs along the hydro skeleton to guarantee the flow
"""
import logging

import geopandas as gpd
import numpy as np
from shapely import line_locate_point

from lidro.create_virtual_point.vectors.intersect_points_by_line import (
    return_points_by_line,
)


def calculate_linear_regression_line(points: gpd.GeoDataFrame, line: gpd.GeoDataFrame, crs: str):
    """This function calculates a linear regression line in order to read the Zs
       along the hydro skeleton to guarantee the flow.
       A river is a natural watercourse whose slope is less than 1%, and
       the error tolerance specified in the specifications is 0.5 m.
       So, the linear regression model must have a step of 50 m.

    Args:
        points (gpd.GeoDataFrame): A GeoDataFrame containing points along Hydro's Skeleton
        line (gpd.GeoDataFrame): A GeoDataFrame containing each line from Hydro's Skeleton
        crs (str): a pyproj CRS object used to create the output GeoJSON file

    Returns:
        np.poly1d: Regression model
        numpy.array: Determination coefficient
    """
    if points.empty or line.empty:
        logging.warning("Input GeoDataFrames 'points' and 'line' must not be empty")
        return np.poly1d([0, 0]), 0.0

    # Retrieve points along the line
    gdf_points = return_points_by_line(points, line)

    if gdf_points.empty or len(gdf_points) < 3:
        logging.warning("Not enough points for regression analysis")
        return np.poly1d([0, 0]), 0.0

    # Combine all `points_knn` into a single list
    all_points_knn = []
    for knn_list in gdf_points["points_knn"]:
        all_points_knn.extend(knn_list)

    # Convert the list of points to a numpy array and remove duplicates
    all_points_knn_array = np.array(all_points_knn)
    unique_points_knn = np.unique(all_points_knn_array, axis=0)

    # Create final data structure
    final_data = {"geometry": [line.iloc[0]["geometry"]], "points_knn": unique_points_knn}

    # Generate projected coordinates
    points_gs = gpd.GeoSeries().from_xy(
        final_data["points_knn"][:, 0],  # X coordinates
        final_data["points_knn"][:, 1],  # Y coordinates
        final_data["points_knn"][:, 2],  # Z coordinates
        crs=crs,  # Coordinate reference system
    )

    # Locate each point along the polyline
    d_line = line_locate_point(final_data["geometry"], points_gs, normalized=False)

    # Create a GeoDataFrame for regression analysis
    regression_gpd = gpd.GeoDataFrame(geometry=points_gs)
    # This column contains the curvilinear abscissa
    regression_gpd["ac"] = d_line
    bins = np.arange(regression_gpd["ac"].max(), step=50)  # Create bins for curvilinear abscissa
    regression_gpd["ac_bin"] = np.digitize(regression_gpd["ac"], bins)  # Digitize curvilinear abscissa into bins
    # This column contains the Z value of the point
    regression_gpd["z"] = regression_gpd.geometry.z

    # Linear regression model using binned data
    temp = regression_gpd.groupby("ac_bin").aggregate(
        {
            "ac": "mean",  # Mean of curvilinear abscissa
            "z": [
                ("quantile", lambda x: x.quantile(0.1)),  # 10th percentile of Z values
                ("std", lambda x: x.quantile(0.75) - x.quantile(0.25)),
            ],  # Interquartile range of Z values
        }
    )
    # Linear regression with weights
    coeff, SSE, *_ = np.polyfit(temp["ac"]["mean"], temp["z"]["quantile"], deg=1, full=True)

    # Calculate SST (TOTAL SQUARE SUN)
    SST = np.sum((temp["z"]["quantile"] - np.mean(temp["z"]["quantile"])) ** 2)

    # Determination coefficient [0, 1]
    r2 = 1 - (SSE / SST)

    model = np.poly1d(coeff)

    return model, r2
