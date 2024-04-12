# -*- coding: utf-8 -*-
""" Merge
"""
import os

import geopandas as gpd
from shapely.ops import unary_union


def merge_geom(input_folder: str, output_folder: str, crs: str):
    """Merge severals masks of hydro surfaces from the points classification of the input LAS/LAZ file,
    filter mask (keep only water's area > 1000 m²) and save it as a GeoJSON file.

    Args:
        input_folder (str): folder who contains severals Masks Hydro
        output_folder (str): output folder
        crs (str): a pyproj CRS object used to create the output GeoJSON file
    """
    # List for stocking all GeoDataFrame
    polys = []

    # Parcourir tous les fichiers dans le dossier
    for fichier in os.listdir(input_folder):
        if fichier.endswith(".GeoJSON"):
            # Charger chaque fichier GeoJSON en tant que GeoDataFrame
            geojson = gpd.read_file(os.path.join(input_folder, fichier))
            merge_geom = geojson["geometry"].unary_union
            # Ajouter le GeoDataFrame à la liste
            polys.append(merge_geom)

    # Union geometry
    mergedPolys = unary_union(polys)

    geometry = gpd.GeoSeries(mergedPolys, crs=crs).explode(index_parts=False)

    # keep only water's area > 1000 m²
    filter_geometry = [geom for geom in geometry if geom.area > 1000]

    gdf = gpd.GeoDataFrame(geometry=filter_geometry, crs=crs)

    # save the result
    gdf.to_file(os.path.join(output_folder, "MaskHydro_merge.geojson"), driver="GeoJSON", crs=crs)
