import sys

from hydra import compose, initialize
import geopandas as gpd
from omegaconf import DictConfig
from shapely import LineString, Point

from lidro.skeleton.branch import Branch, get_vertices_dict, get_df_points_from_gdf, line_merge, cut, cut_both_ends

sys.path.append('lidro/skeleton')

BRANCH_TEST_1_PATH = "data/skeleton_hydro/test_files/90.geojson"
CRS_FOR_TEST = 2154
WATER_MIN_SIZE_TEST = 20
CLIPPING_LENGTH = 50


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


def test_line_merge():
    """test of line_merge"""
    point_0_0 = [0, 0]
    point_0_1 = [0, 1]
    point_0_2 = [0, 2]
    point_0_3 = [0, 3]
    point_0_4 = [0, 4]
    point_0_5 = [0, 5]
    point_0_6 = [0, 6]
    point_1_4 = [1, 4]
    point_2_4 = [2, 4]

    line_1 = LineString([point_0_0, point_0_1, point_0_2])
    line_2 = LineString([point_0_2, point_0_3, point_0_4])
    line_3 = LineString([point_0_4, point_0_5])
    line_4 = LineString([point_0_5, point_0_6])
    line_5 = LineString([point_0_4, point_1_4])
    line_6 = LineString([point_1_4, point_2_4])

    line_list = [line_1,
                 line_2,
                 line_3,
                 line_4,
                 line_5,
                 line_6
                 ]

    gdf_gap_lines = gpd.GeoDataFrame(geometry=line_list).set_crs(CRS_FOR_TEST, allow_override=True)
    gdf_merged = line_merge(gdf_gap_lines, CRS_FOR_TEST)
    assert len(gdf_merged) == 3
    for line in gdf_merged['geometry']:
        if point_0_0 in line.coords:
            assert len(line.coords) == 5
            assert point_0_1 in line.coords
            assert point_0_2 in line.coords
            assert point_0_3 in line.coords
            assert point_0_4 in line.coords
        if point_0_6 in line.coords:
            assert len(line.coords) == 3
            assert point_0_4 in line.coords
            assert point_0_5 in line.coords
        if point_2_4 in line.coords:
            assert len(line.coords) == 3
            assert point_1_4 in line.coords
            assert point_0_4 in line.coords


def test_get_vertices_dict():
    point_0_0 = [0, 0]
    point_0_1 = [0, 1]
    point_0_2 = [0, 2]
    point_0_3 = [0, 3]
    point_0_4 = [0, 4]
    point_0_5 = [0, 5]
    point_0_6 = [0, 6]
    point_1_4 = [1, 4]
    point_2_4 = [2, 4]

    line_1 = LineString([point_0_0, point_0_1, point_0_2])
    line_2 = LineString([point_0_2, point_0_3, point_0_4])
    line_3 = LineString([point_0_4, point_0_5])
    line_4 = LineString([point_0_5, point_0_6])
    line_5 = LineString([point_0_4, point_1_4])
    line_6 = LineString([point_1_4, point_2_4])

    line_list = [line_1,
                 line_2,
                 line_3,
                 line_4,
                 line_5,
                 line_6
                 ]

    gdf_gap_lines = gpd.GeoDataFrame(geometry=line_list).set_crs(CRS_FOR_TEST, allow_override=True)

    vertices_dict = get_vertices_dict(gdf_gap_lines)

    assert len(vertices_dict) == 7
    assert vertices_dict[Point(point_0_0)] == [line_1]
    assert vertices_dict[Point(point_0_6)] == [line_4]
    assert vertices_dict[Point(point_2_4)] == [line_6]
    assert len(vertices_dict[Point(point_0_2)]) == 2
    assert len(vertices_dict[Point(point_0_4)]) == 3


def test_create_voronoi_lines():
    with initialize(version_base="1.2", config_path="../../configs"):
        config = compose(
            config_name="configs_lidro.yaml",
            overrides=[
                f"skeleton.branch.water_min_size={WATER_MIN_SIZE_TEST}",
            ]
        )
        branch_1 = read_branch(config, BRANCH_TEST_1_PATH, "test_branch_1")
        voronoi_lines = branch_1.create_voronoi_lines()
        assert len(voronoi_lines) == 1028

        voronoi_merged = line_merge(voronoi_lines, CRS_FOR_TEST)
        assert len(voronoi_merged) == 157
        vertices_dict = get_vertices_dict(voronoi_merged)
        # count number of extremities :
        nb_extremities = 0
        for lines_list in vertices_dict.values():
            if len(lines_list) == 1:
                nb_extremities += 1
        assert nb_extremities == 80


def test_creation_skeleton_lines():
    """test creation/simplification of skeleton lines for a branch"""
    with initialize(version_base="1.2", config_path="../../configs"):
        config = compose(
            config_name="configs_lidro.yaml",
            overrides=[
                f"skeleton.branch.water_min_size={WATER_MIN_SIZE_TEST}",
            ]
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


def test_cut():
    point_0_0 = [0, 0]
    point_0_1 = [0, 1]
    point_0_2 = [0, 2]
    point_0_4 = [0, 4]
    point_0_6 = [0, 6]

    line = LineString([point_0_0, point_0_1, point_0_2, point_0_4, point_0_6])
    result_line = cut(line, 2)

    # check that all points are here
    assert tuple(point_0_2) in result_line.coords
    assert tuple(point_0_4) in result_line.coords
    assert tuple(point_0_6) in result_line.coords
    assert len(result_line.coords) == 3

    # check that a correct new point has been created
    result_line = cut(line, 3)
    assert (0, 3) in result_line.coords

    # check that the cut keeps 1m of the line
    result_line = cut(line, 8)
    assert result_line.length == 1


def test_cut_both_ends():
    point_0_0 = [0, 0]
    point_0_1 = [0, 1]
    point_0_2 = [0, 2]
    point_0_4 = [0, 4]
    point_0_5 = [0, 5]
    point_0_6 = [0, 6]

    line = LineString([point_0_0, point_0_1, point_0_2, point_0_4, point_0_5, point_0_6])

    # check that all points are here
    result_line = cut_both_ends(line, 2)
    assert tuple(point_0_2) in result_line.coords
    assert tuple(point_0_4) in result_line.coords
    assert len(result_line.coords) == 2

    # check that correct new points have been created
    result_line = cut_both_ends(line, 4)
    assert (0, 3.5) in result_line.coords
    assert (0, 2.5) in result_line.coords

    # check that the cut keeps 1m of the line
    result_line = cut_both_ends(line, 8)
    assert result_line.length == 1


def test_shorten_lines():
    """test creation/simplification of skeleton lines for a branch"""
    with initialize(version_base="1.2", config_path="../../configs"):
        config = compose(
            config_name="configs_lidro.yaml",
            overrides=[
                f"skeleton.clipping_length={CLIPPING_LENGTH}",
            ]
        )
        branch_1 = read_branch(config, BRANCH_TEST_1_PATH, "test_branch_1")

        # create branch_1's skeleton
        branch_1.create_skeleton()
        branch_1.simplify()

        # check length before shortening
        total_length_before = sum(line.length for line in branch_1.gdf_skeleton_lines['geometry'])
        assert total_length_before == 775.0587088169204

        # check length after shortening
        branch_1.shorten_lines()
        total_length_after = sum(line.length for line in branch_1.gdf_skeleton_lines['geometry'])
        assert total_length_after == 675.0587088169583
