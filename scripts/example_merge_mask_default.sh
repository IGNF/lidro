# For lauching Mask Hydro merged
python -m lidro.main_merge_mask \
io.input_dir=./data/mask_hydro_merge/ \
io.output_dir=./tmp/merge_mask_hydro/ \
mask_generation.vector.min_water_area=150 \
mask_generation.vector.buffer_positive=1 \
mask_generation.vector.buffer_negative=-1.5 \
mask_generation.vector.tolerance=1 \



