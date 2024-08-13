# For lauching create skeleton lines
python lidro/main_create_skeleton_lines.py \
skeleton.file_path.mask_input_path=[input_filepath] \
skeleton.file_path.global_lines_output_path=[output_filepath] \
skeleton.db_uni.db_user=[user_name] \
"skeleton.db_uni.db_password=[password]" \
skeleton.file_path.skeleton_lines_ouput_path=[out_filepath(optional)] \
skeleton.file_path.gap_lines_ouput_path=[out_filepath(optional)]

# skeleton.file_path.mask_input_path : input path to the .geojson with the water masks
# skeleton.file_path.global_lines_output_path : output path for all the skeletons
# skeleton.db_uni.db_user : username for "bduni_france_consultation"
# skeleton.db_uni.db_password : password for "bduni_france_consultation". WARNING ! If there is a special character in the password,
# the line must be written like this : "skeleton.db_uni.db_password='$tr@ng€_ch@r@ct€r$'" (note the " and the ')
# skeleton.file_path.skeleton_lines_ouput_path : (optional) output path for only the skeleton inside water beds defined by the input masks
# skeleton.file_path.gap_lines_ouput_path : (optional) output path for only the lines between water beds defined by the input masks