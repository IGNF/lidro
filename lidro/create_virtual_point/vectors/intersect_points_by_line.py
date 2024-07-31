# -*- coding: utf-8 -*-
""" Identifies all points that intersect each line
"""
import geopandas as gpd
from shapely.geometry import CAP_STYLE, Polygon


def apply_buffers_to_geometry(line: gpd.GeoDataFrame, buffer: float) -> Polygon:
    """Buffer geometry
    Objective: apply buffer from hydro's section

    Args:
        line (gpd.GeoDataFrame): geopandas dataframe with input geometry
        buffer (float): buffer to apply to the input geometry

    Returns:
        Polygon: Hydro' section with buffer
    """
    # Buffer
    geom = line.buffer(buffer, cap_style=CAP_STYLE.square)
    return geom


def return_points_by_line(points: gpd.GeoDataFrame, line: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """This function identifies all points that intersect each hydro's section

    Args:
        points (gpd.GeoDataFrame): A GeoDataFrame containing points along Hydro's Skeleton
        line (gpd.GeoDataFrame): A GeoDataFrame containing each line from Hydro's Skeleton

    Returns:
        gpd.GeoDataFrame: A GeoDataframe containing only points that intersect each hydro's section
    """
    # Apply buffer (2 meters by default) from Mask Hydro
    line_buffer = apply_buffers_to_geometry(line, 0.1)
    gdf_line_buffer = gpd.GeoDataFrame(geometry=line_buffer)

    # Perform spatial join to find intersections
    pts_intersect = gpd.sjoin(points, gdf_line_buffer, how="left", predicate="intersects")

    # Filter out rows where 'index_right' is NaN
    pts_intersect = pts_intersect.dropna(subset=["index_right"])

    return pts_intersect
