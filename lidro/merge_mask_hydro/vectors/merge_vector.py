# -*- coding: utf-8 -*-
""" Merge
"""
import os

import geopandas as gpd
from shapely.ops import unary_union

from lidro.merge_mask_hydro.vectors.check_rectify_geometry import (
    apply_buffers_to_geometry,
    check_geometry,
)
from lidro.merge_mask_hydro.vectors.close_holes import close_holes


def merge_geom(
    input_folder: str,
    output_folder: str,
    crs: str,
    min_water_area: int,
    buffer_positive: float,
    buffer_negative: float,
    tolerance: float,
):
    """Merge several masks of hydro surfaces from the points classification
       of the input LAS/LAZ files from input_folder,
       filter mask (keep only water's area > min_water_area) and save it as a GeoJSON file.

    Args:
        input_folder (str): folder which contains several geojson geometries
        output_folder (str): output folder
        crs (str): a pyproj CRS object used to create the output GeoJSON file
        min_water_area (int): filter Mask Hydro : keep only water objects with area bigger
                              than min_water_area (> 150 m² by default)
        buffer_positive (int): positive buffer to apply to the mask
        buffer_negative (int): negative buffer to apply to the mask
        tolerance (float): All parts of a simplified geometry will be no more
                           than tolerance distance from the original.
    """
    # Browse all files in folder
    gdf = [
        gpd.read_file(os.path.join(input_folder, file), crs=crs).unary_union
        for file in os.listdir(input_folder)
        if file.endswith(".GeoJSON")
    ]

    # Union geometry
    gdf = unary_union(gdf)
    gdf = gpd.GeoSeries(gdf, crs=crs).explode(index_parts=False)

    # keep only water's area (> 150 m² by default)
    gdf = gdf[gdf.geometry.area > min_water_area]

    # Correct geometric errors: simplify certain shapes to make calculations easier
    gdf = apply_buffers_to_geometry(gdf, buffer_positive, buffer_negative).explode(index_parts=False)
    gdf = gdf.simplify(tolerance=tolerance, preserve_topology=True)

    # Check and rectify the invalid geometry
    gdf = check_geometry(gdf)

    # Correction of holes (< 100m²) in Hydrological Masks
    gdf = close_holes(gdf, min_hole_area=100)
    gdf = gpd.GeoSeries(gdf, crs=crs).explode(index_parts=False)

    # filter out water area < min_water_area (150 m² by default) again to make sure that previous geometry updates did not generate new small water areas
    gdf = gdf[gdf.geometry.area > min_water_area]

    # save the result
    gdf.to_file(os.path.join(output_folder, "MaskHydro_merge.geojson"), driver="GeoJSON", crs=crs)
