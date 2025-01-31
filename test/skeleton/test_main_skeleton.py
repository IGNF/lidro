import os
from test.skeleton.test_branch import read_branch

import geopandas as gpd
import pandas as pd
import pytest
from dotenv import load_dotenv
from hydra import compose, initialize

from lidro.skeleton.branch import Candidate
from lidro.skeleton.create_skeleton_lines import (
    create_branches_list,
    create_branches_pair,
    query_db_for_bridge_across_gap,
    select_candidates,
)

load_dotenv()

DB_UNI_USER = os.getenv("DB_UNI_USER")
DB_UNI_PASSWORD = os.getenv("DB_UNI_PASSWORD")
CRS = 2154
MAIN_SKELETON_TEST_1_1_PATH = "data/other/skeleton/40.geojson"
MAIN_SKELETON_TEST_1_2_PATH = "data/other/skeleton/43.geojson"
MAIN_SKELETON_TEST_1_3_PATH = "data/other/skeleton/44.geojson"


def test_main_skeleton_1():
    with initialize(version_base="1.2", config_path="../../configs"):
        config = compose(
            config_name="configs_lidro.yaml",
        )

        branch_2_1 = read_branch(config, MAIN_SKELETON_TEST_1_1_PATH, "test_main_skeleton_1_1")
        branch_2_2 = read_branch(config, MAIN_SKELETON_TEST_1_2_PATH, "test_main_skeleton_1_2")
        branch_2_3 = read_branch(config, MAIN_SKELETON_TEST_1_3_PATH, "test_main_skeleton_1_3")

        three_branches = [branch_2_1.gdf_branch_mask, branch_2_2.gdf_branch_mask, branch_2_3.gdf_branch_mask]
        gdf_three_branches = gpd.GeoDataFrame(pd.concat(three_branches, ignore_index=True))

        branches_list = create_branches_list(config, gdf_three_branches, CRS)
        branches_pair_list = create_branches_pair(config, branches_list)
        validated_candidates = select_candidates(config, branches_pair_list)

        assert len(validated_candidates) == 2  # 3 branches close from each other, so there should be 2 candidates
        candidate_1 = validated_candidates[0]
        candidate_2 = validated_candidates[1]

        assert candidate_1.squared_distance < 30
        assert candidate_2.squared_distance < 75


# do that test only if we can connect to BD UNI
@pytest.mark.bduni
def test_query_db_for_bridge_across_gap():
    """Test : query_db_for_bridge_across_gap"""
    with initialize(version_base="1.2", config_path="../../configs"):
        config = compose(
            config_name="configs_lidro.yaml",
            overrides=[
                f"skeleton.db_uni.db_user={DB_UNI_USER}",
                f'skeleton.db_uni.db_password="{DB_UNI_PASSWORD}"',
            ],
        )
        dummy_candidate_1 = Candidate(None, None, (687575.5, 6748540.586179815), (687594.5, 6748515.586065615), 0)
        dummy_candidate_2 = Candidate(None, None, (689272.5, 6760595.5), (689322.5, 6760553.5), 0)

        is_bridge_1 = query_db_for_bridge_across_gap(config, dummy_candidate_1)
        is_bridge_2 = query_db_for_bridge_across_gap(config, dummy_candidate_2)
        assert not is_bridge_1
        assert is_bridge_2
