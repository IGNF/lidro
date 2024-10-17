# -*- coding: utf-8 -*-
""" Apply Z from grid
"""
import geopandas as gpd
from shapely import line_locate_point


def calculate_grid_z_with_model(points: gpd.GeoDataFrame, line: gpd.GeoDataFrame, model) -> gpd.GeoDataFrame:
    """Calculate Z with regression model.
    If points are not on the line, these points will be projected on this line

    Args:
        points (gpd.GeoDataFrame): A GeoDataFrame containing the grid points
        line (gpd.GeoDataFrame): A GeoDataFrame containing each line from Hydro's Skeleton
        model (dict): A dictionary representing the regression model

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame of initial points, but with a Z.
    """
    # Calculate curvilinear abscises for all points of the grid
    curvilinear_abs = line_locate_point(line.loc[0, "geometry"], points["geometry"].array, normalized=False)
    # line_points = line.copy()
    if len(line.index) > 1:
        print(line["geometry"])
        raise ValueError("Line is not with a single line", line)

    # Prediction of Z values using the regression model
    # Its possible to use non-linear models for prediction
    predicted_z = model(curvilinear_abs)

    # Generate a new geodataframe, with 3D points
    grid_with_z = calculate_grid_z(points, predicted_z)

    return grid_with_z


def calculate_grid_z(points: gpd.GeoDataFrame, predicted_z: float) -> gpd.GeoDataFrame:
    """Calculate Z grid

    Args:
        points (gpd.GeoDataFrame): A GeoDataFrame containing the grid points
        predicted_z (float): predicted Z for river

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame of initial points, but with a Z.
    """
    # Generate a new geodataframe, with 3D points
    grid_with_z = gpd.GeoDataFrame(
        geometry=gpd.GeoSeries().from_xy(points.geometry.x, points.geometry.y, predicted_z), crs=points.crs
    )

    return grid_with_z
