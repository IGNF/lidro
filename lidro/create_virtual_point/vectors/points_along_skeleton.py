# -*- coding: utf-8 -*-
""" Create several points every 2 meters (by default) along skeleton Hydro
"""
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import linemerge


def generate_points_along_skeleton(input_file: str, distance_meters: 2, crs: str | int) -> gpd.GeoDataFrame:
    """Create several points every 2 meters (by default) along skeleton Hydro

    Args:
        input_file (str): Path from Skeleton Hydro
        distance_meters (float): distance in meters between 2 consecutive points (default: 2 meters)
        crs (str | int): Make a CRS from an EPSG code : CRS WKT string

    Returns:
        gpd.GeoDataFrame: Points every 2 meters (by default) along skeleton hydro
    """
    # Read the input file
    lines_gdf = gpd.read_file(input_file, crs=crs)

    # Segmentize geometry
    lines_merged = linemerge(lines_gdf.unary_union, directed=False)

    # Create severals points every "distance meters" along skeleton's line
    list_points = [
        Point(lines_merged.interpolate(distance, normalized=False))
        for distance in range(0, int(lines_merged.length), distance_meters)
    ]

    points_gdf = gpd.GeoDataFrame(geometry=list_points, crs=crs).explode(ignore_index=True)

    return points_gdf
