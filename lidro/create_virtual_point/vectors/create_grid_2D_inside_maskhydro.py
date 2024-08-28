# -*- coding: utf-8 -*-
""" Create a regula 2D grid
"""
import geopandas as gpd
import numpy as np
import shapely.vectorized


def generate_grid_from_geojson(mask_hydro: gpd.GeoDataFrame, spacing=0.5, margin=0):
    """
    Generates a regular 2D grid of evenly spaced points within a polygon defined
    in a GeoJSON file.

    Args:
        mask_hydro (gpd.GeoDataFrame): A GeoDataFrame containing each mask hydro from Hydro's Skeleton
        spacing (float, optional): Spacing between the grid points in meters. The default value is 0.5 meter.
        margin (int, optional): Margin around mask for grid creation. The default value is 0 meter.

    Returns:
        geopandas.GeoDataFrame: A GeoDataFrame containing the grid points within the polygon.
    """
    # Extract the polygon
    polygon = mask_hydro.geometry.unary_union  # Combine all polygons into a single shape if there are multiple

    if margin:
        polygon = polygon.buffer(margin)

    # Get the bounds of the polygon
    minx, miny, maxx, maxy = polygon.bounds

    # Generate the grid points
    x_points = np.arange(minx, maxx, spacing)
    y_points = np.arange(miny, maxy, spacing)
    grid_points = np.meshgrid(x_points, y_points)

    # Filter points that are within the polygon
    grid_points_in_polygon = shapely.vectorized.contains(polygon, *grid_points)

    filtred_x = grid_points[0][grid_points_in_polygon]
    filtred_y = grid_points[1][grid_points_in_polygon]

    # Convert to GeoDataFrame
    points_gs = gpd.points_from_xy(filtred_x, filtred_y)
    grid_gdf = gpd.GeoDataFrame(geometry=points_gs, crs=mask_hydro.crs)

    return grid_gdf
