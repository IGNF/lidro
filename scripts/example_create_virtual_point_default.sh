# Launch hydro mask merging
python -m lidro.main_create_virtual_point \
io.input_dir=./data/ \
io.input_mask_hydro=./data/merge_mask_hydro/dataset_1/MaskHydro_merge_with_multibranch_skeleton.geojson \
io.input_skeleton=./data/skeleton_hydro/Skeleton_Hydro_multibranch.geojson \
io.dir_points_skeleton=./tmp/point_skeleton/ \
io.output_dir=./tmp/ \
virtual_point.pointcloud.points_grid_spacing=0.5 \



