import sys

from hydra import compose, initialize
import geopandas as gpd
from omegaconf import DictConfig

from lidro.skeleton.branch import Branch, get_vertices_dict

sys.path.append('lidro/skeleton')

BRANCH_TEST_1_PATH = "test_files/90.geojson"


def read_branch(config: DictConfig, branch_path: str, branch_name: str) -> Branch:
    gdf_branch_mask = gpd.read_file(branch_path)
    crs = gdf_branch_mask.crs
    mask_branch = gdf_branch_mask["geometry"][0]
    return Branch(config, branch_name, mask_branch, crs)


def test_branch_1():
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
