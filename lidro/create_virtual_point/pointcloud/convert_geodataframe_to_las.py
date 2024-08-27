# -*- coding: utf-8 -*-
""" this function convert GeoDataframe "virtual points" to LIDAR points
"""
import logging
import os

import geopandas as gpd
import laspy
import numpy as np
import pandas as pd


def geodataframe_to_las(virtual_points: gpd.GeoDataFrame, output_dir: str, crs: str, classes: int):
    """This function convert virtual points (GeoDataframe) to LIDAR points with classification for virtual points

    Args:
        virtual_points (gpd.GeoDataFrame): A GeoDataFrame containing virtuals points from Mask Hydro
        output_dir (str): folder to output LAS
        crs (str): a pyproj CRS object used to create the output GeoJSON file
        classes (int): The number of the classe assign those virtual points
    """
    # Combine all virtual points into a single GeoDataFrame
    grid_with_z = gpd.GeoDataFrame(pd.concat(virtual_points, ignore_index=True))

    # Extract x, y, and z coordinates
    grid_with_z["x"] = grid_with_z.geometry.x
    grid_with_z["y"] = grid_with_z.geometry.y
    grid_with_z["z"] = grid_with_z.geometry.z

    # Create a DataFrame with the necessary columns
    las_data = pd.DataFrame(
        {
            "x": grid_with_z["x"],
            "y": grid_with_z["y"],
            "z": grid_with_z["z"],
            "classification": np.full(len(grid_with_z), classes, dtype=np.uint8),  # Add classification of 68
        }
    )

    # Create a LAS file with laspy
    header = laspy.LasHeader(point_format=6, version="1.4")

    # Create a LAS file with laspy and add the VLR for CRS
    las = laspy.LasData(header)
    las.x = las_data["x"].values
    las.y = las_data["y"].values
    las.z = las_data["z"].values
    las.classification = las_data["classification"].values

    # Add CRS information to the VLR
    vlr = laspy.vlrs.known.WktCoordinateSystemVlr(crs.to_wkt())
    las.vlrs.append(vlr)

    # Save the LAS file
    output_las = os.path.join(output_dir, "virtual_points.las")
    las.write(output_las)
    logging.info(f"Virtual points LAS file saved to {output_las}")
