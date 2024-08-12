# Launch hydro mask merging
python -m lidro.main_create_virtual_point \
io.input_dir=./data/ \
io.input_mask_hydro=./data/merge_mask_hydro/MaskHydro_merge.geosjon \
io.input_skeleton=./data/skeleton_hydro/Skeleton_Hydro.geojson \
io.output_dir=./tmp/points_skeleton/ \
#io.virtual_point.filter.keep_neighbors_classes=[2, 9] \ #Keep ground and water pointclouds between Hydro Mask and Hydro Mask buffer
#io.virtual_point.vector.distance_meters=5 \ # distance in meters between 2 consecutive points from Skeleton Hydro
#io.virtual_point.vector.buffer=3 \ #buffer for searching the points classification (default. "3") of the input LAS/LAZ file
#io.virtual_point.vector.k=3 \ #the number of nearest neighbors to find with KNeighbors



