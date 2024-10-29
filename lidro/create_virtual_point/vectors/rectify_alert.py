# -*- coding: utf-8 -*-
"""Optimized function to adjust Z values of the downstream skeleton"""
import logging
from typing import List, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import CAP_STYLE, LineString

from lidro.create_virtual_point.vectors.intersect_skeleton_by_bridge import (
    extract_bridge_skeleton_info,
)


def rectify_z_from_downstream_skeleton(
    input_bridge: str, list_skeleton_with_z: List, crs: str
) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Adjusts the Z values of N points in the downstream skeleton to match the Z value
    of the last point in the upstream skeleton, up until reaching z_upstream + 0.1.
    If no alert is active, adds the original downstream geometry without modification.

    Args:
        input_bridge (str): Path to the bridge input file
        list_skeleton_with_z (List): List of skeletons with Z values and associated hydro mask
        crs (str): Coordinate reference system

    Returns:
        Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]: A tuple of GeoDataFrames containing
        the updated or original downstream and upstream skeleton geometries.
    """
    # Load bridge data and apply a 5m buffer to each geometry
    gdf_bridge = gpd.read_file(input_bridge, crs=crs)
    gdf_bridge["geometry"] = gdf_bridge.buffer(5, cap_style=CAP_STYLE.square)

    downstream_geometries = []
    upstream_geometries = []

    for bridge in gdf_bridge["geometry"]:
        skeleton_info = extract_bridge_skeleton_info(bridge, list_skeleton_with_z)

        downstream_geometry = skeleton_info["downstream_geometry"]
        upstream_geometry = skeleton_info["upstream_geometry"]

        # Add upstream geometry directly without modification
        upstream_geometries.extend(upstream_geometry)

        # Check if alert is active and process downstream geometry accordingly
        if skeleton_info["alert"].iloc[0] is True:
            logging.info("Alert detected for bridge intersection. Updating Z values...")
            z_upstream = float(skeleton_info["z_upstream"].iloc[0])
            z_downstream = float(skeleton_info["z_downstream"].iloc[0])

            for line in downstream_geometry:
                # Convert coordinates to NumPy arrays for efficient Z-value handling
                coords = np.array(line.coords)
                x_vals, y_vals, z_vals = coords[:, 0], coords[:, 1], coords[:, 2]

                # Set the initial Z value of the downstream skeleton to z_downstream
                z_vals[0] = z_downstream

                # Apply z_upstream to all points in the downstream skeleton until reaching z_upstream
                z_vals[z_vals > z_upstream] = z_upstream

                # Rebuild the geometry with the updated Z values
                updated_coords = np.column_stack([x_vals, y_vals, z_vals])
                downstream_geometries.append(LineString(updated_coords))
        else:
            # If no alert, add the original downstream geometry
            logging.info("No alert detected. Adding original downstream geometry.")
            downstream_geometries.extend(downstream_geometry)

    # Create GeoDataFrames for downstream and upstream geometries
    downstream_gdf = gpd.GeoDataFrame([{"geometry": geom} for geom in downstream_geometries], crs=crs)

    upstream_gdf = gpd.GeoDataFrame([{"geometry": geom} for geom in upstream_geometries], crs=crs)

    return downstream_gdf, upstream_gdf


def create_list_rectify_skeleton_with_mask(
    input_bridge: str, hydro_mask_path: str, list_skeleton_with_z: List, crs: str
) -> List[gpd.GeoDataFrame]:
    """
    Processes skeletons per hydro mask, prioritizes downstream geometries, and returns
    a list of GeoDataFrames containing unique skeleton geometries intersected
    with each hydro mask along with the geometry of each mask.

    Args:
        input_bridge (str): Path to the bridge input file
        list_skeleton_with_z (List): List of skeletons with Z values and associated hydro masks
        crs (str): Coordinate reference system
        hydro_mask_path (str): Path to the hydro mask GeoJSON file

    Returns:
        List[gpd.GeoDataFrame]: A list of GeoDataFrames, each containing a unique skeleton geometry
                                intersected with its hydro mask and the geometry of the mask itself.
    """
    # # Load the hydro mask GeoJSON as a GeoDataFrame
    hydro_masks = gpd.read_file(hydro_mask_path).to_crs(crs)

    # # Generate downstream and upstream skeletons
    downstream_gdf, upstream_gdf = rectify_z_from_downstream_skeleton(input_bridge, list_skeleton_with_z, crs)

    # # Identify unique downstream geometries and add unmatched upstream geometries
    # Keep Only the Matching Geometries from downstream_gdf
    result_gdf = downstream_gdf.drop_duplicates(subset="geometry")
    # Add Non-Matching Geometries from upstream_gdf
    unmatched_upstream = upstream_gdf[upstream_gdf["geometry"].isin(downstream_gdf["geometry"]) is False]
    result_gdf = pd.concat([result_gdf, unmatched_upstream], ignore_index=True)

    # # For each mask, get the intersecting skeleton geometries and prioritize downstream geometries
    list_result_gdfs = []
    for mask in hydro_masks.itertuples():
        # Filter result_gdf to only include geometries that intersect with the current mask
        intersecting_geometries = result_gdf[result_gdf.intersects(mask.geometry)]
        # Prioritize downstream geometries within the intersecting set
        mask_downstream = intersecting_geometries[intersecting_geometries["geometry"].isin(downstream_gdf["geometry"])]
        if not mask_downstream.empty:
            mask_gdf = mask_downstream
        else:
            mask_gdf = intersecting_geometries
        # Add the mask geometry as a new column for reference
        mask_gdf = mask_gdf.copy()
        mask_gdf["geometry_mask"] = mask.geometry

        list_result_gdfs.append(mask_gdf)

    return list_result_gdfs
