# For lauching Mask Hydro
python -m lidro.main_create_mask \
io.input_dir=./data/pointcloud/ \
io.output_dir=./tmp/ \
mask_generation.raster.dilatation_size=3 \
mask_generation.filter.keep_classes="[0, 1, 2, 3, 4, 5, 6, 17, 64, 65, 66, 67]" \ 


