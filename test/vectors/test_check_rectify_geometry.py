import geopandas as gpd
from shapely.geometry import MultiPolygon

from lidro.merge_mask_hydro.vectors.check_rectify_geometry import (
    check_geometry,
    fix_invalid_geometry,
    simplify_geometry,
)

input = "./data/merge_mask_hydro/MaskHydro_merge.geojson"


def test_simplify_geometry_default():
    # Load each GeoJSON file as GeoDataFrame
    geojson = gpd.read_file(input)
    geometry = geojson["geometry"].unary_union
    buffer = simplify_geometry(geometry, 1, -1)
    assert isinstance(buffer, MultiPolygon)


def test_check_geometry_default():
    # Load each GeoJSON file as GeoDataFrame
    geojson = gpd.read_file(input)
    check_geom = check_geometry(geojson)
    assert isinstance(check_geom.dtypes, object)


def test_fix_invalid_geometry_default():
    # Load each GeoJSON file as GeoDataFrame
    geojson = gpd.read_file(input)
    valid_geom = geojson.geometry.apply(lambda geom: fix_invalid_geometry(geom))
    assert isinstance(valid_geom.dtypes, object)
    assert valid_geom[2] == geojson.geometry[2]
