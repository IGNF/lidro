import os
import shutil
import subprocess as sp
from pathlib import Path

import pytest
from hydra import compose, initialize

from lidro.main_create_mask import main

DATA_DIR = Path("data/tile_0830_6291")
INPUT_DIR = DATA_DIR / "pointcloud"
OUTPUT_DIR = Path("tmp") / "main_create_mask"


def setup_module(module):
    if OUTPUT_DIR.is_dir():
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_main_run_okay():
    cmd = f"""python -m lidro.main_create_mask \
        io.input_dir={INPUT_DIR}\
        io.output_dir={OUTPUT_DIR}
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
    assert (Path(output_dir) / "MaskHydro_Semis_2021_0830_6291_LA93_IGN69.GeoJSON").is_file()


def test_main_lidro_input_file():
    input_dir = Path("data/other/pointcloud")
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
