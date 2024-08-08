# For lauching Mask Hydro merged
python -m lidro.main_merge_mask \
io.input_dir=./data/mask_hydro/ \
io.output_dir=./tmp/merge_mask_hydro/ \
#io.mask_generation.vector.min_water_area=150 \ #Filter water's area (m²)
#io.mask_generation.vector.buffer_positive=1 \ #Parameters for buffer
#io.mask_generation.vector.buffer_negative=-1.5 \ #Parameters for buffer
#io.mask_generation.vector.tolerance=1 \ # Tolerance from Douglas-Peucker : simplify mask hydro



