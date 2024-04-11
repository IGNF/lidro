import os
import subprocess as sp
from pathlib import Path

import pytest
from hydra import compose, initialize

from lidro.main import main

INPUT_DIR = Path("data") / "pointcloud"
OUTPUT_DIR = Path("tmp") / "main"


def setup_module(module):
    os.makedirs("tmp/main", exist_ok=True)


def test_main_run_okay():
    repo_dir = Path.cwd().parent
    cmd = f"""python -m lidro.main \
        io.input_dir="{repo_dir}/lidro/data/pointcloud/"\
        io.output_dir="{repo_dir}/lidro/tmp/main/"
        """
    sp.run(cmd, shell=True, check=True)


def test_main_lidro_default():
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR / "main_lidro_default"
    pixel_size = 1
    tile_size = 1000
    srid = 2154
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.input_dir={input_dir}",
                f"io.output_dir={output_dir}",
                f"io.pixel_size={pixel_size}",
                f"io.tile_size={tile_size}",
                f"io.srid={srid}",
            ],
        )
    main(cfg)
    assert (Path(output_dir) / "MaskHydro_LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.GeoJSON").is_file()


def test_main_lidro_input_file():
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR / "main_lidro_input_file"
    input_filename = "LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"
    pixel_size = 1
    tile_size = 1000
    srid = 2154
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.input_filename={input_filename}",
                f"io.input_dir={input_dir}",
                f"io.output_dir={output_dir}",
                f"io.pixel_size={pixel_size}",
                f"io.tile_size={tile_size}",
                f"io.srid={srid}",
            ],
        )
    main(cfg)
    assert (Path(output_dir) / "MaskHydro_LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.GeoJSON").is_file()


def test_main_lidro_fail_no_input_dir():
    output_dir = OUTPUT_DIR / "main_no_input_dir"
    pixel_size = 1
    tile_size = 1000
    srid = 2154
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.output_dir={output_dir}",
                f"io.pixel_size={pixel_size}",
                f"io.tile_size={tile_size}",
                f"io.srid={srid}",
            ],
        )
    with pytest.raises(ValueError):
        main(cfg)


def test_main_lidro_fail_wrong_input_dir():
    output_dir = OUTPUT_DIR / "main_wrong_input_dir"
    pixel_size = 1
    tile_size = 1000
    srid = 2154
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                "io.input_dir=some_random_input_dir",
                f"io.output_dir={output_dir}",
                f"io.pixel_size={pixel_size}",
                f"io.tile_size={tile_size}",
                f"io.srid={srid}",
            ],
        )
    with pytest.raises(FileNotFoundError):
        main(cfg)


def test_main_lidro_fail_no_output_dir():
    input_dir = INPUT_DIR
    pixel_size = 1
    tile_size = 1000
    srid = 2154
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.input_dir={input_dir}",
                f"io.pixel_size={pixel_size}",
                f"io.tile_size={tile_size}",
                f"io.srid={srid}",
            ],
        )
    with pytest.raises(ValueError):
        main(cfg)
