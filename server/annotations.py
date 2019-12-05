from shapely.geometry import Polygon
from itertools import combinations_with_replacement

from utils import *

def calc_iou(poly1, poly2):
    assert(len(poly1) == 4 and len(poly2) == 4)

    a = Polygon([(p['x'], p['y']) for p in poly1])
    b = Polygon([(p['x'], p['y']) for p in poly2])

    return a.intersection(b).area / a.union(b).area

class Annotation(object):
	def __init__(self, json_str=None):
		self.label = ""
		self.producer = ""
		self.qualifiers = []
		self.points = []
		self.raw_points = []

		if json_str is not None:
			self.initialize_from_json(json_str)

	def __repr__(self):
		self_str = self.label
		if self.producer:
			self_str += ' [{}]'.format(self.producer)
		if self.qualifiers:
			self_str += ' ({})'.format(self.qualifiers)
		self_str += ' ' + str(self.points)
		return self_str

	def initialize_from_json(self, json_str):
		json_obj = json_str
		if type(json_str) == str:
			json_obj = json.loads(json_str)

		self.label = json_obj['label'].replace('.', '').lower().strip()
		self.producer = json_obj['producer'].lower().strip()
		self.qualifiers = json_obj['qualifiers'].lower().strip()
		self.points = [(p['x'], p['y']) for p in json_obj['points']]
		self.raw_points = json_obj['points']

	def iou(self, other=None):
		if other is None or type(other) is not Annotation:
			return 0

		return calc_iou(self.raw_points, other.raw_points)

	def diff(self, other=None):
		if other is None or type(other) is not Annotation:
			return 0

		iou = self.iou(other)
		return iou

# used once per frame
class AnnotationAggregator(object):
	def __init__(self):
		self.default_path = unlabeled_root
		self.annotations = {}

	def clearAnnotations(self):
		self.annotations = {}

	def load_annotations(self, json_paths):
		annotations = {}
		for i, json_path in enumerate(json_paths):
			with open(json_path, 'r') as f:
				json_obj = json.loads(f.read())
				for label in json_obj:
					if i not in annotations:
						annotations[i] = []
					annotations[i].append(Annotation(label))

		self.annotations = annotations
		return annotations

	def aggregate(self):
		if self.annotations is None:
			return None

		# this is ~ O(n^5) lmao wtf
		# we should try to make this better in the future
		for ann1 in self.annotations:
			for label in self.annotations[ann1]:
				for ann2 in [x for x in self.annotations if x != ann1]:
					#print(ann1, ann2)
					pass
		return '{}'
