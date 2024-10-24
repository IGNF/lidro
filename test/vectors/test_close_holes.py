import geopandas as gpd
import pytest
from shapely import get_num_interior_rings
from shapely.geometry import Polygon

from lidro.vectors.close_holes import close_holes

input = "./data/merge_mask_hydro/dataset_1/MaskHydro_merge_with_multibranch_skeleton.geojson"


@pytest.mark.parametrize(
    "min_area, expected_nb_interiors", [(None, 0), (0, 10), (10000, 1)]  # remove all holes  # keep all holes
)
def test_close_holes_default(min_area, expected_nb_interiors):
    # Load each GeoJSON file as GeoDataFrame
    geojson = gpd.read_file(input)
    geometry = geojson["geometry"][1]  # with contain severals holes

    print("NUM interiors::", get_num_interior_rings(geometry))
    mask_without_hole = close_holes(geometry, min_area)
    print(mask_without_hole.interiors)

    assert isinstance(mask_without_hole, Polygon)
    assert get_num_interior_rings(mask_without_hole) == expected_nb_interiors
