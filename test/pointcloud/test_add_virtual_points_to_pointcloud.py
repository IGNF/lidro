import os
import shutil
from pathlib import Path

import pdal
import pytest
from shapely.geometry import Polygon

# Import the function to test
from lidro.create_virtual_point.pointcloud.add_virtual_points_to_pointcloud import (
    add_virtual_points_by_tiles,
)

# Path to temporary directory for output files
TMP_PATH = Path("./tmp/virtual_points/pointcloud/add_virtual_points_by_tiles")


def setup_module():
    """Setup function to ensure the temporary directory is clean before tests."""
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


@pytest.fixture
def mock_input_files():
    """Fixture providing mock input files for testing."""
    return {
        "input_file": "./data/point_virtual/virtual_points.laz",
        "input_las": "./data/pointcloud/Semis_2021_0830_6291_LA93_IGN69.laz",
        "output_laz_file": str(TMP_PATH / "output_0830_6291_with_virtual_points.laz"),
        "geom": Polygon(
            [
                (830000.0, 6290000.0),
                (831000.0, 6290000.0),
                (831000.0, 6291000.0),
                (830000.0, 6291000.0),
                (830000.0, 6290000.0),
            ]
        ),
    }


def test_add_virtual_points_by_tiles_success(mock_input_files):
    """Test the function with valid input files and ensure the output is created."""
    add_virtual_points_by_tiles(**mock_input_files)

    # Verify that the output file is created
    assert os.path.exists(mock_input_files["output_laz_file"]), "Output LAZ file should be created."


def test_output_laz_file_format(mock_input_files):
    """Test that the output file is in the correct LAZ format."""
    add_virtual_points_by_tiles(**mock_input_files)

    # Check that the output file exists
    output_file = mock_input_files["output_laz_file"]
    assert os.path.exists(output_file), "Output LAZ file should be created."

    # Verify the format using PDAL
    pipeline = pdal.Pipeline(
        f"""
    [
        {{"type": "readers.las", "filename": "{output_file}"}}
    ]
    """
    )
    pipeline.execute()

    # Check if the point count is greater than 0, meaning the output is valid
    point_count = pipeline.metadata["metadata"]["readers.las"]["count"]

    assert point_count > 0, "The output LAZ file should contain points."
