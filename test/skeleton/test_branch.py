import sys

from hydra import compose, initialize
import geopandas as gpd
from omegaconf import DictConfig
from shapely import LineString

from lidro.skeleton.branch import Branch, get_vertices_dict, get_df_points_from_gdf, line_merge

sys.path.append('lidro/skeleton')

BRANCH_TEST_1_PATH = "test_files/90.geojson"


def read_branch(config: DictConfig, branch_path: str, branch_name: str) -> Branch:
    gdf_branch_mask = gpd.read_file(branch_path)
    crs = gdf_branch_mask.crs
    mask_branch = gdf_branch_mask["geometry"][0]
    return Branch(config, branch_name, mask_branch, crs)


def test_get_df_points_from_gdf():
    """test of 'get_df_points_from_gdf'"""
    gdf_branch_mask = gpd.read_file(BRANCH_TEST_1_PATH)
    df_all_coords = get_df_points_from_gdf(gdf_branch_mask)
    assert len(df_all_coords) == 235


# def test_line_merge():
#     line_1 = LineString([0, 0], [0, 1], [0, 2])
#     line_2 = LineString([0, 2], [0, 3], [0, 4])
#     line_3 = LineString([0, 4], [0, 5])
#     line_4 = LineString([0, 5], [0, 6])
#     line_5 = LineString([0, 4], [1, 4])
#     line_6 = LineString([1, 4], [2, 4])
#     line_list = [line_1,
#                  line_2,
#                  line_3,
#                  line_4,
#                  line_5,
#                  line_6
#                  ]
    
#     # gap_lines_list = [validated_candidate.line for validated_candidate in validated_candidates]
#     # gdf_gap_lines = gpd.GeoDataFrame(geometry=gap_lines_list).set_crs(crs, allow_override=True)
#     pass


def test_creation_skeleton_lines():
    """test creation/simplification of skeleton lines for a branch"""
    with initialize(version_base="1.2", config_path="../../configs"):
        config = compose(
            config_name="configs_lidro.yaml",
        )
        branch_1 = read_branch(config, BRANCH_TEST_1_PATH, "test_branch_1")

        # create branch_1's skeleton
        branch_1.create_skeleton()
        branch_1.simplify()

        # number of extremity of branch_1's skeleton
        vertices_dict = get_vertices_dict(branch_1.gdf_skeleton_lines)
        extremities_cpt = 0
        for lines_list in vertices_dict.values():
            if len(lines_list) == 1:
                extremities_cpt += 1

        assert extremities_cpt == 3  # check that this branch's skeleton has exactly 3 extremities

