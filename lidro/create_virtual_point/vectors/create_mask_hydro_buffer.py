# -*- coding: utf-8 -*-
""" Extract a Z elevation value every N meters along the hydrographic skeleton
"""
import geopandas as gpd
from shapely.geometry import CAP_STYLE, MultiPolygon


def apply_buffers_to_geometry(hydro_mask: gpd.GeoDataFrame, buffer: float) -> MultiPolygon:
    """Buffer geometry
    Objective: create a HYDRO mask largest

    Args:
        hydro_mask (gpd.GeoDataFrame): geopandas dataframe with input geometry
        buffer (float): buffer to apply to the input geometry

    Returns:
        MutliPolygon: Mask Hydro with buffer
    """
    # Buffer
    geom = hydro_mask.buffer(buffer, cap_style=CAP_STYLE.square)
    return geom


def create_mask_hydro_buffer(file_mask: str, buffer: float, crs: str | int) -> gpd.GeoDataFrame:
    """Apply buffer (2 meters by default) from Mask Hydro

    Args:
        file_mask (str): Path from Mask Hydro
        buffer (float): buffer to apply to the input geometry
        crs (str | int): Make a CRS from an EPSG code : CRS WKT string

    Returns:
        gpd.GeoDataFrame : geometry columns are encoded to WKT
    """
    # Read Mask Hydro merged
    gdf = gpd.read_file(file_mask, crs=crs).unary_union

    # Apply buffer (2 meters by default) from Mask Hydro
    gdf = apply_buffers_to_geometry(gdf, buffer)

    return gdf
