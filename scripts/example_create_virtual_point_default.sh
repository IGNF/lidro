# Launch hydro mask merging
python -m lidro.main_create_virtual_point \
io.input_dir=./data/ \
io.input_mask_hydro=./data/merge_mask_hydro/MaskHydro_merge.geojson \
io.input_skeleton=./data/skeleton_hydro/Skeleton_Hydro.geojson \
io.output_dir=./tmp/ \
#io.virtual_point.vector.s=0.5 \ #Spacing between the grid points in meters



