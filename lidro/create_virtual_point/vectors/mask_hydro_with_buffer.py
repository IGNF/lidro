# -*- coding: utf-8 -*-
""" Create a new Mask Hydro at the edge of the bank with a buffer
"""
import geopandas as gpd
from shapely.geometry import CAP_STYLE


def import_mask_hydro_with_buffer(file_mask: str, buffer: float, crs: str | int) -> gpd.GeoDataFrame:
    """Create a new Mask Hydro at the edge of the bank with a buffer (+50 cm and -N cm)

    Args:
        file_mask (str): Path from Mask Hydro
        buffer (float): buffer to apply to the input geometry
        crs (str | int): Make a CRS from an EPSG code : CRS WKT string

    Returns:
        gpd.GeoDataFrame : geometry columns are encoded to WKT
    """
    # Read Mask Hydro merged
    gdf = gpd.read_file(file_mask, crs=crs).unary_union

    # Apply negative's buffer + difference from Mask Hydro
    # Return a polygon representing the limit of the bank with a buffer of N meters
    gdf_buffer = gdf.difference(gdf.buffer(-abs(buffer), cap_style=CAP_STYLE.square))

    return gdf_buffer
