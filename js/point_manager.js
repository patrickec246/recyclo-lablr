class Shape {
	qualifiers = "";
	label = "";
	points = new Array();

	constructor(label = null) {
		if (label) {
			this.label = label;
		}
	}

	set_label(label) {
		this.label = label;
	}

	get_label() {
		return this.label;
	}

	clear() {
		this.points.length = 0;
	}

	add_point(x, y) {
		if (this.points.length >= 4) return false;

		this.points.push({x:x, y:y, angle: 0});
		this.sort_points();

		return true;
	}

	num_points() {
		return this.points.length;
	}

	pop_point() {
		if (this.points.length > 0) {
			var popped = this.points.pop();
			this.sort_points();
			return popped;
		}

		return null;
	}

	inside_shape(x, y) {
		var inside = false;
		for (var i = 0, j = this.points.length - 1; i < this.points.length; j = i++) {
			var xi = this.points[i].x, yi = this.points[i].y;
			var xj = this.points[j].x, yj = this.points[j].y;

			var intersect = ((yi > y) != (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
			if (intersect) inside = !inside;
		}
		return inside;
	}

	sort_points() {
		// sort by x, find x avg
		this.points.sort((a, b) => a.y - b.y );
		const centroid_y = (this.points[0].y + this.points[this.points.length - 1].y) / 2;
		
		// sort by y, find y avg
		this.points.sort((a, b) => b.x - a.x);
		const centroid_x = (this.points[0].x + this.points[this.points.length - 1].y) / 2;
		
		// centroid
		const centroid = {x:centroid_x, y:centroid_y};

		// find angle between centroid and point
		var startAng;
		this.points.forEach(point => {
			var ang = Math.atan2(point.y - centroid_y, point.x - centroid_x);

			if (!startAng) {
				startAng = ang;
			} else if (ang < startAng) {
				ang += Math.PI * 2;
			}
			point.angle = ang;
		});

		// sort by angle from centroid
		this.points.sort((a, b) => a.angle - b.angle);
		this.points.unshift(this.points.pop());
	}

	centroid() {
		var cx = 0;
		var cy = 0;

		for (var i = 0; i < this.points.length; i++) {
			var point = this.points[i];

			cx += point.x;
			cy += point.y;
		}

		return {x:(cx/this.points.length), y:(cy/this.points.length)};
	}

	to_s() {
		var s = '';
		this.points.forEach(p => {
			s += ['[', 'x:', p.x, ', y:', p.y, ']\n'].join('');
		});
		return s;
	}

	get_closest_point(x, y, max_dist = 5) {
		var closest_point = null;
		var closest_dist = Number.MAX_SAFE_INTEGER;
		var idx = 0;

		for (var i = 0; i < this.points.length; i++) {
			var p = this.points[i];
			var dist = Math.hypot(x - p.x, y - p.y);
			if (dist < closest_dist) {
				closest_dist = dist;
				closest_point = p;
				idx = i;
			}
		}

		if (closest_dist > max_dist) {
			return null;
		} 

		return { point:closest_point, idx:idx, dist:closest_dist };
	}

	replace_closest_point(x, y, max_dist=5) {
		var closest = this.get_closest_point(x, y);

		if (closest) {
			this.points[closest.idx].x = closest.point.x;
			this.points[closest.idx].y = closest.point.y;
			return true;
		}

		return false;
	}

	calculate_dock_location(width, height) {
		var minx = Number.MAX_SAFE_INTEGER, miny = Number.MAX_SAFE_INTEGER;
		var maxx = 0, maxy = 0;

		this.points.forEach(point => {
			minx = Math.min(point.x, minx);
			miny = Math.min(point.y, miny);
			maxx = Math.max(point.x, maxx);
			maxy = Math.max(point.y, maxy);
		});

		var left  = minx > (width + 20);
		var above = miny > (height + 20);

		if (above) {
			return [ ((minx + maxx) / 2) - 150, miny - (20 + height)];
		}

		var startX = left  ? minx - (10 + width)  : maxx + 10;
		var startY = above ? miny - (10 + height) : maxy + 10;

		return [startX, startY];
	}
}

class ShapeManager {
	shapes = new Array();

	delete_shape(shape) {
		for (var i = 0; i < this.shapes.length; i++) {
			if (this.shapes[i] == shape) {
				this.shapes.splice(i);
				return true;
			}
		}
		return false;
	}

	select_shape(x, y) {
		for (var i = 0; i < this.shapes.length; i++) {
			if (this.shapes[i].inside_shape(x, y)) {
				return this.shapes[i];
			}
		}
		return null;
	}

	replace_closest_point(x, y, max_dist=5) {
		var closest_shape = null;
		var closest_dist = Number.MAX_SAFE_INTEGER;
		var shape_idx = 0;
		var point_idx = 0;

		for (var i = 0; i < this.shapes.length; i++) {
			var shape = this.shapes[i];
			var p = shape.get_closest_point(x, y, max_dist);

			if (p && p.dist < closest_dist) {
				closest_dist = p.dist;
				closest_shape = shape;
				shape_idx = i;
				point_idx = p.idx;
			}
		}

		if (closest_dist > max_dist) {
			return false;
		}

		this.shapes[shape_idx].points[point_idx].x = x;
		this.shapes[shape_idx].points[point_idx].y = y;

		return true;
	}

	clear_shapes() {
		this.shapes.length = 0;
	}

	num_shapes() {
		return this.shapes.length;
	}

	add_shape(shape, label = null) {
		if (label) {
			shape.label = label;
		}

		this.shapes.push(shape);
	}

	print_shapes() {
		this.shapes.forEach(s => {
			console.log(s.to_s())
		})
	}

	draw_shape(shape, ctx) {
		// draw polygon

		ctx.beginPath();
		ctx.moveTo(shape.points[0].x, shape.points[0].y);

		var cx = 0;
		var cy = 0;
		var n = shape.points.length;

		for (var i = 0; i < shape.points.length; i++) {
			var point = shape.points[i];
			ctx.lineTo(point.x, point.y);

			cx += point.x;
			cy += point.y;
		}

		ctx.closePath();
		ctx.fillStyle = 'rgba(0, 0, 0, .15)';
		ctx.fill();

		ctx.strokeStyle = 'rgba(0, 255, 255, .7)';
		ctx.stroke();

		// draw edge points
		for (var i = 0; i < shape.points.length; i++) {
			var point = shape.points[i];
			ctx.lineJoin = 'bevel';
			ctx.strokeStyle='red';
			ctx.strokeRect(point.x - 2, point.y - 2, 5, 5);
			ctx.fillStyle='white';
			ctx.fillText(i, point.x + 5, point.y + 5);
		}

		var text_x = (cx / n) + 5;
		var text_y = (cy / n) + 5;

		ctx.font = "14pt Arial";
		ctx.fillStyle='rgba(0, 0, 0, .6)';
		ctx.fillText(shape.label, text_x + 1, text_y + 1);
		ctx.fillStyle='white';
		ctx.fillText(shape.label, text_x, text_y)

		var centroid = shape.centroid();
		ctx.fillRect(centroid.x - 1, centroid.y - 1, 3, 3);
	}

	draw_shapes(ctx) {
		this.shapes.forEach(shape => {
			this.draw_shape(shape, ctx);
		});
	}

	formatLabels() {
		var output = new Array();

		this.shapes.forEach(shape => {
			var points = new Array();
			shape.points.forEach(point => {
				points.push({x:point.x, y:point.y});
			});

			output.push({
				label:shape.label,
				qualifiers:shape.qualifiers,
				points:points,
			});
		});

		return JSON.stringify(output);
	}
}

class StatsManager {
	num_images = 0;
	num_shapes = 0;

	complete_image(shapes=1, images=1) {
		this.num_images += images;
		this.num_shapes += shapes;
	}

	get_num_images() {
		return this.num_images;
	}

	mAPIncrease() {
		return this.num_shapes * .0000626;
	}
}