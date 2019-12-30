import sys
import pathlib

FILE_PATH = pathlib.Path(__file__).parent
STREAM_NODES_PATH = FILE_PATH.joinpath('nodes')

sys.path.insert(0, str(FILE_PATH.absolute().parent.joinpath('labels')))

from label_preprocessor import *

class Stream():
    def __init__(self, stream_name=''):
        self.stream_name = stream_name

class StreamManager():
    def __init__(self):
        self.default_stream = None
        self.streams = {}
        self.label_tree = build_primary_tree()
    
    def add_stream(self, stream):
        if self.default_stream is None:
            self.default_stream = stream

        if stream['name'] not in self.streams:
            self.streams[stream['name']] = stream
    
    def get_stream(self, stream_name):
        if stream_name in self.streams:
            return self.streams[stream_name]
        return None
    
    def get_default_stream(self):
        for _,stream in self.streams.items():
            if 'default' in stream:
                return stream
        
        if not self.streams:
            return None
        
        _,stream = self.streams.items()[0]
        return stream

    def infer_stream(self, label=None, stream=None):
        if type(label) is str and stream is None:
            label_data = self.label_tree.get_node(label)
            if not label_data:
                return None
            
            if 'stream' not in label_data.data:
                return self.get_default_stream()
            
            return self.infer_stream(label=label_data.data, stream=label_data.data['stream'])
        
        if not stream in self.streams:
            return self.get_default_stream()
        
        stream_data = self.streams[stream]
        return stream_data
    