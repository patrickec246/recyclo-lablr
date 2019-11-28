import cv2
import os
import uuid
import json
import glob

raw_root = 'data/raw'
labaled_root = 'data/labeled'
unlabeled_root = 'data/unlabeled'

def load_frame_annotations(uuid, frame, frame_dir=unlabeled_root):
    js = []

    annotation_dir = os.path.join(frame_dir, uuid, str(frame), '*.json')

    for annotation in glob.glob(annotation_dir):
        with open(annotation, 'r') as f:
            js.append(json.loads(f.read()))

    return js

def process_video(video_path, frame_output_dir, delete_after_processing=False):
    frames = convert_video_to_frames(video_path)

    if not frames:
        return None

    if not os.path.exists(frame_output_dir):
        os.mkdir(frame_output_dir)

    dir_name = uuid.uuid4().hex
    path_name = os.path.join(frame_output_dir, dir_name)
    os.mkdir(path_name)

    for i, frame in frames:
        annotation_path = os.path.join(path_name, str(i))
        os.mkdir(annotation_path)
        frame_path = os.path.join(annotation_path, '{}.jpg'.format(i))
        cv2.imwrite(frame_path, frame)
        create_annotation_template(annotation_path, i)

    return path_name

def create_annotation_template(annotation_path, frame):
    template_json = {}
    template_json['shapes'] = []

    with open(os.path.join(annotation_path, '{}.json'.format(frame)), 'w+') as f:
        f.write(json.dumps(template_json))

def convert_video_to_frames(video_path):
    if not os.path.exists(video_path):
        return None

    output = []

    video = cv2.VideoCapture(video_path)
    r, frame = video.read()
    i = 0

    while r:
        output.append((i, frame))
        r, frame = video.read()
        i += 1

    return output

'''
 Utils for server functionality
'''
