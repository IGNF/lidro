import geopandas as gpd
from shapely.geometry import MultiPolygon

from lidro.merge_mask_hydro.vectors.check_rectify_geometry import (
    apply_buffers_to_geometry,
    fix_topology,
)

input = "./data/merge_mask_hydro/MaskHydro_merge.geojson"


def test_apply_buffers_to_geometry_default():
    # Load each GeoJSON file as GeoDataFrame
    geojson = gpd.read_file(input)
    geometry = geojson["geometry"].unary_union
    buffer = apply_buffers_to_geometry(geometry, 1, -1)
    assert isinstance(buffer, MultiPolygon)


def test_fix_topology_default():
    # Load each GeoJSON file as GeoDataFrame
    geojson = gpd.read_file(input)
    check_geom = fix_topology(geojson)

    assert isinstance(check_geom.dtypes, object)

    assert geojson.geometry.dtype == "geometry"

    # duplicates in the data
    assert not geojson.duplicated().any(), "There are duplicates in the data"

    # Check geometry
    assert geojson["geometry"].is_valid.all(), "Geometry no-valid"

