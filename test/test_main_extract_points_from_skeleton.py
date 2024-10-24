import os
import subprocess as sp
from pathlib import Path

import pytest
from hydra import compose, initialize

from lidro.main_extract_points_from_skeleton import main

INPUT_DIR = Path("data/tile_0830_6291")
OUTPUT_DIR = Path("tmp") / "main_extract_points_around_skeleton"


def setup_module(module):
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_main_run_okay():

    cmd = f"""python -m lidro.main_extract_points_from_skeleton \
        io.input_dir={INPUT_DIR}\
        io.input_filename=Semis_2021_0830_6291_LA93_IGN69.laz \
        io.input_mask_hydro="{INPUT_DIR}/mask_hydro_merge/MaskHydro_merge.geojson"\
        io.input_skeleton="{INPUT_DIR}/skeleton/skeleton_hydro.geojson"\
        io.output_dir={OUTPUT_DIR}
        """
    sp.run(cmd, shell=True, check=True)


def test_main_extract_points_skeleton_input_file():
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR / "main_extract_points_skeleton_input_file"
    input_filename = "Semis_2021_0830_6291_LA93_IGN69.laz"
    input_mask_hydro = INPUT_DIR / "mask_hydro_merge/MaskHydro_merge.geojson"
    input_skeleton = INPUT_DIR / "skeleton/skeleton_hydro.geojson"
    distances_meters = 5
    buffer = 2
    srid = 2154
    k = 10
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.input_filename={input_filename}",
                f"io.input_dir={input_dir}",
                f"io.output_dir={output_dir}",
                f"io.input_mask_hydro={input_mask_hydro}",
                f"io.input_skeleton={input_skeleton}",
                f"virtual_point.vector.distance_meters={distances_meters}",
                f"virtual_point.vector.buffer={buffer}",
                f"virtual_point.vector.k={k}",
                f"io.srid={srid}",
            ],
        )
    main(cfg)
    assert (Path(output_dir) / "Semis_2021_0830_6291_LA93_IGN69_points_skeleton.geojson").is_file()


def test_main_extract_points_skeleton_fail_no_input_dir():
    output_dir = OUTPUT_DIR / "main_no_input_dir"
    input_mask_hydro = INPUT_DIR / "mask_hydro_merge/MaskHydro_merge.geojson"
    input_skeleton = INPUT_DIR / "skeleton/skeleton_hydro.geojson"
    distances_meters = 5
    buffer = 2
    srid = 2154
    k = 10
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.input_mask_hydro={input_mask_hydro}",
                f"io.input_skeleton={input_skeleton}",
                f"io.output_dir={output_dir}",
                f"virtual_point.vector.distance_meters={distances_meters}",
                f"virtual_point.vector.buffer={buffer}",
                f"virtual_point.vector.k={k}",
                f"io.srid={srid}",
            ],
        )
    with pytest.raises(ValueError):
        main(cfg)


def test_main_extract_points_skeleton_fail_wrong_input_dir():
    output_dir = OUTPUT_DIR / "main_wrong_input_dir"
    input_mask_hydro = INPUT_DIR / "mask_hydro_merge/MaskHydro_merge.geojson"
    input_skeleton = INPUT_DIR / "skeleton/skeleton_hydro.geojson"
    distances_meters = 5
    buffer = 2
    srid = 2154
    k = 10
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                "io.input_dir=some_random_input_dir",
                f"io.input_mask_hydro={input_mask_hydro}",
                f"io.input_skeleton={input_skeleton}",
                f"io.output_dir={output_dir}",
                f"virtual_point.vector.distance_meters={distances_meters}",
                f"virtual_point.vector.buffer={buffer}",
                f"virtual_point.vector.k={k}",
                f"io.srid={srid}",
            ],
        )
    with pytest.raises(FileNotFoundError):
        main(cfg)


def test_main_extract_points_skeleton_fail_no_output_dir():
    input_dir = INPUT_DIR
    input_mask_hydro = INPUT_DIR / "mask_hydro_merge/MaskHydro_merge.geojson"
    input_skeleton = INPUT_DIR / "skeleton/skeleton_hydro.geojson"
    distances_meters = 5
    buffer = 2
    srid = 2154
    k = 10
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.input_dir={input_dir}",
                f"io.input_mask_hydro={input_mask_hydro}",
                f"io.input_skeleton={input_skeleton}",
                f"virtual_point.vector.distance_meters={distances_meters}",
                f"virtual_point.vector.buffer={buffer}",
                f"virtual_point.vector.k={k}",
                f"io.srid={srid}",
            ],
        )
    with pytest.raises(ValueError):
        main(cfg)


def test_main_extract_points_skeleton_fail_no_input_mask_hydro():
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR / "main_no_input_dir"
    input_skeleton = INPUT_DIR / "skeleton/skeleton_hydro.geojson"
    distances_meters = 5
    buffer = 2
    srid = 2154
    k = 10
    with initialize(version_base="1.2", config_path="../configs"):
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.input_dir={input_dir}",
                f"io.output_dir={output_dir}",
                "io.input_mask_hydro=some_random_input_mask_hydro",
                f"io.input_skeleton={input_skeleton}",
                f"virtual_point.vector.distance_meters={distances_meters}",
                f"virtual_point.vector.buffer={buffer}",
                f"virtual_point.vector.k={k}",
                f"io.srid={srid}",
            ],
        )
    with pytest.raises(ValueError):
        main(cfg)


def test_main_extract_points_skeleton_fail_no_input_skeleton():
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR / "main_no_input_dir"
    input_mask_hydro = INPUT_DIR / "mask_hydro_merge/MaskHydro_merge.geojson"
    distances_meters = 5
    buffer = 2
    srid = 2154
    k = 10
    with initialize(version_base="1.2", config_path="../configs"):
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.input_dir={input_dir}",
                f"io.output_dir={output_dir}",
                f"io.input_mask_hydro={input_mask_hydro}",
                "io.input_skeleton=some_random_input_skeleton",
                f"virtual_point.vector.distance_meters={distances_meters}",
                f"virtual_point.vector.buffer={buffer}",
                f"virtual_point.vector.k={k}",
                f"io.srid={srid}",
            ],
        )
    with pytest.raises(ValueError):
        main(cfg)
