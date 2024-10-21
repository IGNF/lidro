# -*- coding: utf-8 -*-
""" Run function "update skeleton with Z"
"""
import logging

import geopandas as gpd
import numpy as np
from shapely import line_locate_point
from shapely.geometry import LineString, Point


def skeleton_3d_with_linear_regression(line: gpd.GeoDataFrame, model: np.poly1d, crs: str) -> gpd.GeoDataFrame:
    """
    This function updates the 2D hydro skeleton 'line' by adding a 3D 'Z' value
    based on a previously calculated linear regression model, and saves the updated
    skeleton to a GeoJSON file.

    Args:
        line (gpd.GeoDataFrame): A GeoDataFrame containing each 2D line from Hydro's Skeleton.
        model (np.poly1d): The linear regression model to calculate Z values.
        crs (str): The coordinate reference system of the line.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame of the updated 3D skeleton with Z values.
    """
    # For each line in the GeoDataFrame, extract points and calculate Z values
    updated_geometries = []
    z_mean_values = []  # List to store Z mean values for each geometry

    for i, geom in line.iterrows():
        line_geom = geom["geometry"]

        # If the line is not a LineString, skip it
        if line_geom.geom_type != "LineString":
            logging.warning(f"Geometry at index {i} is not a LineString")
            continue

        # Extract points (2D)
        coords_2d = np.array(line_geom.coords)

        # Calculate the curvilinear abscissa for each point using line_locate_point
        abscissas = abscissas = np.array([line_locate_point(line_geom, Point(x, y)) for x, y in coords_2d])

        # Predict Z values using the regression model
        z_values = model(abscissas)

        # Calculate the mean Z value and store it
        z_mean = np.mean(z_values)
        z_mean_values.append(z_mean)

        # Update each coordinate with the Z value
        coords_3d = [(x, y, z) for (x, y), z in zip(coords_2d, z_values)]

        # Create a new LineString with 3D coordinates
        updated_geom = LineString(coords_3d)
        updated_geometries.append(updated_geom)

    # Create a new GeoDataFrame for the updated lines
    updated_line = gpd.GeoDataFrame(geometry=updated_geometries, crs=crs)

    # Add the Z mean values as a new column
    updated_line["z_mean"] = z_mean_values

    return updated_line


def skeleton_3d_with_flatten(line: gpd.GeoDataFrame, z_value: float, crs: str) -> gpd.GeoDataFrame:
    """
    This function updates the 2D hydro skeleton 'line' by adding a 3D 'Z' value
    based on a previously calculated flatten model, and saves the updated
    skeleton to a GeoJSON file.

    Args:
        line (gpd.GeoDataFrame): A GeoDataFrame containing each 2D line from Hydro's Skeleton.
        z_value (float) : Z of the river
        crs (str): The coordinate reference system of the line.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame of the updated 3D skeleton with Z values.
    """
    # For each line in the GeoDataFrame, extract points and calculate Z values
    updated_geometries = []
    for i, geom in line.iterrows():
        line_geom = geom["geometry"]

        # If the line is not a LineString, skip it
        if line_geom.geom_type != "LineString":
            logging.warning(f"Geometry at index {i} is not a LineString")
            continue

        # Extract points (2D)
        coords_2d = np.array(line_geom.coords)

        # Update each coordinate with the Z value
        coords_3d = [(x, y, z) for (x, y), z in zip(coords_2d, z_value)]

        # Create a new LineString with 3D coordinates
        updated_geom = LineString(coords_3d)
        updated_geometries.append(updated_geom)

    # Create a new GeoDataFrame for the updated lines
    updated_line = gpd.GeoDataFrame(geometry=updated_geometries, crs=crs)

    # Add the Z mean values as a new column
    updated_line["z_mean"] = z_value

    return updated_line
