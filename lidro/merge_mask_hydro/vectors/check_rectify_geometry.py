# -*- coding: utf-8 -*-
""" Rectify and check geometry
"""
from shapely.geometry import CAP_STYLE
from shapely.validation import make_valid


def simplify_geometry(s, buffer_positive: float, buffer_negative: float):
    """Buffer geometry
    Objective: create a HYDRO mask at the edge of the bank, not protruding over the banks

    Args:
        s (GeoJSON): Hydro Mask geometry
        buffer_positive (float): positive buffer from Mask Hydro
        buffer_negative (float): negative buffer from Mask Hydro

    Returns:
        GeoJSON: Hydro Mask geometry simplify
    """
    # Buffer
    _geom = s.buffer(buffer_positive, cap_style=CAP_STYLE.square)
    geom = _geom.buffer(buffer_negative, cap_style=CAP_STYLE.square)
    return geom


def fix_invalid_geometry(geometry):
    """Set invalid geoemtries

    Args:
        geometry (GeoJSON): Hydro Mask geometry

    Returns:
        GeoJSON: Hydro Mask geometry valid
    """

    if not geometry.is_valid:
        return make_valid(geometry)
    else:
        return geometry


def check_geometry(initial_gdf):
    """Check topology

    Args:
        initial_gdf (GeoJSON): Hydro Mask geometry

    Returns:
        GeoJSON: Hydro Mask geometry valid
    """
    # Obtain simple geometries
    gdf_simple = initial_gdf.explode(ignore_index=True)
    # Delete duplicate geoemtries if any
    gdf_without_duplicates = gdf_simple.drop_duplicates(ignore_index=True)
    # Identify invalid geometries and keep only valid ones
    gdf_valid = gdf_without_duplicates.copy()
    gdf_valid.geometry = gdf_valid.geometry.apply(lambda geom: fix_invalid_geometry(geom))
    return gdf_valid
