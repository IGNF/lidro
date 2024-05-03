import geopandas as gpd
from shapely.geometry import MultiPolygon

from lidro.merge_mask_hydro.vectors.remove_hole import remove_hole

input = "./data/merge_mask_hydro/MaskHydro_merge.geojson"


def test_remove_hole_default():
    # Load each GeoJSON file as GeoDataFrame
    geojson = gpd.read_file(input)
    geometry = geojson["geometry"].unary_union
    mask_without_hole = remove_hole(geometry)

    assert isinstance(mask_without_hole, MultiPolygon)
