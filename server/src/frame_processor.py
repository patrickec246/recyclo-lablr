import os
import json

from utils import *
from annotations import *
from settings import *

import shutil

# global aggregator
aggregator = AnnotationAggregator()

# return a list of directories of adequately labeled images,
# along with the json files (labels) in the directory
def find_saturated_frames(num_annotations):
	all_uuids = glob.glob(os.path.join(UNLABELED_DATA_PATH, '*', ''))
	uuids = [{'uuid' : os.path.basename(os.path.normpath(x)), 'path' : os.path.normpath(x)} for x in all_uuids]

	saturated_frames = []
	for root, dirs, files in os.walk(UNLABELED_DATA_PATH):
		json_files = [j for j in files if j.endswith('.json') and j is not 'metadata.json']
		if len(json_files) >= num_annotations:
			saturated_frames.append({'dir' : root, 'json_files' : json_files})

	return saturated_frames

# for all frames which have been adequately labeled,
# merge their labels and add the final label to the final dataset
def complete_saturated_frames(num_annotations=1):
	saturated_frames = find_saturated_frames(num_annotations)

	for frame in saturated_frames:
		json_files = [os.path.join(frame['dir'], json_file) for json_file in frame['json_files']]

		frame_no = os.path.basename(frame['dir'])
		uuid = os.path.split(os.path.split(frame['dir'])[0])[1]

		# For each frame, gather up all labeled 'versions' and combine into a single label
		aggregator.load_annotations(json_files)
		aggregated_label = aggregator.aggregate()

		# Construct the output content
		json_obj = {k:v for k,v in read_video_metadata(uuid).items()}
		json_obj['labels'] = aggregated_label
		json_obj['img_data'] = convert_img_to_base64(os.path.join(frame['dir'], 'frame.jpg'), quality=100)
		json_obj['src_id'] = uuid

		target_file_dir = os.path.join(LABELED_DATA_PATH, uuid)
		if not os.path.exists(target_file_dir):
			os.mkdir(target_file_dir)

		# The frame and its labels can now be written to target_file
		target_file = os.path.join(target_file_dir, '{}.json'.format(frame_no))
		with open(target_file, 'w+') as f:
			f.write(json.dumps(json_obj, indent=4, sort_keys=True))
			shutil.rmtree(frame['dir'])

		log('Merged annotations for frame: {}'.format(frame))

# once a directory is empty (except for the metadata file), clean it up
def cleanup_completed_videos():
	for file in glob.glob(os.path.join(UNLABELED_DATA_PATH, '*', '')):
		dir_files = glob.glob(os.path.join(file, '*'))
		if len(dir_files) == 1 and os.path.basename(dir_files[0]) == 'metadata.json':
			log('Deleting video: {}'.format(file))
			shutil.rmtree(file)

