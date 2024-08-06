# -*- coding: utf-8 -*-
""" Merge skeleton by Mask Hydro
"""
import logging
import os

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, MultiLineString


def explode_multipart(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Explode multi-part geometries into single-part geometries

    Args:
        gdf (gpd.GeoDataFrame): A GeoDataFrame

    Returns:
       gpd.GeoDataframe :  a GeoDataFrame exploded
    """
    exploded_geom = gdf.explode(index_parts=True)
    exploded_geom = exploded_geom.reset_index(drop=True)

    return exploded_geom


def combine_and_connect_lines(geometries: list) -> LineString:
    """Combines and connects a list of LineString and MultiLineString geometries into a single LineString.

    Args:
        geometries (list): A list of LineString and/or MultiLineString objects.

    Returns:
        LineString: The merged and connected geometry.
    """
    # Convert all geometries into lists of lines
    lines = [geom.geoms if isinstance(geom, MultiLineString) else [geom] for geom in geometries]
    # Extract and combine all coordinates from the nested list using a list comprehension
    all_coords = [
        coord for sublist in lines for line in sublist if isinstance(line, LineString) for coord in line.coords
    ]
    # Create a new connected line
    connected_line = LineString(all_coords)

    return connected_line


def merge_skeleton_by_mask(
    input_skeleton: gpd.GeoDataFrame, input_mask_hydro: gpd.GeoDataFrame, output_dir: str, crs: str
) -> pd.DataFrame:
    """Combine skeleton lines into a single polyline for each hydro entity.
        Save a invalid mask to GeoDataframe

    Args:
        input_skeleton (gpd.GeoDataFrame): A GeoDataFrame containing each line from Hydro's Skeleton
        input_mask_hydro (gpd.GeoDataFrame): A GeoDataFrame containing Mask Hydro
        output_dir (str): output folder
        crs (str): a pyproj CRS object used to create the out

    Returns:
       Dataframe :  Dataframe with single polyline "skeleton" by hydro entity
    """  # Inputs
    gdf_skeleton = gpd.read_file(input_skeleton)
    gdf_skeleton = explode_multipart(gdf_skeleton)
    gdf_mask_hydro = gpd.read_file(input_mask_hydro)
    gdf_mask_hydro = explode_multipart(gdf_mask_hydro)

    # # Perform a spatial join to find skeletons within each mask_hydro
    gdf_joined = gpd.sjoin(gdf_skeleton, gdf_mask_hydro, how="inner", predicate="intersects")
    # geometry intersections with funtion "overlay"
    gdf_intersections = gpd.overlay(gdf_joined, gdf_mask_hydro, how="intersection")

    # Combine skeleton lines into a single polyline for each hydro entity
    combined_skeletons = gdf_intersections.groupby("index_right")["geometry"].apply(combine_and_connect_lines)
    gdf_combined_skeletons = gpd.GeoDataFrame(combined_skeletons, columns=["geometry"], crs=crs).reset_index()
    # # Re-join with mask_hydro to keep only the combined skeletons within masks
    gdf_joined_combined = gpd.sjoin(
        gdf_combined_skeletons, gdf_mask_hydro, how="inner", predicate="intersects", lsuffix="combined", rsuffix="mask"
    )

    # # Count the number of skeletons per mask
    skeleton_counts = gdf_joined_combined["index_mask"].value_counts()

    valid_masks = skeleton_counts[skeleton_counts == 1].index
    invalid_masks = skeleton_counts[skeleton_counts != 1].index

    # Filter to keep only masks with a single skeleton
    if not valid_masks.empty:
        # Filter the joined GeoDataFrame to keep only valid masks
        gdf_valid_joined = gdf_joined_combined[gdf_joined_combined["index_mask"].isin(valid_masks)]
        # Merge the geometries of masks and skeletons into the resulting GeoDataFrame
        df_result = gdf_valid_joined.merge(
            gdf_mask_hydro, left_on="index_mask", right_index=True, suffixes=("_skeleton", "_mask")
        )
        # Keep only necessary columns
        df_result = df_result[["geometry_skeleton", "geometry_mask"]]

    if not invalid_masks.empty:
        # Filter the joined GeoDataFrame to keep invalid masks
        gdf_invalid_joined = gdf_joined_combined[gdf_joined_combined["index_mask"].isin(valid_masks)]
        # Merge the geometries of masks and skeletons into the resulting GeoDataFrames
        df_exclusion = gdf_invalid_joined.merge(
            gdf_mask_hydro, left_on="index_mask", right_index=True, suffixes=("_skeleton", "_mask")
        )
        # Keep only necessary columns
        df_exclusion = df_exclusion[["geometry_skeleton", "geometry_mask"]]
        # Save the results and exclusions to separate GeoJSON files
        # Convert DataFrame to GeoDataFrame
        gdf_exclusion = gpd.GeoDataFrame(df_exclusion, geometry="geometry_mask")
        exclusions_outputs = os.path.join(output_dir, "mask_skeletons_exclusions.geojson")
        gdf_exclusion.to_file(exclusions_outputs, driver="GeoJSON")
        logging.info(f"Error: Save the exclusions rivers in GeoJSON : {exclusions_outputs}")

    return df_result
