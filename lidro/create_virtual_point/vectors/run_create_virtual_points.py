# -*- coding: utf-8 -*-
""" Run function "virtual points"
"""
import geopandas as gpd
import numpy as np
from scipy.interpolate import interp1d
from shapely.geometry import Point

from lidro.create_virtual_point.vectors.create_grid_2D_inside_maskhydro import (
    generate_grid_from_geojson,
)


def compute_virtual_points_by_section(
    line_gdf: gpd.GeoDataFrame,
    mask_hydro: gpd.GeoDataFrame,
    crs: str,
    spacing: float,
    # output_dir: str,
) -> gpd.GeoDataFrame:
    """This function generates a regular grid of 3D points spaced every N meters inside each hydro entity
    = virtual point

    Args:
        line_gdf (gpd.GeoDataFrame): A GeoDataFrame containing each line from Hydro's Skeleton 3D (rectify or not)
        mask_hydro (gpd.GeoDataFrame): A GeoDataFrame containing each mask hydro from Hydro's Skeleton
        crs (str): A pyproj CRS object used to create the output GeoJSON file
        spacing (float, optional): Spacing between the grid points in meters.
                                   The default value is 0.5 meter

    Returns:
        gpd.GeoDataFrame: All virtual points by Mask Hydro
    """
    # Generate grid 2D inside mask hydro
    grid_gdf = generate_grid_from_geojson(mask_hydro, spacing)

    # Extract the polyline from skeleton hydro (assuming there is only one geometry in line_gdf)
    skeleton_line = line_gdf.iloc[0].geometry
    # Extract points and their coordinates
    polyline_coords = [Point(coord) for coord in skeleton_line.coords]
    # Extract Z values from the 3D coordinates
    z_values = np.array([coord[2] for coord in skeleton_line.coords])  # assuming the polyline is in 3D

    # Compute cumulative distances along the polyline for interpolation
    cumulative_distances = [0] + [
        skeleton_line.project(Point(polyline_coords[i].x, polyline_coords[i].y))
        for i in range(1, len(polyline_coords))
    ]

    # Interpolation function for Z based on cumulative distances along the polyline
    z_interpolator = interp1d(cumulative_distances, z_values, kind="linear", fill_value="extrapolate")

    # Assign Z values to grid points by projecting each point onto the polyline
    z_values_for_grid = []
    for point in grid_gdf.geometry:
        # Project the 2D point onto the polyline to get the distance along the polyline
        distance_on_polyline = skeleton_line.project(point)
        # Interpolate the Z value at this distance
        z_value = z_interpolator(distance_on_polyline)
        z_values_for_grid.append(z_value)

    # Create a new GeoDataFrame with X, Y, and interpolated Z values as 3D points
    grid_with_z = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(grid_gdf.geometry.x, grid_gdf.geometry.y, z_values_for_grid), crs=grid_gdf.crs
    )

    return grid_with_z
