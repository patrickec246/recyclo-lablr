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
		self.votes = 1

		if json_str is not None:
			self.initialize_from_json(json_str)
	
	def json_str(self):
		return json.dumps(self.annotation)

	def initialize_from_json(self, json_str):
		json_obj = json_str
		if type(json_str) == str:
			json_obj = json.loads(json_str)

		if not json_obj:
			return False

		self.label = json_obj['label'].replace('.', '').lower().strip()
		self.producer = json_obj['producer'].lower().strip()
		self.qualifiers = json_obj['qualifiers'].lower().strip()
		self.points = [(p['x'], p['y']) for p in json_obj['points']]
		return True

	def iou(self, other=None):
		if other is None or type(other) is not Annotation:
			return 0

		return calc_iou(self.points, other.points)
	
	def label_diff(self, other=None):
		return 1 if self.same_type(other) else 0
	
	def same_type(self, other=None):
		if other is None or type(other) is not Annotation:
			return False
		return self.label == other.label

	def diff(self, other=None):
		if other is None or type(other) is not Annotation:
			return 0

		iou = self.iou(other) # [0, 1] proportional to similarity
		label_diff = self.label_diff(other) # [0, 1] proportional to similarity
		return (1 - iou) # [0, 1] proportional to dissimilarity (diff)

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
		min_iou = .8
		tracking_layer = [] 
		if self.annotations is None:
			return None
		
		for i, idx in enumerate(self.annotations):
			for j, annotation in enumerate(self.annotations[idx]):
				represented = False
				ann = Annotation()
				if not ann.initialize_from_json(annotation):
					continue
				for tracking_annotation in tracking_layer:
					iou = ann.diff(tracking_annotation)
					if iou < min_iou and ann.same_type(tracking_annotation):
						tracking_annotation.votes += 1
						represented = True
						break
				
				if not represented:
					tracking_layer.append(ann)
		
		return [a.annotation for a in tracking_layer]
