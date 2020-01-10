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
		if type(json_str) is str:
			json_obj = json.loads(json_str)

		if not json_obj:
			return False

		self.qualifiers = json_obj['qualifiers'].lower().strip()
		self.producer   = json_obj['producer'].lower().strip()
		self.label      = json_obj['label'].replace('.', '').lower().strip()
		self.points     = [(p['x'], p['y']) for p in json_obj['points']]
		return True

	def iou(self, other=None):
		assert(other)
		assert(type(other) is Annotation)
		return calc_iou(self.points, other.points)
	
	# TODO: Implement tree-depth based diff for calculating diff
	# between two labels in the label-tree
	def label_diff(self, other=None):
		return int(not self.same_type(other))
	
	def same_type(self, other=None):
		assert(other)
		assert(type(other) is Annotation)
		return self.label == other.label

	def diff(self, other=None):
		assert(other)
		assert(type(other) is Annotation)

		iou = self.iou(other) # [0, 1] proportional to similarity
		# label_diff = self.label_diff(other) <-- Once tree-depth [0,1] implemented, average this in
		return (1 - iou) # [0, 1] proportional to dissimilarity (diff)

class AnnotationAggregator(object):
	def __init__(self):
		self.default_path = UNLABELED_DATA_PATH
		self.clearAnnotations()

	def clearAnnotations(self):
		self.annotations = {}

	def load_annotations(self, json_paths, load_into_object=True):
		ann = {}
		for i, json_path in enumerate(json_paths):
			with open(json_path, 'r') as f:
				json_obj = json.loads(f.read())
				for label in json_obj:
					if i not in ann:
						ann[i] = []
					annotation = Annotation(label)
					ann[i].append(annotation.json_str())

		if load_into_object:
			self.annotations = ann

		return ann

	def aggregate(self, min_iou=.8):
		tracking_layer = [] 
		if self.annotations is None:
			return None
		
		for _, idx in enumerate(self.annotations):
			for _, annotation in enumerate(self.annotations[idx]):
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
