# Launch hydro mask merging
python -m lidro.main_create_virtual_point \
io.input_dir=./data/ \
io.input_mask_hydro=./data/merge_mask_hydro/MaskHydro_merge.geojson \
io.input_skeleton=./data/skeleton_hydro/Skeleton_Hydro.geojson \
io.dir_points_skeleton=./tmp/point_skeleton/ \
io.output_dir=./tmp/ \
virtual_point.pointcloud.points_grid_spacing=0.5 \



