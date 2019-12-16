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
		self.annotation = {}

		if json_str is not None:
			self.initialize_from_json(json_str)
	
	def json_str(self):
		return json.dumps(self.annotation)

	def initialize_from_json(self, json_str):
		json_obj = json_str
		if type(json_str) == str:
			json_obj = json.loads(json_str)

		self.annotation.clear()
		self.annotation['label'] = json_obj['label'].replace('.', '').lower().strip()
		self.annotation['producer'] = json_obj['producer'].lower().strip()
		self.annotation['qualifiers'] = json_obj['qualifiers'].lower().strip()
		self.annotation['points'] = [(p['x'], p['y']) for p in json_obj['points']]
		self.annotation['raw_points'] = json_obj['points']

	def iou(self, other=None):
		if other is None or type(other) is not Annotation:
			return 0

		return calc_iou(self.raw_points, other.raw_points)

	def diff(self, other=None):
		if other is None or type(other) is not Annotation:
			return 0

		iou = self.iou(other)
		return iou

# TODO: Fix this up
class AnnotationAggregator(object):
	def __init__(self):
		self.default_path = unlabeled_root
		self.annotations = {}

	def clearAnnotations(self):
		self.annotations = {}

	def load_annotations(self, json_paths):
		ann = {}
		for i, json_path in enumerate(json_paths):
			with open(json_path, 'r') as f:
				json_obj = json.loads(f.read())
				for label in json_obj:
					if i not in ann:
						ann[i] = []
					annotation = Annotation(label)
					ann[i].append(annotation.json_str())

		self.annotations = ann
		return ann

	def aggregate(self):
		min_iou = .2
		if self.annotations is None:
			return None
		
		for i, idx in enumerate(self.annotations):
			for j, annotation in enumerate(self.annotations[idx]):
				print(i, j, annotation)

		return json.dumps(self.annotations, indent=4, sort_keys=True)
