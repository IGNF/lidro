import geopandas as gpd
from shapely.geometry import MultiPolygon

from lidro.merge_mask_hydro.vectors.check_rectify_geometry import (
    apply_buffers_to_geometry,
    check_geometry,
)

input = "./data/merge_mask_hydro/MaskHydro_merge.geojson"


def test_apply_buffers_to_geometry_default():
    # Load each GeoJSON file as GeoDataFrame
    geojson = gpd.read_file(input)
    geometry = geojson["geometry"].unary_union
    buffer = apply_buffers_to_geometry(geometry, 1, -1)
    assert isinstance(buffer, MultiPolygon)


def test_check_geometry_default():
    # Load each GeoJSON file as GeoDataFrame
    geojson = gpd.read_file(input)
    check_geom = check_geometry(geojson)
    assert isinstance(check_geom.dtypes, object)
