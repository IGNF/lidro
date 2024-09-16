import os
import shutil
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Polygon

# Import the function from your module
from lidro.create_virtual_point.pointcloud.auto_tiling_from_las import (
    create_geojson_from_laz_files,
    extract_bounds_from_laz,
)

TMP_PATH = Path("./tmp/virtual_points/pointcloud/auto_tiling_from_las")


def setup_module():
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


@pytest.fixture
def mock_laz_files():
    # LAZ files
    return [
        "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las",
        "./data/pointcloud/Semis_2021_0830_6291_LA93_IGN69.laz",
    ]


def test_extract_bounds_from_laz_file_not_found():
    """Test that the function raises a FileNotFoundError when the file does not exist."""
    non_existing_file = "./data/pointcloud/non_existing_file.laz"

    with pytest.raises(FileNotFoundError, match=f"The file '{non_existing_file}' does not exist."):
        extract_bounds_from_laz(non_existing_file)


def test_extract_bounds_from_real_laz_file():
    """Test if extract_bounds_from_laz returns a bounding box of 1km x 1km for the real file."""
    laz_file = "./data/pointcloud/Semis_2021_0830_6291_LA93_IGN69.laz"
    bounds = extract_bounds_from_laz(laz_file)

    assert len(bounds) == 4, "Bounding box should return 4 values."
    assert bounds == (830000, 6290000, 831000, 6291000), f"Expected (830000, 6290000, 831000, 6291000), got {bounds}"

    min_x, min_y, max_x, max_y = bounds
    # Check that the values are within expected ranges
    width = max_x - min_x
    height = max_y - min_y
    # Ensure the bounding box forms a 1km x 1km tile
    expected_size = 1000.0
    tolerance = 1.0  # Allow small tolerance for precision errors
    assert abs(width - expected_size) <= tolerance, f"Width should be approximately 1km, got {width}."
    assert abs(height - expected_size) <= tolerance, f"Height should be approximately 1km, got {height}."


def test_create_geojson_from_laz_files(mock_laz_files):
    """
    Test creating a GeoJSON from .laz files and check the structure.
    """
    # Path for output geojson
    output_geojson_path = Path(TMP_PATH) / "output_tiles.geojson"

    # Call the function to test
    create_geojson_from_laz_files(mock_laz_files, str(output_geojson_path), crs="EPSG:2154")

    # Verify that the file was created
    assert os.path.exists(output_geojson_path), "GeoJSON file should be created."

    # Load the generated GeoJSON file
    gdf = gpd.read_file(output_geojson_path)

    # Verify that the geometries match the bounding boxes
    expected_polygons = [
        Polygon(
            [
                (706044.9375, 6626159.0),
                (706292.25, 6626159.0),
                (706292.25, 6626324.0),
                (706044.9375, 6626324.0),
                (706044.9375, 6626159.0),
            ]
        ),
        Polygon(
            [
                (830000.0, 6290000.0),
                (831000.0, 6290000.0),
                (831000.0, 6291000.0),
                (830000.0, 6291000.0),
                (830000.0, 6290000.0),
            ]
        ),
    ]

    for i, geom in enumerate(gdf.geometry):
        assert geom.equals(expected_polygons[i]), f"Polygon {i} doesn't match expected geometry"
        assert geom.geom_type == "Polygon", f"Geometry type is not Polygon for {i}, found {geom.geom_type}."
        assert geom.is_valid, "Polygon is not valid."
        assert len(geom.exterior.coords) == 5, "Polygon should have 5 coordinates, including the closing point."

    # Verify that the number of tiles is correct
    assert len(gdf) == 2, "The number of tiles in the GeoJSON is incorrect."


def test_empty_laz_file_list():
    """Test when an empty list of LAZ files is provided."""
    # Path for output geojson
    output_geojson_path = Path(TMP_PATH) / "output_empty_laz_file.geojson"

    # Ensure no leftover file exists before the test
    if os.path.exists(output_geojson_path):
        os.remove(output_geojson_path)

    # Call the function with an empty list
    create_geojson_from_laz_files([], str(output_geojson_path), crs="EPSG:2154")

    # Verify that the GeoJSON file is not created
    assert not os.path.exists(output_geojson_path), "GeoJSON file should not be created with an empty file list."


def test_invalid_crs(mock_laz_files):
    """Test handling of invalid coordinate reference systems (CRS)."""
    # Path for output geojson
    output_geojson_path = Path(TMP_PATH) / "output_invalid_crs.geojson"

    with pytest.raises(ValueError, match="Invalid CRS"):
        create_geojson_from_laz_files(mock_laz_files, str(output_geojson_path), crs="INVALID_CRS")
