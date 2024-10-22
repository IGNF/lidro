# -*- coding: utf-8 -*-
""" Merge skeleton by Mask Hydro
"""
import logging
import os

import geopandas as gpd
import pandas as pd
from shapely import line_merge, set_precision

from lidro.vectors.close_holes import close_holes


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


def combine_skeletons(gdf_skeleton: gpd.GeoDataFrame, gdf_mask_hydro: gpd.GeoDataFrame, crs: str) -> gpd.GeoDataFrame:
    """Combine skeletons that belong to the same entity (single polygon) of the hydro mask.

    Args:
        gdf_skeleton (gpd.GeoDataFrame): hydro skeletons (one skeleton by row)
        gdf_mask_hydro (gpd.GeoDataFrame): hydro mask (one entity/polygon by row)
        crs (str): a pyproj CRS object used to create the output

    Raises:
        ValueError: when some skeleton lines are disjoint inside a single mask polygon

    Returns:
        gpd.GeoDataFrame: each row contains the combined skeleton lines for the one hydro entity
    """
    # # Perform a spatial join to find skeletons within each mask_hydro
    gdf_joined = gpd.sjoin(gdf_skeleton, gdf_mask_hydro, how="inner", predicate="intersects")
    # geometry intersections with function "overlay"
    gdf_intersections = gpd.overlay(gdf_joined, gdf_mask_hydro, how="intersection", keep_geom_type=True)

    # Combine skeleton lines into a single polyline for each hydro entity
    # Group geometries based on index_right
    combined_skeletons = gdf_intersections.dissolve(by="index_right")
    # Apply line_merge where it is possible (skeleton lines are joint), raise an error in other cases
    combined_skeletons["geometry"] = combined_skeletons["geometry"].apply(line_merge)

    if not (combined_skeletons["geometry"].geom_type == "LineString").all():
        raise ValueError(
            "Combined skeleton geometry should all be of type LineString,"
            f"got {combined_skeletons['geometry'].geom_type} instead. This means that "
            "there is a hole in the skeleton inside one hydro entity, or the skeleton has "
            "multiple branches."
        )

    gdf_combined_skeletons = gpd.GeoDataFrame(combined_skeletons, columns=["geometry"], crs=crs).reset_index()

    # # Re-join with mask_hydro to keep only the combined skeletons within masks
    gdf_joined_combined = gpd.sjoin(
        gdf_combined_skeletons, gdf_mask_hydro, how="inner", predicate="intersects", lsuffix="combined", rsuffix="mask"
    )

    return gdf_joined_combined


def merge_skeleton_by_mask(input_skeleton: str, input_mask_hydro: str, output_dir: str, crs: str) -> pd.DataFrame:
    """Combine skeleton lines into a single polyline for each hydro entity.
        Save a invalid mask to GeoDataframe

    Args:
        input_skeleton (str): the path to a file (that can be converted to a GeoDataFrame)
            containing each line from Hydro's Skeleton
        input_mask_hydro (str): he path to a file (that can be converted to a GeoDataFrame)
            containing the hydro mask
        output_dir (str): output folder
        crs (str): a pyproj CRS object used to create the out

    Returns:
       Dataframe :  Dataframe with single "skeleton" LineString by hydro entity
    """
    # Inputs
    gdf_skeleton = gpd.read_file(input_skeleton)
    gdf_skeleton = explode_multipart(gdf_skeleton)
    # set centimetric precision (equivalent to point cloud precision)
    gdf_skeleton["geometry"] = set_precision(gdf_skeleton["geometry"], 0.01)

    gdf_mask_hydro = gpd.read_file(input_mask_hydro)
    gdf_mask_hydro = explode_multipart(gdf_mask_hydro)
    # Close holes in gdf_mask-hydro to prevent island from dividing a skeleton into multiple parts
    gdf_mask_hydro["geometry"] = gdf_mask_hydro["geometry"].apply(close_holes)
    print("gdf_mask_hydro::", gdf_mask_hydro)

    gdf_combined = combine_skeletons(gdf_skeleton, gdf_mask_hydro, crs)

    # # Count the number of skeletons per mask
    skeleton_counts = gdf_combined["index_mask"].value_counts()

    valid_masks = skeleton_counts[skeleton_counts == 1].index
    invalid_masks = skeleton_counts[skeleton_counts != 1].index

    # Filter to keep only masks with a single skeleton
    if not valid_masks.empty:
        # Filter the joined GeoDataFrame to keep only valid masks
        gdf_valid_joined = gdf_combined[gdf_combined["index_mask"].isin(valid_masks)]
        # Merge the geometries of masks and skeletons into the resulting GeoDataFrame
        df_result = gdf_valid_joined.merge(
            gdf_mask_hydro, left_on="index_mask", right_index=True, suffixes=("_skeleton", "_mask")
        )
        # Keep only necessary columns
        df_result = df_result[["geometry_skeleton", "geometry_mask"]]

    else:
        df_result = gpd.GeoDataFrame(columns=["geometry_skeleton", "geometry_mask"])

    if not invalid_masks.empty:
        # Filter the joined GeoDataFrame to keep invalid masks
        gdf_invalid_joined = gdf_combined[gdf_combined["index_mask"].isin(valid_masks)]
        # Merge the geometries of masks and skeletons into the resulting GeoDataFrames
        df_exclusion = gdf_invalid_joined.merge(
            gdf_mask_hydro, left_on="index_mask", right_index=True, suffixes=("_skeleton", "_mask")
        )
        # Keep only necessary columns
        df_exclusion = df_exclusion[["geometry_mask"]]
        # Save the results and exclusions to separate GeoJSON files
        # Convert DataFrame to GeoDataFrame
        gdf_exclusion = gpd.GeoDataFrame(df_exclusion, geometry="geometry_mask")
        exclusions_outputs = os.path.join(output_dir, "mask_skeletons_exclusions.geojson")
        gdf_exclusion.to_file(exclusions_outputs, driver="GeoJSON")
        logging.info(f"Error: Save the exclusions rivers in GeoJSON : {exclusions_outputs}")

    return df_result
