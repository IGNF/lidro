import geopandas as gpd
from shapely.geometry import MultiPolygon

from lidro.merge_mask_hydro.vectors.check_rectify_geometry import (
    apply_buffers_to_geometry,
    fix_topology,
)

def test_apply_buffers_to_geometry_default():
    input = "./data/merge_mask_hydro/MaskHydro_merge.geojson"
    # Load each GeoJSON file as GeoDataFrame
    geojson = gpd.read_file(input)
    geometry = geojson["geometry"].unary_union
    buffer = apply_buffers_to_geometry(geometry, 1, -1)
    assert isinstance(buffer, MultiPolygon)


def test_fix_topology_default():
    input = "./data/merge_mask_hydro/MaskHydro_merge.geojson"
    # Load each GeoJSON file as GeoDataFrame
    geojson = gpd.read_file(input)
    check_geom = fix_topology(geojson)

    assert isinstance(check_geom.dtypes, object)

    assert check_geom.geometry.dtype == "geometry"

    # Check not duplicates in the data
    assert not check_geom.duplicated().any(), "There are duplicates in the data"

    # # Check geometry
    assert check_geom.geometry.is_valid.all(), "Geometry no-valid"

def test_fix_topology_error():
    input_error = "./data/merge_mask_hydro/MaskHydro_merge_NoValid.geojson"
    # Load each GeoJSON file as GeoDataFrame
    geojson = gpd.read_file(input_error)
    check_geom = fix_topology(geojson)

    assert isinstance(check_geom.dtypes, object)
    
    assert check_geom.geometry.dtype == "geometry"

    # Check not duplicates in the data
    assert not check_geom.duplicated().any(), "There are duplicates in the data"

    # # Check geometry
    assert check_geom.geometry.is_valid.all(), "Geometry no-valid"