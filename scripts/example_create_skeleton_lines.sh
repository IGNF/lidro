# For lauching create skeleton lines
python lidro/main_create_skeleton_lines.py \
io.skeleton.mask_input_path=[input_filepath] \
io.skeleton.global_lines_output_path=[output_filepath] \
skeleton.db_uni.db_user=[user_name] \
"skeleton.db_uni.db_password=[password]" \
io.skeleton.skeleton_lines_output_path=[out_filepath(optional)] \
io.skeleton.gap_lines_output_path=[out_filepath(optional)]

# io.skeleton.mask_input_path : input path to the .geojson with the water masks
# io.skeleton.global_lines_output_path : output path for all the skeletons
# skeleton.db_uni.db_user : username for "bduni_france_consultation"
# skeleton.db_uni.db_password : password for "bduni_france_consultation". WARNING ! If there is a special character in the password,
# the line must be written like this : "skeleton.db_uni.db_password='$tr@ng€_ch@r@ct€r$'" (note the " and the ')
# io.skeleton.skeleton_lines_output_path : (optional) output path for only the skeleton inside water beds defined by the input masks
# io.skeleton.gap_lines_output_path : (optional) output path for only the lines between water beds defined by the input masks