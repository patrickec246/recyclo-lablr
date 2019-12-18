import os
import json

from utils import *
from annotations import *
from settings import *

import shutil

aggregator = AnnotationAggregator()

def get_unlabeled_frames():
	unlabeled_frames = glob.glob(os.path.join(unlabeled_root, '*', '*', ''))
	return {'unlabeled_frames' : unlabeled_frames, 'num_unlabeled_frames' : len(unlabeled_frames)}

def find_saturated_frames(num_annotations):
	all_uuids = glob.glob(os.path.join(unlabeled_root, '*', ''))
	uuids = [{'uuid' : os.path.basename(os.path.normpath(x)), 'path' : os.path.normpath(x)} for x in all_uuids]

	saturated_frames = []
	for root, dirs, files in os.walk(unlabeled_root):
		jsons = [j for j in files if '.json' in j and 'metadata' not in j]
		if len(jsons) >= num_annotations:
			saturated_frames.append({'dir' : root, 'jsons' : jsons})

	return saturated_frames

def complete_saturated_frames(num_annotations=2):
	saturated_frames = find_saturated_frames(num_annotations)

	for frame in saturated_frames:
		json_files = [os.path.join(frame['dir'], j) for j in frame['jsons']]

		frame_no = os.path.basename(frame['dir'])
		uuid = os.path.split(os.path.split(frame['dir'])[0])[1]

		aggregator.load_annotations(json_files)
		aggregated_label = aggregator.aggregate()

		json_obj = {}
		json_obj['labels'] = aggregated_label
		json_obj['img_data'] = convert_img_to_base64(os.path.join(frame['dir'], 'frame.jpg'), quality=100)
		json_obj['src_id'] = uuid
		for k,v in read_video_metadata(uuid).items():
			json_obj[k] = v

		completed_frame = json.dumps(json_obj, indent=4, sort_keys=True)

		target_file_dir = os.path.join(labeled_root, uuid)
		if not os.path.exists(target_file_dir):
			os.mkdir(target_file_dir)

		target_file = os.path.join(target_file_dir, '{}.json'.format(frame_no))

		with open(target_file, 'w+') as f:
			f.write(completed_frame)
			shutil.rmtree(frame['dir'])

		log('Merged annotations for frame: {}'.format(frame))

def cleanup_completed_videos():
	videos = []

	for file in glob.glob(os.path.join(unlabeled_root, '*', '')):
		dir_files = glob.glob(os.path.join(file, '*'))
		if len(dir_files) == 1 and os.path.basename(dir_files[0]) == 'metadata.json':
			log('Deleting video: {}'.format(file))
			shutil.rmtree(file)
		videos.append(file)

	return videos

complete_saturated_frames()