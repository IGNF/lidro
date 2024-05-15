import geopandas as gpd
from shapely.geometry import Polygon

from lidro.merge_mask_hydro.vectors.close_holes import close_holes

input = "./data/merge_mask_hydro/MaskHydro_merge.geojson"


def test_close_holes_default():
    # Load each GeoJSON file as GeoDataFrame
    geojson = gpd.read_file(input)
    geometry = geojson["geometry"][1] # with contain severals holes
    mask_without_hole = close_holes(geometry, 100)

    assert isinstance(mask_without_hole, Polygon)
