# -*- coding: utf-8 -*-
""" Run function "virtual points"
"""
import logging
import os

import geopandas as gpd
import numpy as np
import pandas as pd

from lidro.create_virtual_point.vectors.apply_Z_from_grid import (
    calculate_grid_z_for_flattening,
    calculate_grid_z_with_model,
)
from lidro.create_virtual_point.vectors.create_grid_2D_inside_maskhydro import (
    generate_grid_from_geojson,
)
from lidro.create_virtual_point.vectors.flatten_river import flatten_little_river
from lidro.create_virtual_point.vectors.linear_regression_model import (
    calculate_linear_regression_line,
)


def lauch_virtual_points_by_section(
    points: gpd.GeoDataFrame,
    line: gpd.GeoDataFrame,
    mask_hydro: gpd.GeoDataFrame,
    crs: str,
    spacing: float,
    output_dir: str,
) -> gpd.GeoDataFrame:
    """This function generates a regular grid of 3D points spaced every N meters inside each hydro entity
    = virtual point

    Args:
        points (gpd.GeoDataFrame): A GeoDataFrame containing points along Hydro's Skeleton
        line (gpd.GeoDataFrame): A GeoDataFrame containing each line from Hydro's Skeleton
        mask_hydro (gpd.GeoDataFrame): A GeoDataFrame containing each mask hydro from Hydro's Skeleton
        crs (str): a pyproj CRS object used to create the output GeoJSON file
        spacing (float, optional): Spacing between the grid points in meters. The default value is 1 meter
        output_dir (str): folder to output Mask Hydro without virtual points

    Returns:
        gpd.GeoDataFrame: virtual points by Mask Hydro
    """
    # Check if points GeoDataFrame is empty or
    if points.empty or points["points_knn"].isnull().all():
        logging.warning("The points GeoDataFrame is empty. Saving the skeleton and mask hydro to GeoJSON.")
        masks_without_points = gpd.GeoDataFrame(columns=mask_hydro.columns, crs=mask_hydro.crs)
        for idx, mask in mask_hydro.iterrows():
            logging.warning(f"No points found within mask hydro {idx}. Adding to masks_without_points.")
            masks_without_points = pd.concat([masks_without_points, gpd.GeoDataFrame([mask], crs=mask_hydro.crs)])
        # Save the resulting masks_without_points to a GeoJSON file
        logging.warning("Save the mask Hydro where NON virtual points")
        output_mask_hydro_error = os.path.join(output_dir, "mask_hydro_no_virtual_points.geojson")
        masks_without_points.to_file(output_mask_hydro_error, driver="GeoJSON")

    if not points.empty and not points["points_knn"].isnull().all():
        # Step 1: Generates a regular 2D grid of evenly spaced points within a Mask Hydro
        gdf_grid = generate_grid_from_geojson(mask_hydro, spacing)
        # Calculate the length of the river
        river_length = float(line.length.iloc[0])

        # Step 2 : Model linear regression for river's lenght > 150 m
        # Otherwise flattening the river
        # Apply the algo according to the length of the river
        if river_length > 150:
            model, r2 = calculate_linear_regression_line(points, line, crs)
            if model == np.poly1d([0, 0]) and r2 == 0.0:
                masks_without_points = gpd.GeoDataFrame(columns=mask_hydro.columns, crs=mask_hydro.crs)
                for idx, mask in mask_hydro.iterrows():
                    masks_without_points = pd.concat(
                        [masks_without_points, gpd.GeoDataFrame([mask], crs=mask_hydro.crs)]
                    )
                # Save the resulting masks_without_points because of linear regression is impossible to a GeoJSON file
                output_mask_hydro_error = os.path.join(
                    output_dir, "mask_hydro_no_virtual_points_for_regression.geojson"
                )
                masks_without_points.to_file(output_mask_hydro_error, driver="GeoJSON")
            gdf_grid_with_z = calculate_grid_z_with_model(gdf_grid, line, model)
        else:
            predicted_z = flatten_little_river(points, line)
            if np.isnan(predicted_z) or predicted_z is None:
                masks_without_points = gpd.GeoDataFrame(columns=mask_hydro.columns, crs=mask_hydro.crs)
                for idx, mask in mask_hydro.iterrows():
                    masks_without_points = pd.concat(
                        [masks_without_points, gpd.GeoDataFrame([mask], crs=mask_hydro.crs)]
                    )
                # Save the resulting masks_without_points because of flattening river is impossible to a GeoJSON file
                output_mask_hydro_error = os.path.join(
                    output_dir, "mask_hydro_no_virtual_points_for_little_river.geojson"
                )
                masks_without_points.to_file(output_mask_hydro_error, driver="GeoJSON")
            gdf_grid_with_z = calculate_grid_z_for_flattening(gdf_grid, line, predicted_z)

        return gdf_grid_with_z
