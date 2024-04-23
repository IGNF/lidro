# -*- coding: utf-8 -*-
""" Merge
"""
import os

import geopandas as gpd
from shapely.geometry import MultiPolygon
from shapely.ops import unary_union

from lidro.vectors.check_rectify_geometry import (
    check_geometry,
    remove_hole,
    simplify_geometry,
)


def merge_geom(input_folder: str, output_folder: str, crs: str):
    """Merge severals masks of hydro surfaces from the points classification of the input LAS/LAZ file,
    filter mask (keep only water's area > 150 m²) and save it as a GeoJSON file.

    Args:
        input_folder (str): folder who contains severals Masks Hydro
        output_folder (str): output folder
        crs (str): a pyproj CRS object used to create the output GeoJSON file
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

    # keep only water's area > 150 m²
    filter_geometry = [geom for geom in geometry if geom.area > 150]
    gdf_filter = gpd.GeoDataFrame(geometry=filter_geometry, crs=crs)

    # Check and rectify the invalid geometry
    gdf = check_geometry(gdf_filter)

    # Correcting geometric errors: simplifying certain shapes to make calculations easier
    buffer_geom = gdf["geometry"].apply(simplify_geometry)
    simplify_geom = buffer_geom.simplify(tolerance=0.5, preserve_topology=True)

    # Correction of holes (< 100m²) in Hydrological Masks
    list_parts = []
    for poly in simplify_geom:
        list_parts.append(poly)
    not_hole_geom = remove_hole(MultiPolygon(list_parts))
    geometry = gpd.GeoSeries(not_hole_geom.geoms, crs=crs).explode(index_parts=False)
    gdf = gpd.GeoDataFrame(geometry=geometry, crs=crs)

    # save the result
    gdf.to_file(os.path.join(output_folder, "MaskHydro_merge.geojson"), driver="GeoJSON", crs=crs)
