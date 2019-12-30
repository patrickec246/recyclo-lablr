class Stream():
    def __init__(self, stream_name=''):
        self.stream_name = stream_name
    
    def print(self):
        print('yop')

class StreamManager():
    def __init__(self):
        self.default_stream = None
        self.streams = {}
    
    def add_stream(self, stream):
        if self.default_stream is None:
            self.default_stream = stream

        if stream['name'] not in self.streams:
            self.streams[stream['name']] = stream
    
    def get_stream(self, stream_name):
        if stream_name in self.streams:
            return self.streams[stream_name]
        return None