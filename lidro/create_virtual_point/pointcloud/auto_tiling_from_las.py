# -*- coding: utf-8 -*-
""" This function automatically creates the tiling of lidar tiles (.GeoJSON)
"""
import logging
import math
import os
from typing import List

import geopandas as gpd
import pdal
from shapely.geometry import Polygon


def extract_bounds_from_laz(input_points):
    """
    This function uses PDAL to read metadata from a .laz file.

    Args:
        input_points (str): Path to the input LAS/LAZ file

    Returns:
        tuple: A tuple containing (min_x, min_y, max_x, max_y) representing the bounding box.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If the metadata does not contain the required bounding box information.
        RuntimeError: If the PDAL pipeline execution fails.
    """
    # Check if the input file exists
    if not os.path.isfile(input_points):
        raise FileNotFoundError(f"The file '{input_points}' does not exist.")

    try:
        # Extract info by pointcloud using PDAL
        pipeline = pdal.Reader.las(filename=input_points, nosrs=True) | pdal.Filter.info()
        pipeline.execute()

        metadata = pipeline.metadata
        bounds = metadata.get("metadata", {}).get("readers.las", None)

        # Ensure bounds information is available
        if bounds is None or not all(k in bounds for k in ("minx", "miny", "maxx", "maxy")):
            raise ValueError(f"Bounding box information missing in metadata for file '{input_points}'.")

        # Retrieve bounding box coordinates (extent of the tile)
        min_x = bounds["minx"]
        min_y = bounds["miny"]
        max_x = bounds["maxx"]
        max_y = bounds["maxy"]

        return (min_x, min_y, max_x, max_y)

    except Exception as e:
        raise RuntimeError(f"Failed to extract bounds from '{input_points}': {e}")


def create_geojson_from_laz_files(laz_files: List, output_geojson_path: str, crs: str):
    """
    Create a GeoJSON from a list of .laz files by calculating the footprint (bounding box) of each tile
    and save it to a GeoJSON file.

    Args:
        laz_files (List): list of file paths to .laz files.
        output_geojson_path (str): the path where the resulting GeoJSON will be saved.
        crs (str): a pyproj CRS string used to create the output GeoJSON file.
    """
    # Return early if laz_files is empty, and make sure the output file is not created
    if not laz_files:
        logging.info("No LAZ files provided, skipping GeoJSON creation.")
        return

    # Check if CRS is valid by trying to set it
    try:
        if crs:
            gpd.GeoSeries([Polygon()]).set_crs(crs)
    except Exception as e:
        raise ValueError(f"Invalid CRS: {crs}") from e

    # Create a list of dictionaries representing the tiles
    tiles = [
        {
            "tile_id": str(int(min_x)) + "_" + str(math.ceil(max_y / 1000) * 1000),
            "tilename_las": os.path.basename(laz_file),
            "geometry": Polygon([(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]),
        }
        for laz_file in laz_files
        for min_x, min_y, max_x, max_y in [extract_bounds_from_laz(laz_file)]  # Single call to the function
    ]

    # Create a GeoDataFrame from the tiles list, explicitly setting the geometry column
    gdf = gpd.GeoDataFrame(tiles, geometry="geometry")

    # Set the coordinate reference system (CRS) if provided
    if crs:
        gdf.set_crs(crs, inplace=True)

    # Save the GeoDataFrame to a GeoJSON file
    gdf.to_file(output_geojson_path, driver="GeoJSON")
