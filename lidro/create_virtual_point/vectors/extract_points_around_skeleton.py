# -*- coding: utf-8 -*-
""" Extract points around skeleton by tile
"""
import logging
import os
from typing import List

import geopandas as gpd
import pandas as pd
from pdaltools.las_info import las_get_xy_bounds
from shapely.geometry import Point

from lidro.create_virtual_point.pointcloud.crop_las import (
    read_filter_and_crop_pointcloud,
)
from lidro.create_virtual_point.vectors.clip_points_with_bounding_box import (
    clip_points_with_box,
)
from lidro.create_virtual_point.vectors.las_around_point import filter_las_around_point


def extract_points_around_skeleton_points_one_tile(
    filename: str,
    input_dir: str,
    output_dir: str,
    input_mask_hydro_buffer: gpd.GeoDataFrame,
    points_skeleton_gdf: gpd.GeoDataFrame,
    crs: str | int,
    classes: List[int:int],
    k: int,
):
    """Severals steps :
        1-  Crop filtered pointcloud by Mask Hydro with buffer
        2-  Extract a Z elevation value along the hydrographic skeleton

    Args:
        filename (str): filename to the LAS file
        input_dir (str): input folder
        output_dir (str): ouput folder
        input_mask_hydro_buffer (gpd.GeoDataFrame): hydro mask with buffer
        points_skeleton_gdf (gpd.GeoDataFrame): Points every N meters along skeleton hydro
        crs (str | int): Make a CRS from an EPSG code : CRS WKT string
        classes (List):  List of classes to use for the filtering
        k (int): the number of nearest neighbors to find
    """
    # Step 1 : Crop filtered pointcloud by Mask Hydro with buffer
    input_dir_points = os.path.join(input_dir, "pointcloud")
    tilename = os.path.splitext(filename)[0]  # filename to the LAS file
    input_pointcloud = os.path.join(input_dir_points, filename)  # path to the LAS file
    logging.info(f"\nCroping filtered pointcloud by Mask Hydro with buffer for tile : {tilename}")
    # Croping filtered pointcloud by Mask Hydro with buffer for tile
    points_clip = read_filter_and_crop_pointcloud(input_pointcloud, str(input_mask_hydro_buffer), classes)
    logging.info(f"\nCropping skeleton points for tile: {tilename}")
    # Extract bounding box for clipping points by tile
    bbox = las_get_xy_bounds(input_pointcloud)
    points_skeleton_clip = clip_points_with_box(points_skeleton_gdf, bbox)
    # Create list with Skeleton's points with Z for step 4
    points_skeleton_with_z_clip = [
        ([geom.x, geom.y]) for geom in points_skeleton_clip.geometry if isinstance(geom, Point)
    ]
    # Step 2 : Extract a Z elevation value along the hydrographic skeleton
    logging.info(f"\nExtract a Z elevation value along the hydrographic skeleton for tile : {tilename}")
    points_Z = filter_las_around_point(points_skeleton_with_z_clip, points_clip, k)
    df_points_z = pd.DataFrame(points_Z)  # Convert Dataframe
    # Convert list "points_knn" to string
    df_points_z["points_knn_str"] = df_points_z["points_knn"].apply(lambda x: str(x))
    df_points_z = df_points_z[["geometry", "points_knn_str"]]
    if not df_points_z.empty and "points_knn_str" in df_points_z.columns and "geometry" in df_points_z.columns:
        # Convert the DataFrame to a GeoDataFrame
        points_z_gdf = gpd.GeoDataFrame(df_points_z, geometry="geometry")
        points_z_gdf.set_crs(crs, inplace=True)
        # Save the result by LIDAR tile
        output_geojson_path = os.path.join(output_dir, "_points_skeleton".join([tilename, ".geojson"]))
        points_z_gdf.to_file(output_geojson_path, driver="GeoJSON")
        logging.info(f"Result saved to {output_geojson_path}")
