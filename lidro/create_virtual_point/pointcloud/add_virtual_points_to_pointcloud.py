# -*- coding: utf-8 -*-
""" Add virtual points by tiles"""
import json

import pdal
from shapely.geometry import Polygon


def add_virtual_points_by_tiles(input_file: str, input_las: str, output_laz_file: str, geom: Polygon):
    """Add virtual points (3D point grid in LAZ format) by LIDAR tiles (tiling file)

    Args:
        input_file (str): Path to the input virtual points file (LAZ)
        input_las (str): Path to the LIDAR tiles (LAZ)
        output_dir (str): Path to the output LIDAR tiles (LAZ) with virtual points
        geom (Polygon):  Shapely Polygon (LIDAR tiles)
    """
    # Add virtual points by LIDAR tiles
    pipeline = [
        {"type": "readers.las", "filename": input_file, "nosrs": True},
        {"type": "filters.crop", "polygon": geom.wkt},  # Convert the Shapely Polygon to WKT
        {"type": "readers.las", "filename": input_las, "nosrs": True},
        {"type": "filters.merge"},
        {
            "type": "writers.las",
            "filename": output_laz_file,
            "compression": True,
            "minor_version": 4,
            "dataformat_id": 6,
        },
    ]
    # Create and execute the pipeline
    p = pdal.Pipeline(json.dumps(pipeline))
    p.execute()
