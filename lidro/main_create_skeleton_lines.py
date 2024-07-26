""" Main script for creating skeleton lines inside masks
"""
import hydra
from omegaconf import DictConfig

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from skeleton.create_skeleton_lines import create_branches_list, create_branches_pair, select_candidates
from skeleton.branch import Branch, line_merge


@hydra.main(version_base="1.2", config_path="../configs/", config_name="configs_lidro.yaml")
def run(config: DictConfig):
    """
    Get whole hydrographic skeleton lines, based on
    a geojson file containing multiple river contours.
    The result file will contain "skeleton" lines running in the middle of 
    those contours to describe the flow of the rivers, and lines crossing the contours
    to join with the skeleton lines, as bridge and other elements may "break" river contours
    args:
        - config (DictConfig): the config dict from hydra
    """

    gdf_hydro_global_mask = gpd.read_file(config.SKELETON.FILE_PATH.MASK_INPUT_PATH)
    crs = gdf_hydro_global_mask.crs  # Load a crs from input

    branches_list = create_branches_list(config, gdf_hydro_global_mask, crs)
    branches_pair_list = create_branches_pair(config, branches_list)
    validated_candidates = select_candidates(config, branches_pair_list)

    # create the gap lines from the selected candidates
    gap_lines_list = [validated_candidate.line for validated_candidate in validated_candidates]
    gdf_gap_lines = gpd.GeoDataFrame(geometry=gap_lines_list).set_crs(crs, allow_override=True)
    if config.SKELETON.FILE_PATH.GAP_LINES_OUTPUT_PATH:
        gdf_gap_lines.to_file(config.SKELETON.FILE_PATH.GAP_LINES_OUTPUT_PATH, driver='GeoJSON')

    # add the extremities used on each branch to close a gap to the list of gap_point of that branch,
    # to create a new line toward that extremity and know not to remove it during the "simplify"
    for candidate in validated_candidates:
        candidate.branch_1.gap_points.append(Point(candidate.extremity_1))
        candidate.branch_2.gap_points.append(Point(candidate.extremity_2))

    # get skeletons for all branches
    for branch in branches_list:
        branch: Branch
        branch.create_skeleton()
        branch.simplify()

    # putting all skeleton lines together, and save them if there is a path
    branch_lines_list = [branch.gdf_skeleton_lines for branch in branches_list]
    gdf_branch_lines = gpd.GeoDataFrame(pd.concat(branch_lines_list, ignore_index=True))
    if config.SKELETON.FILE_PATH.GAP_LINES_OUTPUT_PATH:
        gdf_branch_lines.to_file(config.SKELETON.FILE_PATH.SKELETON_LINES_OUTPUT_PATH, driver='GeoJSON')

    # saving all lines
    gdf_global_lines = gpd.GeoDataFrame(pd.concat([gdf_branch_lines, gdf_gap_lines], ignore_index=True))
    gdf_global_lines = line_merge(gdf_global_lines, crs) # merge lines into polylines
    gdf_global_lines.to_file(config.SKELETON.FILE_PATH.GLOBAL_LINES_OUTPUT_PATH, driver='GeoJSON')

if __name__ == "__main__":
    run()
