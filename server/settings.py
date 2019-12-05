import logging
import threading

logging.basicConfig(filename='server.log', level=logging.INFO, format='[%(asctime)s] [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

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
