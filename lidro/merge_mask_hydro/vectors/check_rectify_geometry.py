# -*- coding: utf-8 -*-
""" Rectify and check geometry
"""
from shapely.geometry import CAP_STYLE
import geopandas as gpd

def apply_buffers_to_geometry(hydro_mask, buffer_positive: float, buffer_negative: float):
    """Buffer geometry
    Objective: create a HYDRO mask at the edge of the bank, not protruding over the banks. 
    In this case, negative buffer should be bigger than positive buffer

    Args:
        hydro_mask (gpd.GeoDataFrame): geopandas dataframe with input geometry
        buffer_positive (float): positive buffer to apply to the input geometry
        buffer_negative (float): negative buffer to apply to the input geometry
    Returns:
        GeoJSON: updated geometry
    """
    # Buffer
    _geom = hydro_mask.buffer(buffer_positive, cap_style=CAP_STYLE.square)
    geom = _geom.buffer(buffer_negative, cap_style=CAP_STYLE.square)
    return geom


def fix_topology(initial_gdf: gpd.GeoDataFrame)-> gpd.GeoDataFrame:
    """Fix topology

    Args:
        initial_gdf (gpd.GeoDataFrame): Hydro Mask geometry

    Returns:
        gpd.GeoDataFrame: Hydro Mask geometry valid
    """    
    # Obtain simple geometries
    gdf_simple = initial_gdf.explode(ignore_index=True)

    gdf_simple = gdf_simple.drop_duplicates(ignore_index=True)

    # Identify invalid geometries, then return a GeoSeries with valid geometries
    gdf_valid = gdf_simple.make_valid()

    return gdf_valid
