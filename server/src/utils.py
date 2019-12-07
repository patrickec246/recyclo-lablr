import cv2
import os
import uuid
import json
import glob
import pyexifinfo
import datetime
import base64
import random

from settings import *

from io import StringIO, BytesIO
from PIL import Image

logs_root = 'logs'
data_root = 'data'
raw_root = 'data/raw'
labeled_root = 'data/labeled'
unlabeled_root = 'data/unlabeled'

'''
 This is going to take some massaging to fine tune but this works... ok...
'''
def calculate_average_annotations(annotations, iou_thresh=.75):
    if len(annotations) > 0:
        return annotations[0]

    shapes = {}
    for annotation in annotations:
        shape_map = {}

        for shape in annotation['shapes']:
            label = shape['label']
            producer = shape['producer']
            qualities = shape['qualifiers']
            points = shape['points']

            if label not in shape_map:
                shape_map[label] = [points]
            else:
                shape_map[label].append(points)

        annotation_list = {}
        for label, proposed_points in shape_map.items():
            sorted_points = [sort_points_cw(point_list) for point_list in proposed_points]

            avg_points = []
            n = 0
            points_per_poly = 4

            for shape_points in sorted_points:
                for i in range(points_per_poly):
                    avg_points[i] += shape_points[i]

            if calc_iou(shape_map[label]['points'], sorted_points) >= iou_thresh:
                shapes[label].merge(sorted_points)
    return shapes

def load_frame_annotations(uuid, frame, frame_dir=unlabeled_root):
    js = []

    annotation_dir = os.path.join(frame_dir, uuid, str(frame), '*.json')

    for annotation in glob.glob(annotation_dir):
        with open(annotation, 'r') as f:
            js.append(json.loads(f.read()))

    return js

def pick_random_video():
    valid_videos = [x for x in glob.glob(os.path.join(raw_root, '*')) if 'MOV' in x]
    return random.choice(valid_videos) if len(valid_videos) > 0 else None

def process_video(video_path, frame_output_dir=unlabeled_root, delete_after_processing=False):
    log('Attempting to process video {}'.format(video_path))
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
        frame_path = os.path.join(annotation_path, 'frame.jpg')
        cv2.imwrite(frame_path, frame)

    metadata = get_video_metadata(video_path)
    metadata_path = os.path.join(path_name, 'metadata.json')

    with open(metadata_path, 'w+') as f:
        f.write(json.dumps(metadata, indent=4, sort_keys=True))

    if delete_after_processing:
        log('Converted {} to individual frames. Deleting source video')
        os.remove(video_path)

    return path_name

def convert_video_to_frames(video_path):
    if not os.path.exists(video_path):
        return None

    output = []

    log('Converting video to frames: {}'.format(video_path))

    video = cv2.VideoCapture(video_path)
    r, frame = video.read()
    i = 0

    while r:
        output.append((i, frame))
        r, frame = video.read()
        i += 1

    return output

def get_video_metadata(file_path):
    exifinfo = pyexifinfo.get_json(file_path)[0]

    gps = exifinfo['QuickTime:GPSCoordinates']
    mktime = exifinfo['QuickTime:CreationDate']

    args = gps.split(',')
    latitude = args[0].strip()
    longitude = args[1].strip()
    elevation = args[2].strip()

    utcmktime = datetime.datetime.strptime(mktime, '%Y:%m:%d %H:%M:%S%z').strftime("%a %b %d %Y %H:%M:%S %Z")

    return {'latitude':latitude, 'longitude':longitude, 'elevation':elevation, 'creationtime':utcmktime}

def read_video_metadata(uuid):
    metadata_file = os.path.join(unlabeled_root, uuid, 'metadata.json')

    if not os.path.exists(metadata_file):
        return None

    with open(metadata_file) as f:
        return json.loads(f.read())

def convert_img_to_base64(img_path, quality=70):
    if not os.path.exists(img_path):
        return None

    buf = BytesIO()
    img = Image.open(img_path)
    img.save(buf, format="JPEG", quality=quality)
    buf.seek(0)

    return base64.b64encode(buf.read()).decode()

def add_annotation(uuid, frame_no, js):
    frame_dir = os.path.join(unlabeled_root, uuid, frame_no)

    if not os.path.exists(frame_dir):
        return str(False)

    json_files = sorted(glob.glob(os.path.join(frame_dir, '*.json')))

    if len(json_files) == 0:
        new_annotation_file = os.path.join(frame_dir, '0.json')
    else:
        last_json_file = json_files[-1]
        last_json_file_int = int(os.path.basename(last_json_file).split('.')[0])
        new_annotation_file = os.path.join(frame_dir, '.'.join([str(last_json_file_int + 1), 'json']))

    with open(new_annotation_file, 'w+') as f:
        clean_json = json.loads(js)
        f.write(json.dumps(clean_json, indent=4, sort_keys=True))
        stats.increment_frames_labeled()
        stats.increment_total_labels(len(clean_json))
        log('Wrote annotation for uuid: {}, frame: {}'.format(uuid, frame_no))

    return str(True)

def generate_image_labeling_json(last_img_uuid=None, last_frame=-1, sequential_img=False, load_server_polygons=False):
    def pick_next_image(last_img_uuid, last_frame, sequential_img, pseudo_sequential=False):
        if sequential_img:
            last_frame += 1

            if last_img_uuid is None:
                last_img_uuid = random.choice([d for d in os.listdir(unlabeled_root) if not d.startswith('.')])

            target_path = os.path.join(unlabeled_root, last_img_uuid)
            frame_path = os.path.join(target_path, str(last_frame))

            if os.path.exists(frame_path):
                return os.path.join(target_path, str(last_frame), 'frame.jpg')
            else:
                return pick_next_image(last_img_uuid, last_frame, False, True)
        else:
            img_uuid = random.choice([d for d in os.listdir(unlabeled_root) if not d.startswith('.')])
            target_path = os.path.join(unlabeled_root, img_uuid)
            frames = sorted([d for d in os.listdir(target_path) if not d.startswith('.')])
            target_frame = frames[0] if pseudo_sequential else random.choice(frames)
            return os.path.join(target_path, target_frame, 'frame.jpg')
    
    get_frame = pick_next_image(last_img_uuid, last_frame, sequential_img)
    frame_text = convert_img_to_base64(get_frame)

    frame_no_dir = os.path.dirname(get_frame)
    uuid_dir = os.path.dirname(frame_no_dir)
    frame_no = os.path.basename(frame_no_dir)
    uuid = os.path.basename(uuid_dir)

    json_out = {'uuid' : uuid, 'frame_no' : frame_no}
    json_out['frame'] = str(frame_text)

    if load_server_polygons:
        json_out['metadata'] = calculate_average_annotations(load_frame_annotations(uuid, frame_no))

    return json.dumps(json_out, indent=4, sort_keys=True)

def available_frames():
    return len([f[0] for r,d,f in os.walk(unlabeled_root) if 'jpg' in f[0]])

def load_labeled_stats(in_memory=True):
    if in_memory:
        return {'total_images' : stats.frames_labeled, 'total_labels' : stats.total_labels}
    else:
        labeled_stats_file = os.path.join(logs_root, 'stats.json')
        if os.path.exists(labeled_stats_file):
            with open(labeled_stats_file, 'r') as f:
                return json.loads(f.read())
        else:
            save_labeled_stats(0, 0)

    return {'total_images' : 0, 'total_labels' : 0}

def save_labeled_stats(total_images, total_labels):
    labeled_stats_file = os.path.join(logs_root, 'stats.json')

    with open(labeled_stats_file, 'w+') as f:
        f.write(json.dumps({'total_images' : total_images, 'total_labels' : total_labels}, indent=4, sort_keys=True))

start_stats = load_labeled_stats(in_memory=False)
stats.set_total_labels(start_stats['total_labels'])
stats.set_frames_labeled(start_stats['total_images'])

'''
 Utils for server functionality
'''
