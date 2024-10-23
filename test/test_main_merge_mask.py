import os
import subprocess as sp
from pathlib import Path

import pytest
from hydra import compose, initialize

from lidro.main_merge_mask import main

INPUT_DIR = Path("data/tile_0830_6291")
OUTPUT_DIR = Path("tmp") / "main_merge_mask_hydro"


def setup_module(module):
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_main_run_okay():
    cmd = f"""python -m lidro.main_merge_mask \
        io.input_dir="{INPUT_DIR}/mask_hydro_merge/"\
        io.output_dir="{OUTPUT_DIR}/main_run_ok"
        """
    sp.run(cmd, shell=True, check=True)


def test_main_lidro_fail_no_input_dir():
    output_dir = OUTPUT_DIR / "main_no_input_dir"
    pixel_size = 1
    min_water_area = 150
    buffer_positive = 0.5
    buffer_negative = -1.5
    tolerance = 1
    srid = 2154
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.output_dir={output_dir}",
                f"io.pixel_size={pixel_size}",
                f"mask_generation.vector.min_water_area={min_water_area}",
                f"mask_generation.vector.buffer_positive={buffer_positive}",
                f"mask_generation.vector.buffer_negative={buffer_negative}",
                f"mask_generation.vector.tolerance={tolerance}",
                f"io.srid={srid}",
            ],
        )
    with pytest.raises(ValueError):
        main(cfg)


def test_main_lidro_fail_wrong_input_dir():
    output_dir = OUTPUT_DIR / "main_wrong_input_dir"
    pixel_size = 1
    min_water_area = 150
    buffer_positive = 0.5
    buffer_negative = -1.5
    tolerance = 1
    srid = 2154
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                "io.input_dir=some_random_input_dir",
                f"io.output_dir={output_dir}",
                f"io.pixel_size={pixel_size}",
                f"mask_generation.vector.min_water_area={min_water_area}",
                f"mask_generation.vector.buffer_positive={buffer_positive}",
                f"mask_generation.vector.buffer_negative={buffer_negative}",
                f"mask_generation.vector.tolerance={tolerance}",
                f"io.srid={srid}",
            ],
        )
    with pytest.raises(FileNotFoundError):
        main(cfg)


def test_main_lidro_fail_no_output_dir():
    input_dir = INPUT_DIR / "mask_hydro_merge"
    pixel_size = 1
    min_water_area = 150
    buffer_positive = 0.5
    buffer_negative = -1.5
    tolerance = 1
    srid = 2154
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.input_dir={input_dir}",
                f"io.pixel_size={pixel_size}",
                f"mask_generation.vector.min_water_area={min_water_area}",
                f"mask_generation.vector.buffer_positive={buffer_positive}",
                f"mask_generation.vector.buffer_negative={buffer_negative}",
                f"mask_generation.vector.tolerance={tolerance}",
                f"io.srid={srid}",
            ],
        )
    with pytest.raises(ValueError):
        main(cfg)
