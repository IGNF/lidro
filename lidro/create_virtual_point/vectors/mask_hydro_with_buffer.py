# -*- coding: utf-8 -*-
""" Extract a Z elevation value every N meters along the hydrographic skeleton
"""
import geopandas as gpd
from shapely.geometry import CAP_STYLE


def import_mask_hydro_with_buffer(file_mask: str, buffer: float, crs: str | int) -> gpd.GeoDataFrame:
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
    gdf_buffer = gdf.buffer(buffer, cap_style=CAP_STYLE.square)

    return gdf_buffer
