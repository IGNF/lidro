# For lauching Mask Hydro
python -m lidro.main_create_mask \
io.input_dir=./data/pointcloud/ \
io.output_dir=./tmp/ \
#io.mask_generation.raster.dilatation_size=3 \ #size for dilatation
#io.mask_generation.filter.keep_classes=[0, 1, 2, 3, 4, 5, 6, 17, 64, 65, 66, 67] \ #Classes to be considered as "non-water"



