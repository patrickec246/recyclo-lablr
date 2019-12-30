import cv2
import os
import uuid
import json
import glob
import pyexifinfo
import datetime
import base64
import random
import re

from settings import *

from pathlib import Path
from io import StringIO, BytesIO
from PIL import Image

# Directories
SRC_DIR = Path(__file__).parents[1]

LOGS_PATH = SRC_DIR.joinpath('logs')
DATA_PATH = SRC_DIR.joinpath('data')

RAW_DATA_PATH = DATA_PATH.joinpath('raw')
LABELED_DATA_PATH = DATA_PATH.joinpath('labeled')
UNLABELED_DATA_PATH = DATA_PATH.joinpath('unlabeled')

# Supported datatypes
supported_video_types = ['mp4', 'avi', 'MOV', 'mov']
supported_image_types = ['png', 'jpg', 'jpeg']

'''
 This is going to take some massaging to fine tune but this works... ok...
'''
def calculate_average_annotations(annotations, iou_thresh=.75):
    if len(annotations) > 0:
        return annotations[0]

    # TODO implement correctly
    return {}

# Loads the annotation 
def load_frame_annotations(uuid, frame, frame_dir=UNLABELED_DATA_PATH):
    js = []

    annotation_dir = os.path.join(frame_dir, uuid, str(frame), '*.json')

    for annotation in glob.glob(annotation_dir):
        with open(annotation, 'r') as f:
            js.append(json.loads(f.read()))

    return js

def pick_random_data_path():
    def supported(data_path):
        for supported_format in supported_video_types:
            if supported_format.endswith('.' + supported_format):
                return True
        for supported_format in supported_image_types:
            if supported_format.endswith('.' + supported_format):
                return True
        return False

    valid_data = [data_path for data_path in glob.glob(os.path.join(RAW_DATA_PATH, '*')) if supported(data_path)]
    return random.choice(valid_data) if len(valid_data) > 0 else None

def process_raw_data(data_path, frame_output_dir=UNLABELED_DATA_PATH, delete_after_processing=True):
    if not data_path:
        return None

    log('Attempting to process data path {}'.format(data_path))

    labeled_video_types = [ext for ext in supported_video_types if data_path.endswith(ext)]
    labeled_image_types = [ext for ext in supported_image_types if data_path.endswith(ext)]
    labels = len(labeled_video_types) + len(labeled_image_types)
    is_video = len(labeled_video_types) == 1

    if labels == 0 or labels > 1:
        return None

    if len(labeled_video_types) == 1:
        frames = convert_video_to_frames(data_path)
    else:
        frames = [(0, cv2.imread(data_path))]

    if not frames:
        return None

    if not os.path.exists(frame_output_dir):
        os.mkdir(frame_output_dir)

    dir_name = uuid.uuid4().hex
    path_name = os.path.join(frame_output_dir, dir_name)
    os.mkdir(path_name)

    for i, frame in enumerate(frames):
        annotation_path = os.path.join(path_name, str(i))
        os.mkdir(annotation_path)
        frame_path = os.path.join(annotation_path, 'frame.jpg')
        cv2.imwrite(frame_path, frame)

    metadata = get_video_metadata(video_path)
    metadata_path = os.path.join(path_name, 'metadata.json')

    with open(metadata_path, 'w+') as f:
        f.write(json.dumps(metadata, indent=4, sort_keys=True))

    if delete_after_processing:
        log('Converted {} to individual frames. Deleting source data')
        os.remove(data_path)

    return path_name

# Converts a video into an image for each frame
def convert_video_to_frames(video_path):
    if not os.path.exists(video_path):
        return None

    log('Converting video to frames: {}'.format(video_path))

    output = []
    video = cv2.VideoCapture(video_path)
    r, frame = video.read()

    while r:
        output.append(frame)
        r, frame = video.read()

    return output

# Extracts metadata from the raw video
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

# Loads the general metadata for a processed video
def read_video_metadata(uuid):
    metadata_file = os.path.join(UNLABELED_DATA_PATH, uuid, 'metadata.json')

    if not os.path.exists(metadata_file):
        return None

    with open(metadata_file) as f:
        return json.loads(f.read())

# Converts an image array object into a base64 character array
def convert_img_to_base64(img_path, quality=80):
    if img_path is None or not os.path.exists(img_path):
        return None

    buf = BytesIO()
    img = Image.open(img_path)
    img.save(buf, format="JPEG", quality=quality)
    buf.seek(0)

    return base64.b64encode(buf.read()).decode()

# Adds a json annotation from the user to annotations uuid/frame_no
def add_annotation(uuid, frame_no, js):
    frame_dir = os.path.join(UNLABELED_DATA_PATH, uuid, frame_no)

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

# Load the GPS (latitude, longitude) from a processed video uuid
def load_img_gps(uuid):
    def dms_to_decimal(dms_str):
        if not dms_str:
            return 0

        dms = re.split('[°\'"]+', dms_str.replace('deg', '°').replace(' ', ''))
        return (float(dms[0]) + (float(dms[1]) / 60) + (float(dms[2]) / 3600)) * (-1 if dms[3] in ['S', 'W'] else 1)

    meta_path = os.path.join(UNLABELED_DATA_PATH, uuid, 'metadata.json')

    if not os.path.exists(meta_path):
        return (0, 0)

    with open(meta_path, 'r') as f:
        meta = json.loads(f.read())
        return dms_to_decimal(meta['latitude']), dms_to_decimal(meta['longitude'])

# Query the next image as a json metadata object with img data represented as base64 string in result['frame']
def generate_image_labeling_json(last_img_uuid=None, last_frame=-1, sequential_img=False, load_server_polygons=False):
    def pick_next_image(last_img_uuid, last_frame, sequential_img, pseudo_sequential=False):
        if sequential_img:
            last_frame += 1

            if last_img_uuid is None:
                last_img_uuid = random.choice([d for d in os.listdir(UNLABELED_DATA_PATH) if not d.startswith('.')])

            target_path = os.path.join(UNLABELED_DATA_PATH, last_img_uuid)
            frame_path = os.path.join(target_path, str(last_frame))

            if os.path.exists(frame_path):
                return os.path.join(target_path, str(last_frame), 'frame.jpg')
            else:
                return pick_next_image(last_img_uuid, last_frame, False, True)
        else:
            available_uuids = [d for d in os.listdir(UNLABELED_DATA_PATH) if not d.startswith('.')]
            if len(available_uuids) == 0:
                return None
            img_uuid = random.choice(available_uuids)
            target_path = os.path.join(UNLABELED_DATA_PATH, img_uuid)
            frames = sorted([d for d in os.listdir(target_path) if not d.startswith('.')])
            target_frame = frames[0] if pseudo_sequential else random.choice(frames)
            return os.path.join(target_path, target_frame, 'frame.jpg')
    
    get_frame = pick_next_image(last_img_uuid, last_frame, sequential_img)

    if get_frame is None:
        return json.dumps({'uuid' : '', 'frame_no' : '', 'frame' : '', 'metadata' : ''}, indent=4, sort_keys=True)

    frame_no_dir = os.path.dirname(get_frame)
    uuid_dir = os.path.dirname(frame_no_dir)
    frame_no = os.path.basename(frame_no_dir)
    uuid = os.path.basename(uuid_dir)

    json_out = {'uuid' : uuid, 'frame_no' : frame_no}
    json_out['latitude'], json_out['longitude'] = load_img_gps(uuid)
    json_out['frame'] = str(convert_img_to_base64(get_frame))

    if load_server_polygons:
        json_out['metadata'] = calculate_average_annotations(load_frame_annotations(uuid, frame_no))

    return json.dumps(json_out, indent=4, sort_keys=True)

def available_frames():
    return len([f[0] for r,d,f in os.walk(UNLABELED_DATA_PATH) if len(f) > 0 and 'jpg' in f[0]])

def load_labeled_stats(in_memory=True):
    if in_memory:
        return {'total_images' : stats.frames_labeled, 'total_labels' : stats.total_labels}
    else:
        labeled_stats_file = os.path.join(LOGS_PATH, 'stats.json')
        if os.path.exists(labeled_stats_file):
            with open(labeled_stats_file, 'r') as f:
                return json.loads(f.read())
        else:
            save_labeled_stats(0, 0)

    return {'total_images' : 0, 'total_labels' : 0}

def save_labeled_stats(total_images, total_labels):
    labeled_stats_file = os.path.join(LOGS_PATH, 'stats.json')

    with open(labeled_stats_file, 'w+') as f:
        f.write(json.dumps({'total_images' : total_images, 'total_labels' : total_labels}, indent=4, sort_keys=True))

# This should be a database, yikes!
start_stats = load_labeled_stats(in_memory=False)
stats.set_total_labels(start_stats['total_labels'])
stats.set_frames_labeled(start_stats['total_images'])
