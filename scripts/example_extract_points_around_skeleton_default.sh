# Launch hydro mask merging
python -m lidro.main_extract_points_from_skeleton \
io.input_dir=./data/ \
io.input_mask_hydro=./data/merge_mask_hydro/MaskHydro_merge.geosjon \
io.input_skeleton=./data/skeleton_hydro/Skeleton_Hydro_multibranch.geojson \
io.output_dir=./tmp/points_skeleton/ \
virtual_point.vector.distance_meters=5 \
virtual_point.vector.buffer=3 \
virtual_point.vector.k=3 \
virtual_point.filter.keep_neighbors_classes="[2, 9]" \



