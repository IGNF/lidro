# -*- coding: utf-8 -*-
""" Identifies all points that intersect each line
"""
import geopandas as gpd
from shapely.geometry import CAP_STYLE


def return_points_by_line(points: gpd.GeoDataFrame, line: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """This function identifies all points that intersect each Skeleton by hydro's section

    Args:
        points (gpd.GeoDataFrame): A GeoDataFrame containing points along Hydro's Skeleton
        line (gpd.GeoDataFrame): A GeoDataFrame containing each line from Hydro's Skeleton

    Returns:
        gpd.GeoDataFrame: A GeoDataframe containing only points that intersect each hydro's section
    """
    # Apply buffer (0.1 meters) from Mask Hydro
    line_buffer = line.buffer(0.1, cap_style=CAP_STYLE.square)
    gdf_line_buffer = gpd.GeoDataFrame(geometry=line_buffer)

    # Perform spatial join to find intersections
    pts_intersect = gpd.sjoin(points, gdf_line_buffer, how="left", predicate="intersects")

    # Filter out rows where 'index_right' is NaN
    pts_intersect = pts_intersect.dropna(subset=["index_right"])
    pts_intersect = pts_intersect.dropna()  # Drop lines which contain one or more NaN values

    return pts_intersect
