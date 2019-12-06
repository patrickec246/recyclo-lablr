import logging
from logging import FileHandler, Formatter

import threading

SERVER_LOG_FILE = 'logs/server.log'

log_file_handler = FileHandler(SERVER_LOG_FILE)
log_file_handler.setLevel(logging.INFO)
log_file_handler.setFormatter(Formatter('[%(asctime)s] [%(levelname)s] - %(message)s'))

logger = logging.getLogger('recyclr.server')
logger.setLevel(logging.INFO)
logger.addHandler(log_file_handler)

def log(log_msg):
	logger.info(log_msg)

class StatsCounter(object):
	def __init__(self):
		self.frames_labeled = 0
		self.frames_labeled_lock = threading.Lock()
		self.total_labels = 0
		self.total_labels_lock = threading.Lock()

	def set_frames_labeled(self, n=0):
		with self.frames_labeled_lock:
			self.frames_labeled = n

	def set_total_labels(self, n=0):
		with self.total_labels_lock:
			self.total_labels = n

	def increment_frames_labeled(self, n=1):
		with self.frames_labeled_lock:
			self.frames_labeled += n

	def increment_total_labels(self, n=1):
		with self.total_labels_lock:
			self.total_labels += n

stats = StatsCounter()