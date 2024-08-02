# For lauching create skeleton lines
python lidro/main_create_skeleton_lines.py \
SKELETON.FILE_PATH.MASK_INPUT_PATH=[input_filepath] \
SKELETON.FILE_PATH.GLOBAL_LINES_OUTPUT_PATH=[output_filepath] \
SKELETON.DB_UNI.DB_USER=[user_name] \
"SKELETON.DB_UNI.DB_PASSWORD=[password]" \
SKELETON.FILE_PATH.SKELETON_LINES_OUTPUT_PATH=[out_filepath(optional)] \
SKELETON.FILE_PATH.GAP_LINES_OUTPUT_PATH=[out_filepath(optional)]

# SKELETON.FILE_PATH.MASK_INPUT_PATH : input path to the .geojson with the water masks
# SKELETON.FILE_PATH.GLOBAL_LINES_OUTPUT_PATH : output path for all the skeletons
# SKELETON.DB_UNI.DB_USER : username for "bduni_france_consultation"
# SKELETON.DB_UNI.DB_PASSWORD : password for "bduni_france_consultation". WARNING ! If there is a special character in the password,
# the line must be written like this : "SKELETON.DB_UNI.DB_PASSWORD='$tr@ng€_ch@r@ct€r$'" (note the " and the ')
# SKELETON.FILE_PATH.SKELETON_LINES_OUTPUT_PATH : (optional) output path for only the skeleton inside water beds defined by the input masks
# SKELETON.FILE_PATH.GAP_LINES_OUTPUT_PATH : (optional) output path for only the lines between water beds defined by the input masks