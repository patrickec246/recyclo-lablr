// globals
var canvas = document.getElementById('polyCanvas');
var ctx = canvas.getContext("2d");
var img_number = 1;
var current_img = "imgs/0001.jpg";
var mgr = new ShapeManager();
var stats = new StatsManager();

// set load hooks
window.onload = reload_canvas;
window.onresize = reload_canvas;

// working vars
var selected_shape = null;
var base_img = new Image();
var last_img = "";
var canvas_down = false;
var added_shape = null;
var add_shape = false;

// when the canvas image is updated, redraw the image
base_img.onload = function() {
	ctx.drawImage(base_img, 0, 0, canvas.width, canvas.height);
	reload_canvas();
}

//
// Drawing utilities
//

function delete_selected_shape() {
	if (selected_shape) {
		mgr.delete_shape(selected_shape);
		selected_shape = null;
		shapeDock.style.display = 'none';
		mgr.deselect_shapes();
		reload_canvas();
	}
}

function update_selected_shape() {
	if (selected_shape) {
		selected_shape.label = document.getElementById('typeLabel').value;
		shapeDock.style.display = 'none';
		mgr.deselect_shapes();
		reload_canvas();
	}
}

// redraw the canvas, background img, and polygons
function reload_canvas() {
	// draw bg img
	if (last_img != current_img) {
		last_img = current_img;
		base_img.src = current_img;
	}

	ctx.drawImage(base_img, 0, 0, canvas.width - 200, canvas.height);

	// draw polygons
	mgr.draw_shapes(ctx);
}

//
// Button functions (add, clear, skip, submit)
//

function addShape() {
	if (!add_shape) {
		add_shape = true;
		added_shape = new Shape();
	}
}

function retrieve_next_image(sequential=false) {
	if (sequential) {
		img_number += 1;
	} else {
		var max = 27;
		img_number = Math.floor(Math.random() * Math.floor(max));
	}

	current_img = 'imgs/' + img_number.toString().padStart(4, '0') + '.jpg';
	console.log(current_img);
	reload_canvas();
}

function clearShapes() {
	mgr.clear_shapes();
	reload_canvas();
}

function skipImage() {
	var sequential = document.getElementById("sequentialFrames").checked;
	var carryover = document.getElementById("previousAnnotations").checked;
	
	if (!sequential || !carryover) {
		clearShapes();
	}

	retrieve_next_image(sequential);
	reload_canvas();
}

function submitLabels() {
	labels = mgr.formatLabels();
	// post labels
	console.log(labels);

	stats.complete_image(shapes = mgr.num_shapes());
	document.getElementById('imgCounter').innerText = stats.get_num_images() + ' images';
	document.getElementById('mAPCounter').innerText = '+ ' + stats.mAPIncrease() + '% mAP';

	skipImage();
}
//
// Canvas ('canvas') asynchronous hooks
//

let drag = false;

canvas.onmousedown = function(e) {
	drag = false;
	if (add_shape) {
		added_shape.add_point(e.offsetX, e.offsetY);

		if (added_shape.num_points() == 4) {
			added_shape.set_selected(true);
			mgr.add_shape(added_shape);
			added_shape.show_dock(shapeDock);

			selected_shape = added_shape;
			added_shape = null;
			add_shape = false;
		}

		reload_canvas();
		return;
	}

	if (mgr.replace_closest_point(e.offsetX, e.offsetY)) {
		reload_canvas();
	}

	canvas_down = true;
}

canvas.onmousemove = function(e) {
	drag = true;
	if (canvas_down) {
		if (mgr.replace_closest_point(e.offsetX, e.offsetY, 20)) {
			reload_canvas();
		}
	} else {
		hovering = mgr.mouseHover(e.offsetX, e.offsetY, reload_canvas);
		canvas.style.cursor = hovering ? 'pointer' : 'crosshair';
	}
}

canvas.onmouseup = function(e) {
	canvas_down = false;

	if (!drag) {
		var selection = mgr.select_shape(e.offsetX, e.offsetY);
		if (selection) {
			selection.show_dock(shapeDock);
			reload_canvas();
		}
	}
}

//
// Dock operations
//

var closeBtn = document.getElementById("closeBtn");
var shapeDock = document.getElementById("shapeDock");

closeBtn.onclick = function(e) {
	if (shapeDock.style.display == 'none') {
		shapeDock.style.display = 'block';
	} else {
		shapeDock.style.display = 'none';
	}
	mgr.deselect_shapes();
	reload_canvas();
}

savePoint = document.getElementById('savePoint');

document.getElementById('typeLabel').addEventListener("keyup", function(e) {
	if (e.keyCode == 13) {
		savePoint.click();
	}
});

document.getElementById('featuresLabel').addEventListener("keyup", function(e) {
	if (e.keyCode == 13) {
		savePoint.click();
	}
});

document.getElementById('producerLabel').addEventListener("keyup", function(e) {
	if (e.keyCode == 13) {
		savePoint.click();
	}
});

$("#sequentialFrames").change(function() {
	$("#previousAnnotations").prop("disabled", !this.checked);
})
