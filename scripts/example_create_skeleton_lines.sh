# For running create skeleton lines
python lidro/main_create_skeleton_lines.py \
io.skeleton.mask_input_path=[input_filepath] \
skeleton.db_uni.db_user=[user_name] \
"skeleton.db_uni.db_password=[password]" \
io.skeleton.skeleton_lines_output_path=[out_filepath(optional)] \
io.skeleton.gap_lines_output_path=[out_filepath(optional)] \
io.skeleton.global_lines_output_path=[output_filepath(optional)]

# example for running create skeleton lines and get only the skeletons lines corresponding to the water beds
python lidro/main_create_skeleton_lines.py \
io.skeleton.mask_input_path=[input_filepath] \
skeleton.db_uni.db_using_db=False \
io.skeleton.skeleton_lines_output_path=[out_filepath]
# as the database is only used to check the presence of bridges, we can deactivate if with "skeleton.db_uni.db_using_db=False", and no login/password
