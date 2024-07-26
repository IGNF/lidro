from typing import List, Tuple

import hydra
from omegaconf import DictConfig
from pyproj.crs.crs import CRS

import geopandas as gpd
import pandas as pd
from pandas import DataFrame as df
from geopandas.geodataframe import GeoDataFrame
import psycopg2
from shapely.geometry import Point

from skeleton.branch import Branch, Candidate
from skeleton.group_maker import GroupMaker


def db_connector(config: DictConfig):
    """
    Return a connector to the postgis database
    args:
        - config (DictConfig): the config dict from hydra
    """
    return psycopg2.connect(
        database=config.SKELETON.DB_UNI.DB_NAME,
        host=config.SKELETON.DB_UNI.DB_HOST,
        user=config.SKELETON.DB_UNI.DB_USER,
        password=config.SKELETON.DB_UNI.DB_PASSWORD,
        port=config.SKELETON.DB_UNI.DB_PORT
        )


def query_db_for_bridge_across_gap(config: DictConfig, candidate: Candidate) -> bool:
    """
    Query the database to check if a candidate to close a gap between 2 branches intersects a bridge
    args:
        - config (DictConfig): the config dict from hydra
        - candidate (Candidate): the candidate we want to check if it crosses a bridge
    """
    # creation of the segment that will be checked to see if it intersects a bridge
    # that segment is the line between the 2 extremities, reduced by a ratio ( if too long, the line can intesects
    # bridge from another area)
    middle_x = (candidate.extremity_1[0] + candidate.extremity_2[0]) / 2
    middle_y = (candidate.extremity_1[1] + candidate.extremity_2[1]) / 2
    new_ext_1_x = (candidate.extremity_1[0] - middle_x) * config.SKELETON.RATIO_GAP + middle_x
    new_ext_1_y = (candidate.extremity_1[1] - middle_y) * config.SKELETON.RATIO_GAP + middle_y
    new_ext_2_x = (candidate.extremity_2[0] - middle_x) * config.SKELETON.RATIO_GAP + middle_x
    new_ext_2_y = (candidate.extremity_2[1] - middle_y) * config.SKELETON.RATIO_GAP + middle_y

    # creation of queries
    line = f"LINESTRING({new_ext_1_x} {new_ext_1_y}, {new_ext_2_x} {new_ext_2_y})"
    query_linear = (
        "SELECT cleabs FROM public.Construction_lineaire "
        "WHERE gcms_detruit = false "
        "AND nature = 'Pont' "
        f"AND ST_Intersects(ST_Force2D(geometrie), ST_GeomFromText('{line}'));"
        )
    query_area = (
        "SELECT cleabs FROM public.Construction_surfacique "
        "WHERE gcms_detruit = false "
        "AND nature = 'Pont' "
        f"AND ST_Intersects(ST_Force2D(geometrie), ST_GeomFromText('{line}'));"
        )

    # execution of queries
    with db_connector(config) as db_conn:
        with db_conn.cursor() as db_cursor:
            db_cursor.execute(query_linear)
            results = db_cursor.fetchall()
            # if no result with linear bridge, maybe with area bridge...
            if not results:
                db_cursor.execute(query_area)
                results = db_cursor.fetchall()

    if results:
        pass

    return True if results else False


def select_candidates(
        config: DictConfig,
        branches_pair_list: List[Tuple[Candidate, Candidate, float]]
        ) -> List[Candidate]:
    """
    create candidates between pairs of branches
    args:
        - config (DictConfig): the config dict from hydra
        - branches_pair_list (List[Tuple[Candidate, Candidate, float]]) : a list of paris, containing
          2 candidates and the minimal distance between them
    """

    # sort the branches pairs by distance between each pair (so the first gap to be closed is the smallest)
    branches_pair_list = sorted(branches_pair_list, key=lambda branches_pair: branches_pair[2])

    # get all the branches (each only once, hence the set)
    branch_set = set()
    for branch_a, branch_b, _ in branches_pair_list:
        branch_set.add(branch_a)
        branch_set.add(branch_b)

    # use GroupMaker to avoid cycles (if branch A connected to branch B, and
    # branch B connected to branch C, then
    # C cannot be connected to A
    branch_group = GroupMaker(list(branch_set))

    validated_candidates = []
    extremities_connected = set()
    for branch_a, branch_b, _ in branches_pair_list:
        branch_a: Branch

        # we don't create link between 2 branches already connected
        if branch_group.are_together(branch_a, branch_b):
            continue

        candidates = branch_a.get_candidates(branch_b)  # get all possible candidates between A abd B

        # test each candidate to see if we can draw a line between its branches
        nb_bridges_crossed = 0
        for candidate in candidates:
            candidate: Candidate
            # we connect each extremity only once
            if candidate.extremity_1 in extremities_connected or candidate.extremity_2 in extremities_connected:
                continue

            # if the gap is wide enough, we check with DB_Uni to see if there is a bridge
            # On the other hand, if it's small enough the candidate is automatically validated
            if candidate.squared_distance > config.SKELETON.GAP_WIDTH_CHECK_DB * config.SKELETON.GAP_WIDTH_CHECK_DB:
                is_bridge = query_db_for_bridge_across_gap(config, candidate)
                # if the line does not cross any bridge, we don't validate that candidate
                if not is_bridge:
                    continue

            # candidate validated
            extremities_connected.add(candidate.extremity_1)
            extremities_connected.add(candidate.extremity_2)
            validated_candidates.append(candidate)
            # a candidate has been validated between A and B, so we put together A and B
            branch_group.put_together(branch_a, branch_b)
            nb_bridges_crossed += 1
            if nb_bridges_crossed >= config.SKELETON.MAX_BRIDGES:   # max bridges reached between those 2 branches
                break
    return validated_candidates


def create_branches_list(config: DictConfig, gdf_hydro_global_mask: GeoDataFrame, crs: CRS) -> List[Branch]:
    """
    create the list of branches from the global mask
    Args:
        - config (DictConfig): the config dict from hydra
        - gdf_hydro_global_mask (GeoDataFrame): a geodataframe containing a list of polygon,
            each polygon being the mask of a river's branch
        - crs (CRS); the crs of gdf_hydro_global_mask
    """

    branches_list = []
    for index_branch, branch_mask_row in gdf_hydro_global_mask.iterrows():
        mask_branch = branch_mask_row["geometry"]
        new_branch = Branch(config, index_branch, mask_branch, crs)
        branches_list.append(new_branch)
    return branches_list


def create_branches_pair(config: DictConfig, branches_list: List[Branch]) -> List[Tuple[Candidate, Candidate, float]]:
    """
    create a list of pairs of branches, containing all the pairs of branches close enough from each other
    for the water to flow anyway between them
    Args:
        - config (DictConfig): the config dict from hydra
    """

    # create branches_pair_list, that stores all pairs of branches close enough to have a bridge
    branches_pair_list = []
    for index, branch_a in enumerate(branches_list[:-1]):
        for branch_b in branches_list[index + 1:]:
            distance = branch_a.distance_to_a_branch(branch_b)
            if distance < config.SKELETON.MAX_GAP_WIDTH:
                branches_pair_list.append((branch_a, branch_b, distance))
    return branches_pair_list


@hydra.main(version_base="1.2", config_path="../../configs/", config_name="configs_lidro.yaml")
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
    if config.SKELETON.FILE_PATH.GAP_LINES_OUTPUT_PATH:
        gdf_gap_lines = gpd.GeoDataFrame(geometry=gap_lines_list).set_crs(crs, allow_override=True)
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
    branch_lines_list.append(gdf_gap_lines)
    gdf_global_lines = gpd.GeoDataFrame(pd.concat(branch_lines_list, ignore_index=True))
    gdf_global_lines.to_file(config.SKELETON.FILE_PATH.GLOBAL_LINES_OUTPUT_PATH, driver='GeoJSON')


if __name__ == "__main__":
    run()
