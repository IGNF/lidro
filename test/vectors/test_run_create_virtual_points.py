import os
import shutil
from pathlib import Path

import geopandas as gpd
import numpy as np
from pyproj import CRS
from shapely.geometry import LineString, Point, Polygon

from lidro.create_virtual_point.vectors.run_create_virtual_points import (
    lauch_virtual_points_by_section,
)

TMP_PATH = Path("./tmp/create_virtual_point/vectors/run_create_virtual_points/")


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def create_test_data_no_points():
    # Create empty GeoDataFrame with the required structure
    points = gpd.GeoDataFrame({"geometry": [], "points_knn": []}, crs="EPSG:2154")

    # Create example lines and mask_hydro GeoDataFrames with two entries each
    lines = gpd.GeoDataFrame(
        {
            "geometry": [
                LineString([(700000, 6600000), (700100, 6600100)]),
                LineString([(700200, 6600200), (700300, 6600300)]),
            ]
        },
        crs="EPSG:2154",
    )

    mask_hydro = gpd.GeoDataFrame(
        {
            "geometry": [
                Polygon(
                    [(700000, 6600000), (700100, 6600000), (700100, 6600100), (700000, 6600100), (700000, 6600000)]
                ),
                Polygon(
                    [(700200, 6600200), (700300, 6600200), (700300, 6600300), (700200, 6600300), (700200, 6600200)]
                ),
            ]
        },
        crs="EPSG:2154",
    )

    return points, lines, mask_hydro


def create_test_data_with_points():
    # Create GeoDataFrame with points and points_knn columns
    points = gpd.GeoDataFrame(
        {
            "geometry": [Point(700050, 6600050)],
            "points_knn": [
                [
                    (700000, 6600000, 10),
                    (700050, 6600050, 15),
                    (700100, 6600100, 20),
                    (700200, 6600200, 30),
                    (700300, 6600300, 40),
                ]
            ],
        },
        crs="EPSG:2154",
    )

    # Example lines and mask_hydro GeoDataFrames
    lines = gpd.GeoDataFrame(
        {
            "geometry": [
                LineString([(700000, 6600000), (700300, 6600300)]),
                LineString([(700400, 6600400), (700500, 6600500)]),
            ]
        },
        crs="EPSG:2154",
    )

    mask_hydro = gpd.GeoDataFrame(
        {
            "geometry": [
                Polygon(
                    [(699900, 6599900), (700400, 6599900), (700400, 6600400), (699900, 6600400), (699900, 6599900)]
                ),
                Polygon(
                    [(700400, 6600400), (700500, 6600400), (700500, 6600500), (700400, 6600500), (700400, 6600400)]
                ),
            ]
        },
        crs="EPSG:2154",
    )

    return points, lines, mask_hydro


def create_test_data_with_geometry_only():
    # Create GeoDataFrame with points column but without points_knn
    points = gpd.GeoDataFrame(
        {"geometry": [Point(700050, 6600050), Point(700250, 6600250)], "points_knn": [None, None]}, crs="EPSG:2154"
    )

    # Example line and mask_hydro GeoDataFrames
    lines = gpd.GeoDataFrame(
        {
            "geometry": [
                LineString([(700000, 6600000), (700100, 6600100)]),
                LineString([(700200, 6600200), (700300, 6600300)]),
            ]
        },
        crs="EPSG:2154",
    )
    mask_hydro = gpd.GeoDataFrame(
        {
            "geometry": [
                Polygon(
                    [(700000, 6600000), (700100, 6600000), (700100, 6600100), (700000, 6600100), (700000, 6600000)]
                ),
                Polygon(
                    [(700200, 6600200), (700300, 6600200), (700300, 6600300), (700200, 6600300), (700200, 6600200)]
                ),
            ]
        },
        crs="EPSG:2154",
    )
    return points, lines, mask_hydro


def create_test_data_with_regression_failure():
    # Create GeoDataFrame with points and points_knn columns that will lead to regression failure
    points = gpd.GeoDataFrame(
        {
            "geometry": [Point(700000, 6600000), Point(700300, 6600300)],
            "points_knn": [
                [
                    (700000, 6600000, 10),
                    (700100, 6600100, 10),  # Same Z to force failure
                    (700200, 6600200, 10),  # Same Z to force failure
                    (700300, 6600300, 10),
                ],
                [
                    (700000, 6600000, 10),
                    (700100, 6600100, 10),  # Same Z to force failure
                    (700200, 6600200, 10),  # Same Z to force failure
                    (700300, 6600300, 10),
                ],
            ],
        },
        crs="EPSG:2154",
    )

    # Create a longer LineString (>150m) to represent a larger river section
    lines = gpd.GeoDataFrame(
        {
            "geometry": [
                LineString([(700000, 6600000), (700200, 6600200)]),  # Length is approximately 282.84 meters
            ]
        },
        crs="EPSG:2154",
    )

    # Create mask_hydro polygons to resemble river segments (long and narrow)
    mask_hydro = gpd.GeoDataFrame(
        {
            "geometry": [
                Polygon(
                    [(699950, 6599950), (700350, 6599950), (700350, 6600350), (699950, 6600350), (699950, 6599950)]
                ),  # A polygon resembling a river segment
            ]
        },
        crs="EPSG:2154",
    )

    return points, lines, mask_hydro


def create_test_data_with_flattening_failure():
    # Create GeoDataFrame with points and points_knn columns : the points_knn is None
    points = gpd.GeoDataFrame(
        {"geometry": [Point(700000, 6600000)], "points_knn": [np.array([])]},
        crs="EPSG:2154",
    )
    # Create a short LineString to represent a small river section (<150 meters)
    lines = gpd.GeoDataFrame(
        {
            "geometry": [
                LineString([(700000, 6600000), (700050, 6600050)]),  # Length is 70.71 meters
            ]
        },
        crs="EPSG:2154",
    )

    # Create mask_hydro polygons to resemble river segments (long and narrow)
    mask_hydro = gpd.GeoDataFrame(
        {
            "geometry": [
                Polygon(
                    [
                        (699980, 6599980),
                        (700020, 6599980),
                        (700030, 6600000),
                        (700020, 6600020),
                        (699980, 6600020),
                        (699970, 6600000),
                    ]
                ),  # A polygon resembling a river bend
            ]
        },
        crs="EPSG:2154",
    )

    return points, lines, mask_hydro


def test_lauch_virtual_points_by_section_with_geometry_only():
    points, lines, mask_hydro = create_test_data_with_geometry_only()
    crs = CRS.from_epsg(2154)
    spacing = 1.0
    output_filename = os.path.join(TMP_PATH, "mask_hydro_no_virtual_points.geojson")

    lauch_virtual_points_by_section(points, lines, mask_hydro, crs, spacing, TMP_PATH)

    assert (Path(TMP_PATH) / "mask_hydro_no_virtual_points.geojson").is_file()
    masks_without_points = gpd.read_file(output_filename)
    assert len(masks_without_points) == len(mask_hydro)


def test_lauch_virtual_points_by_section_no_points():
    points, line, mask_hydro = create_test_data_no_points()
    crs = CRS.from_epsg(2154)
    spacing = 1.0
    output_filename = os.path.join(TMP_PATH, "mask_hydro_no_virtual_points.geojson")

    lauch_virtual_points_by_section(points, line, mask_hydro, crs, spacing, TMP_PATH)

    assert (Path(TMP_PATH) / "mask_hydro_no_virtual_points.geojson").is_file()
    masks_without_points = gpd.read_file(output_filename)
    assert len(masks_without_points) == len(mask_hydro)


def test_lauch_virtual_points_by_section_with_points():
    points, lines, mask_hydro = create_test_data_with_points()
    crs = CRS.from_epsg(2154)
    spacing = 1.0

    grid_with_z = lauch_virtual_points_by_section(points, lines, mask_hydro, crs, spacing, TMP_PATH)

    assert all(isinstance(geom, Point) for geom in grid_with_z.geometry)
    assert all(geom.has_z for geom in grid_with_z.geometry)  # Check that all points have a Z coordinate


def test_lauch_virtual_points_by_section_regression_failure():
    points, lines, mask_hydro = create_test_data_with_regression_failure()
    crs = CRS.from_epsg(2154)
    spacing = 1.0
    output_filename = os.path.join(TMP_PATH, "mask_hydro_no_virtual_points_with_regression.geojson")

    lauch_virtual_points_by_section(points, lines, mask_hydro, crs, spacing, TMP_PATH)

    assert (Path(TMP_PATH) / "mask_hydro_no_virtual_points_with_regression.geojson").is_file()
    masks_without_points = gpd.read_file(output_filename)
    assert len(masks_without_points) == len(mask_hydro)


def test_lauch_virtual_points_by_section_flattening_failure():
    points, lines, mask_hydro = create_test_data_with_flattening_failure()
    crs = CRS.from_epsg(2154)
    spacing = 1.0
    output_filename = os.path.join(TMP_PATH, "mask_hydro_no_virtual_points_for_little_river.geojson")

    lauch_virtual_points_by_section(points, lines, mask_hydro, crs, spacing, TMP_PATH)

    assert (Path(TMP_PATH) / "mask_hydro_no_virtual_points_for_little_river.geojson").is_file()
    masks_without_points = gpd.read_file(output_filename)
    assert len(masks_without_points) == len(mask_hydro)
