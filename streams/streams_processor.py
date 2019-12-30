import pathlib
import json

from stream import *
from treelib import Node, Tree

FILE_PATH = pathlib.Path(__file__).parent
NODES_PATH = FILE_PATH.joinpath('nodes')

def load_streams():
    json_obj_map = {}
    for node in NODES_PATH.glob('**/*.json'):
        json_obj = {}
        with open(node, 'r') as node_file:
            try:
                json_obj = json.loads(node_file.read())
            except:
                continue
        name = json_obj['name'] if 'name' in json_obj else node.stem.replace('-', ' ')
        json_obj_map[name] = json_obj
    
    return json_obj_map

def load_stream_manager():
    streams = load_streams()
    if not streams:
        return
    
    stream_manager = StreamManager()

    for stream in streams:
        stream_manager.add_stream(streams[stream])

    return stream_manager
