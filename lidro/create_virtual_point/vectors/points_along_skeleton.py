# -*- coding: utf-8 -*-
""" Create severals points every 2 meters (by default) along skeleton Hydro
"""
import os

import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import linemerge


def generate_points_along_skeleton(
    input_folder: str, input_file: str, distance_meters: 2, crs: tuple
) -> gpd.GeoDataFrame:
    """Create several points every 2 meters (by default) along skeleton Hydro

    Args:
        input_folder (str): folder which contains Skeleton Hydro (1 file ".GeoJSON")
        input_file (str): input filename from Skeleton Hydro
        distance_meters (float): distance in meters between 2 consecutive points (default: 2 meters)
        crs (tuple): a pyproj CRS object used to create the output GeoJSON file

    Returns:
        gpd.GeoDataFrame: Points every 2 meters (by default) along skeleton hydro
    """
    # Read the input file
    lines_gdf = gpd.read_file(os.path.join(input_folder, input_file), crs=crs)

    # Segmentize geometry
    lines_merged = linemerge(lines_gdf.unary_union, directed=True)

    # Create severals points every "distance meters" along skeleton's line
    points = [
        Point(lines_merged.interpolate(distance)) for distance in range(1, int(lines_merged.length), distance_meters)
    ]
    points_gdf = gpd.GeoDataFrame(geometry=points).explode(ignore_index=True)

    return points_gdf
