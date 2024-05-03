# -*- coding: utf-8 -*-
""" Merge
"""
import os

import geopandas as gpd
from shapely.geometry import MultiPolygon
from shapely.ops import unary_union

from lidro.merge_mask_hydro.vectors.check_rectify_geometry import (
    check_geometry,
    simplify_geometry,
)
from lidro.merge_mask_hydro.vectors.remove_hole import remove_hole


def merge_geom(
    input_folder: str,
    output_folder: str,
    crs: str,
    water_area: int,
    buffer_positive: float,
    buffer_negative: float,
    tolerance: float,
):
    """Merge severals masks of hydro surfaces from the points classification of the input LAS/LAZ file,
    filter mask (keep only water's area > 150 m²) and save it as a GeoJSON file.

    Args:
        input_folder (str): folder who contains severals Masks Hydro
        output_folder (str): output folder
        crs (str): a pyproj CRS object used to create the output GeoJSON file
        water_area (int): filter Mask Hydro : keep only water's area (> 150 m² by default)
        buffer_positive (int): positive buffer from Mask Hydro
        buffer_negative (int): negative buffer from Mask Hydro
        tolerance (float): All parts of a simplified geometry will be no more
                           than tolerance distance from the original.
    """
    # List for stocking all GeoDataFrame
    polys = []

    # Browse all files in folder
    for fichier in os.listdir(input_folder):
        if fichier.endswith(".GeoJSON"):
            # Load each GeoJSON file as GeoDataFrame
            geojson = gpd.read_file(os.path.join(input_folder, fichier))
            merge_geom = geojson["geometry"].unary_union
            # Add the GeoDataFrame to the list
            polys.append(merge_geom)

    # Union geometry
    mergedPolys = unary_union(polys)

    geometry = gpd.GeoSeries(mergedPolys, crs=crs).explode(index_parts=False)

    # keep only water's area (> 150 m² by default)
    filter_geometry = [geom for geom in geometry if geom.area > water_area]
    gdf_filter = gpd.GeoDataFrame(geometry=filter_geometry, crs=crs)

    # Check and rectify the invalid geometry
    gdf = check_geometry(gdf_filter)

    # Correcting geometric errors: simplifying certain shapes to make calculations easier
    buffer_geom = simplify_geometry(gdf["geometry"], buffer_positive, buffer_negative).explode(index_parts=False)
    simplify_geom = buffer_geom.simplify(tolerance=tolerance, preserve_topology=True)

    # Correction of holes (< 100m²) in Hydrological Masks
    list_parts = []
    for poly in simplify_geom:
        list_parts.append(poly)

    not_hole_geom = remove_hole(MultiPolygon(list_parts))
    geometry = gpd.GeoSeries(not_hole_geom.geoms, crs=crs).explode(index_parts=False)
    # keep only water's area (> 150 m² by default) :
    filter_geometry_second = [geom for geom in geometry if geom.area > water_area]
    gdf = gpd.GeoDataFrame(geometry=filter_geometry_second, crs=crs)

    # save the result
    gdf.to_file(os.path.join(output_folder, "MaskHydro_merge.geojson"), driver="GeoJSON", crs=crs)
