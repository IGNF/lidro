# For lauching Mask Hydro merged
python -m lidro.main_merge_mask \
io.input_dir=./data/mask_hydro/ \
io.output_dir=./tmp/merge_mask_hydro/ \
io.mask_generation.vector.min_water_area=150 \
io.mask_generation.vector.buffer_positive=1 \
io.mask_generation.vector.buffer_negative=-1.5 \
io.mask_generation.vector.tolerance=1 \



