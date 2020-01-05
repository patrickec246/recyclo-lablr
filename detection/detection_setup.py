import sys
import pathlib

DETECTION_FILE_PATH = pathlib.Path(__file__).parent

sys.path.insert(0, str(DETECTION_FILE_PATH.absolute().parent.joinpath('labels')))

from label_preprocessor import *

def setup():
    # Generate YOLO label list
    generate_server_label_text(file_name='labels.txt', custom_path=DETECTION_FILE_PATH)

setup()
