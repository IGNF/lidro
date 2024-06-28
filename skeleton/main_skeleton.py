from typing import List, Tuple

import hydra
from omegaconf import DictConfig

import geopandas as gpd
import pandas as pd
import psycopg2
# from shapely import Point
from shapely.geometry import Point


from branch import Branch, Candidate
from group_maker import GroupMaker


def db_connector(config: DictConfig):
    """Return a connector to the postgis database"""
    return psycopg2.connect(
        database=config.DB_UNI.DB_NAME,
        host=config.DB_UNI.DB_HOST,
        user=config.DB_UNI.DB_USER,
        password=config.DB_UNI.DB_PASSWORD,
        port=config.DB_UNI.DB_PORT
        )


def query_db_for_bridge(config: DictConfig, candidate: Candidate) -> bool:
    """
    Query the database to check if a candidate for a bridge indeed intersects a bridge
    """
    middle_x = (candidate.extremity_1[0] + candidate.extremity_2[0]) / 2
    middle_y = (candidate.extremity_1[1] + candidate.extremity_2[1]) / 2
    new_ext_1_x = (candidate.extremity_1[0] - middle_x) * config.RATIO_GAP + middle_x
    new_ext_1_y = (candidate.extremity_1[1] - middle_y) * config.RATIO_GAP + middle_y
    new_ext_2_x = (candidate.extremity_2[0] - middle_x) * config.RATIO_GAP + middle_x
    new_ext_2_y = (candidate.extremity_2[1] - middle_y) * config.RATIO_GAP + middle_y
    line = f"LINESTRING({new_ext_1_x} {new_ext_1_y}, {new_ext_2_x} {new_ext_2_y})"
    query_linear = (
        "SELECT cleabs FROM public.Construction_lineaire "
        "WHERE gcms_detruit = false "
        f"AND ST_Intersects(ST_Force2D(geometrie), ST_GeomFromText('{line}'));"
        )
    query_area = (
        "SELECT cleabs FROM public.Construction_surfacique "
        "WHERE gcms_detruit = false "
        f"AND ST_Intersects(ST_Force2D(geometrie), ST_GeomFromText('{line}'));"
        )

    with db_connector(config) as db_conn:
        with db_conn.cursor() as db_cursor:
            db_cursor.execute(query_linear)
            results = db_cursor.fetchall()
            # if no result with linear bridge, maybe with area bridge...
            if not results:
                db_cursor.execute(query_area)
                results = db_cursor.fetchall()
    return True if results else False


def select_candidates(config: DictConfig, branches_pair_list: List[Tuple]) -> List[Candidate]:
    """
    selects candidates between pairs of branches
    """
    # get all the branches (each only once, hence the set)
    branch_set = set()
    for branch_a, branch_b, _ in branches_pair_list:
        branch_set.add(branch_a)
        branch_set.add(branch_b)

    branch_group = GroupMaker(list(branch_set))
    validated_candidates = []
    extremities_connected = set()
    for branch_a, branch_b, _ in branches_pair_list:
        branch_a: Branch

        # we don't create link between 2 branches already connected
        if branch_group.are_together(branch_a, branch_b):
            continue
        candidates = branch_a.get_gap_candidates(branch_b)

        # test each candidate to see if we can draw a line for them
        nb_bridges_crossed = 0
        for candidate in candidates:
            candidate: Candidate
            # we connect each extremity only once
            if candidate.extremity_1 in extremities_connected or candidate.extremity_2 in extremities_connected:
                continue

            # if the gap is wide enough, we check with DB_Uni to see if there is a bridge
            if candidate.squared_distance > config.GAP_WIDTH_CHECK_DB * config.GAP_WIDTH_CHECK_DB:
                is_bridge = query_db_for_bridge(config, candidate)
                # if the line does not cross any bridge, we don't validate that candidate
                if not is_bridge:
                    continue

            # candidate validated
            extremities_connected.add(candidate.extremity_1)
            extremities_connected.add(candidate.extremity_2)
            validated_candidates.append(candidate)
            branch_group.put_together(branch_a, branch_b)
            nb_bridges_crossed += 1
            if nb_bridges_crossed >= config.MAX_BRIDGES:   # max bridges reached between those 2 branches
                break
    return validated_candidates

@hydra.main(config_path="../configs/", config_name="configs_skeleton.yaml")
def run(config: DictConfig):
# def run(gdf_mask_hydro, crs):
    """Calculer le squelette hydrographique

    Args:
        - mask_hydro (GeoJSON) : Mask Hydrographic (Polygone)
        - crs (str): code EPSG
    """
    gdf_mask_hydro = gpd.read_file(config.MASK_INPUT_PATH)
    crs = gdf_mask_hydro.crs  # Load a crs from input

    # create branches
    branches_list = []
    for index_branch, branch_mask_row in gdf_mask_hydro.iterrows():
        mask_branch = branch_mask_row["geometry"]
        new_branch = Branch(config, index_branch, mask_branch, crs)
        branches_list.append(new_branch)

    # create branches_pair_list, that stores all pairs of branches close enough to have a bridge
    branches_pair_list = []
    for index, branch_a in enumerate(branches_list[:-1]):
        for branch_b in branches_list[index + 1:]:
            distance = branch_a.distance_to_a_branch(branch_b)
            if distance < config.MAX_GAP_WIDTH:
                branches_pair_list.append((branch_a, branch_b, distance))

    # sort the branches pairs by distance between them
    branches_pair_list = sorted(branches_pair_list, key=lambda branches_pair:  branches_pair[2])

    validated_candidates = select_candidates(config, branches_pair_list)

    # create the bridge lines from the selected candidates
    bridge_lines = [validated_candidate.line for validated_candidate in validated_candidates]
    gdf_bridge_lines = gpd.GeoDataFrame(geometry=bridge_lines).set_crs(crs, allow_override=True)
    gdf_bridge_lines.to_file("test_bridges_group_maker_mask.geojson", driver='GeoJSON')

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

    # saving skeleton lines from all branches
    branch_lines_list = [branch.gdf_skeleton_lines for branch in branches_list]
    gdf_branch_lines = gpd.GeoDataFrame(pd.concat(branch_lines_list, ignore_index=True))
    gdf_branch_lines.to_file(config.SKELETON_OUTPUT_PATH, driver='GeoJSON')


if __name__ == "__main__":
    run()
