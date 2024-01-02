import pytest
import yaml
from pathlib import Path

def test_config_filter():
    yaml_file = "./configs/filter/default.yaml"
    # Read YAML
    with open(yaml_file, "r") as file:
        data = yaml.safe_load(file)
        classes = data["keep_classes"]
        assert classes == [2]

def test_config_io():
    yaml_file = "./configs/io/default.yaml"
    # Read YAML
    with open(yaml_file, "r") as file:
        data = yaml.safe_load(file)
        spatial_ref = data["spatial_reference"]
        srid = data["srid"]
        assert spatial_ref == 'EPSG:2154' and srid == 2154


def test_config_tile_geometry():
    yaml_file = "./configs/tile_geometry/default.yaml"
    # Read YAML
    with open(yaml_file, "r") as file:
        data = yaml.safe_load(file)
        pixel = data["pixel_size"]
        no_data = data["no_data_value"]
        assert pixel == 1 and no_data == -9999



