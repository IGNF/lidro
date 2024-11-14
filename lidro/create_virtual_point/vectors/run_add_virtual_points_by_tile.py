# -*- coding: utf-8 -*-
""" Run function "create virtual points by tiles"
"""
import json
import logging
import os

from shapely.geometry import shape

from lidro.create_virtual_point.pointcloud.add_virtual_points_to_pointcloud import (
    add_virtual_points_by_tiles,
)


def compute_virtual_points_by_tiles(input_virtual_points: str, tile_geojson: str, input_dir: str, output_dir: str):
    """
    Loops through the tiles in the GeoJSON file and clips a LAZ file into multiple files based on polygons.

    Args:
        input_virtual_points (str): Path to the input virtual points file
        tile_geojson (str): Path to the GeoJSON file containing tile polygons
        input_dir (str): folder to input LIDAR tiles
        output_dir (str): folder to output virtual points by LIDAR tiles
    """
    # Load the GeoJSON tile geometries
    with open(tile_geojson, "r") as f:
        geojson_data = json.load(f)

    # Clip the virtual points by each tile
    for feature in geojson_data["features"]:
        if feature.get("geometry", {}).get("type") == "Polygon":
            name = feature["properties"]["tilename_las"]
            input_las = os.path.join(input_dir, name)
            output_file = os.path.join(output_dir, name)
            shapely_polygon = shape(feature["geometry"])
            add_virtual_points_by_tiles(input_virtual_points, input_las, output_file, shapely_polygon)
            logging.info(f"Clip virtual points by tiles : {input_las}")
