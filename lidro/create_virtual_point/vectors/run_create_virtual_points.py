# -*- coding: utf-8 -*-
""" Run function "virtual points"
"""
import geopandas as gpd
import numpy as np

from lidro.create_virtual_point.vectors.apply_Z_from_grid import (
    calculate_grid_z_for_flattening,
    calculate_grid_z_with_model,
)
from lidro.create_virtual_point.vectors.create_grid_2D_inside_maskhydro import (
    generate_grid_from_geojson,
)
from lidro.create_virtual_point.vectors.flatten_river import flatten_little_river
from lidro.create_virtual_point.vectors.linear_regression_model import (
    calculate_linear_regression_line,
)


def lauch_virtual_points_by_section(
    points: gpd.GeoDataFrame, line: gpd.GeoDataFrame, mask_hydro: gpd.GeoDataFrame, crs: str, spacing: float
) -> gpd.GeoDataFrame:
    """This function generates a regular grid of 3D points spaced every N meters inside each hydro entity
    = virtual point

    Args:
        points (gpd.GeoDataFrame): A GeoDataFrame containing points along Hydro's Skeleton
        line (gpd.GeoDataFrame): A GeoDataFrame containing each line from Hydro's Skeleton
        mask_hydro (gpd.GeoDataFrame): A GeoDataFrame containing each mask hydro from Hydro's Skeleton
        crs (str): a pyproj CRS object used to create the output GeoJSON file
        spacing (float, optional): Spacing between the grid points in meters. The default value is 1 meter.

    Returns:
        gpd.GeoDataFrame: virtual points by Mask Hydro
    """
    # Step 1: Generates a regular 2D grid of evenly spaced points within a Mask Hydro
    gdf_grid = generate_grid_from_geojson(mask_hydro, spacing)
    # Calculate the length of the river
    river_length = float(line.length.iloc[0])

    # Step 2 : Model linear regression for river's lenght > 150 m
    # Otherwise flattening the river
    # Apply the algo according to the length of the river
    if river_length > 150:
        model, r2 = calculate_linear_regression_line(points, line, crs)
        gdf_grid_with_z = calculate_grid_z_with_model(gdf_grid, line, model)

    else:
        predicted_z = flatten_little_river(points, line, crs)
        if np.isnan(predicted_z) or predicted_z is None:
            gdf_grid_with_z = calculate_grid_z_for_flattening(gdf_grid, line, 0)
        else:
            gdf_grid_with_z = calculate_grid_z_for_flattening(gdf_grid, line, predicted_z)

    return gdf_grid_with_z
