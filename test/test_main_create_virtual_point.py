import os
import subprocess as sp
from pathlib import Path

import pytest
from hydra import compose, initialize

from lidro.main_create_virtual_point import main

INPUT_DIR = Path("data")
OUTPUT_DIR = Path("tmp") / "create_virtual_point/main"


def setup_module(module):
    os.makedirs("tmp/create_virtual_point/main", exist_ok=True)


def test_main_run_okay():
    repo_dir = Path.cwd().parent
    cmd = f"""python -m lidro.main_create_virtual_point \
        io.input_dir="{repo_dir}/lidro/data/"\
        io.input_filename=Semis_2021_0830_6291_LA93_IGN69.laz \
        io.input_mask_hydro="{repo_dir}/lidro/data/merge_mask_hydro/MaskHydro_merge.geojson"\
        io.input_skeleton="{repo_dir}/lidro/data/skeleton_hydro/Skeleton_Hydro.geojson"\
        io.output_dir="{repo_dir}/lidro/tmp/create_virtual_point/main/"
        """
    sp.run(cmd, shell=True, check=True)


def test_main_lidro_default():
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR / "main_lidro_default"
    input_mask_hydro = INPUT_DIR / "merge_mask_hydro/MaskHydro_merge.geojson"
    input_skeleton = INPUT_DIR / "skeleton_hydro/Skeleton_Hydro.geojson"
    distances_meters = 10
    buffer = 10
    srid = 2154
    k = 20

    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
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
    assert (Path(output_dir) / "Points_Skeleton.GeoJSON").is_file()


def test_main_lidro_input_file():
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR / "main_lidro_input_file"
    input_filename = "Semis_2021_0830_6291_LA93_IGN69.laz"
    input_mask_hydro = INPUT_DIR / "merge_mask_hydro/MaskHydro_merge.geojson"
    input_skeleton = INPUT_DIR / "skeleton_hydro/Skeleton_Hydro.geojson"
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
    assert (Path(output_dir) / "Points_Skeleton.GeoJSON").is_file()


def test_main_lidro_fail_no_input_dir():
    output_dir = OUTPUT_DIR / "main_no_input_dir"
    input_mask_hydro = INPUT_DIR / "merge_mask_hydro/MaskHydro_merge.geojson"
    input_skeleton = INPUT_DIR / "skeleton_hydro/Skeleton_Hydro.geojson"
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


def test_main_lidro_fail_wrong_input_dir():
    output_dir = OUTPUT_DIR / "main_wrong_input_dir"
    input_mask_hydro = INPUT_DIR / "merge_mask_hydro/MaskHydro_merge.geojson"
    input_skeleton = INPUT_DIR / "skeleton_hydro/Skeleton_Hydro.geojson"
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


def test_main_lidro_fail_no_output_dir():
    input_dir = INPUT_DIR
    input_mask_hydro = INPUT_DIR / "merge_mask_hydro/MaskHydro_merge.geojson"
    input_skeleton = INPUT_DIR / "skeleton_hydro/Skeleton_Hydro.geojson"
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


def test_main_lidro_fail_no_input_mask_hydro():
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR / "main_no_input_dir"
    input_skeleton = INPUT_DIR / "skeleton_hydro/Skeleton_Hydro.geojson"
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


def test_main_lidro_fail_no_input_skeleton():
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR / "main_no_input_dir"
    input_mask_hydro = INPUT_DIR / "merge_mask_hydro/MaskHydro_merge.geojson"
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
