# -*- coding: utf-8 -*-
""" Run function "update skeleton with z"
"""
import logging
import os

import geopandas as gpd
import numpy as np
import pandas as pd

from lidro.create_virtual_point.vectors.create_skeleton_3d import (
    skeleton_3d_with_flatten,
    skeleton_3d_with_linear_regression,
)
from lidro.create_virtual_point.vectors.flatten_river import flatten_little_river
from lidro.create_virtual_point.vectors.linear_regression_model import (
    calculate_linear_regression_line,
)


def compute_skeleton_with_z(
    points: gpd.GeoDataFrame,
    line: gpd.GeoDataFrame,
    mask_hydro: gpd.GeoDataFrame,
    crs: str,
    spacing: float,
    length: int,
    output_dir: str,
) -> gpd.GeoDataFrame:
    """This function update skeleton with Z

    Args:
        points (gpd.GeoDataFrame): A GeoDataFrame containing points along Hydro's Skeleton
        line (gpd.GeoDataFrame): A GeoDataFrame containing each line from Hydro's Skeleton
        mask_hydro (gpd.GeoDataFrame): A GeoDataFrame containing each mask hydro from Hydro's Skeleton
        crs (str): A pyproj CRS object used to create the output GeoJSON file
        spacing (float, optional): Spacing between the grid points in meters.
                                   The default value is 0.5 meter
        length (int, optional): Minimum length of a river to use the linear regression model.
                                      The default value is 150 meters.
        output_dir (str): Folder to output Mask Hydro without virtual points

    Returns:
        gpd.GeoDataFrame: All skeleton with Z
    """
    # Check if the points DataFrame is empty and all the values in the "points_knn" column are null
    if points.empty or points["points_knn"].isnull().all():
        logging.warning("The points GeoDataFrame is empty. Saving the skeleton and mask hydro to GeoJSON.")
        masks_without_points = gpd.GeoDataFrame(columns=mask_hydro.columns, crs=mask_hydro.crs)
        for idx, mask in mask_hydro.iterrows():
            logging.warning(f"No points found within mask hydro {idx}. Adding to masks_without_points.")
            masks_without_points = pd.concat([masks_without_points, gpd.GeoDataFrame([mask], crs=mask_hydro.crs)])
        # Save the resulting masks_without_points to a GeoJSON file
        output_mask_hydro_error = os.path.join(output_dir, "mask_hydro_no_virtual_points.geojson")
        masks_without_points.to_file(output_mask_hydro_error, driver="GeoJSON")
    else:
        # Calculate the length of the river
        river_length = float(line.length.iloc[0])

        # Step 2 : Model linear regression for river's length > 150 m
        if river_length > length:
            model, r2 = calculate_linear_regression_line(points, line, crs)
            if model == np.poly1d([0, 0]) and r2 == 0.0:
                masks_without_points = gpd.GeoDataFrame(columns=mask_hydro.columns, crs=mask_hydro.crs)
                for idx, mask in mask_hydro.iterrows():
                    masks_without_points = pd.concat(
                        [masks_without_points, gpd.GeoDataFrame([mask], crs=mask_hydro.crs)]
                    )
                # Save the resulting masks_without_points because of linear regression is impossible to a GeoJSON file
                output_mask_hydro_error = os.path.join(
                    output_dir, "mask_hydro_no_virtual_points_with_regression.geojson"
                )
                logging.warning(
                    f"Save masks_without_points because linear regression is impossible: {output_mask_hydro_error}"
                )
                masks_without_points.to_file(output_mask_hydro_error, driver="GeoJSON")
            # Apply model from skeleton
            skeleton_hydro_3D = skeleton_3d_with_linear_regression(line, model, crs)
        # Step 2 bis: Model flattening for river's length < 150 m or river's length == 150 m
        else:
            predicted_z = flatten_little_river(points, line)
            if predicted_z == 0:
                masks_without_points = gpd.GeoDataFrame(columns=mask_hydro.columns, crs=mask_hydro.crs)
                for idx, mask in mask_hydro.iterrows():
                    masks_without_points = pd.concat(
                        [masks_without_points, gpd.GeoDataFrame([mask], crs=mask_hydro.crs)]
                    )
                # Save the resulting masks_without_points because of flattening river is impossible to a GeoJSON file
                output_mask_hydro_error = os.path.join(
                    output_dir, "mask_hydro_no_virtual_points_for_little_river.geojson"
                )
                logging.warning(
                    f"Save masks_without_points because of flattening river is impossible: {output_mask_hydro_error}"
                )
                masks_without_points.to_file(output_mask_hydro_error, driver="GeoJSON")
            # Apply model from skeleton
            skeleton_hydro_3D = skeleton_3d_with_flatten(line, model, crs)

        return skeleton_hydro_3D
