// globals
var canvas = document.getElementById('polyCanvas');
var ctx = canvas.getContext("2d");
var img_number = 1;
var mgr = new ShapeManager();
var stats = new StatsManager();

var uuid = "";
var frame_no = -1;
var metadata = "";
var cursorstyle = "default";

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
var canExit = true;

var map;
var marker = null;

function initMap() {
	map = new google.maps.Map(document.getElementById('mapDock'), 
	{
		center: {lat: 47.619, lng: -122.3168},
		zoom: 15,
		disableDefaultUI: true,
		mapTypeId: 'satellite'
	});

	marker = new google.maps.Marker({
		position : new google.maps.LatLng(47.619, -122.3168),
		map      : map
	});
}

function load_map(latitude, longitude) {
	loc = new google.maps.LatLng(latitude, longitude);
	map.setCenter(loc);
	marker.setPosition(loc);
}

// when the canvas image is updated, redraw the image
base_img.onload = function() {
	ctx.drawImage(base_img, 0, 0, canvas.width, canvas.height);
	reload_canvas();
}

/*
 * Drawing utilities
 */

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
	if (label_input_valid() && selected_shape) {
		selected_shape.label = document.getElementById('typeLabel').value;
		shapeDock.style.display = 'none';
		mgr.deselect_shapes();
		reload_canvas();
	}
}

// redraw the canvas, background img, and polygons
function reload_canvas() {
	// draw bg img
	ctx.drawImage(base_img, 0, 0, canvas.width, canvas.height);

	// draw polygons
	mgr.draw_shapes(ctx);
}

/*
 * Button functions (add, clear, skip, submit)
 */

function addShape() {
	if (!add_shape) {
		$("#addPoly").css({
			'background-color' : 'rgb(50, 100, 200)',
			'color' : 'white',
			'border' : '1px solid white',
			'transform' : 'rotate(90deg)'
		});

		$("#plusSign").css({
			'margin-top' : '0px'
		});

		cursorstyle = 'crosshair';
		canvas.style.cursor = cursorstyle;

		add_shape = true;
		added_shape = new Shape();
	}
}

function retrieve_next_image(sequential=false, carryover=false) {
	if (sequential) {
		frame_no += 1;
	}

	$.ajax({
		url: '/request_image',
		data: {
			uuid : uuid,
			frame : frame_no,
			sequential : sequential,
			annotations : carryover
		},
		success: set_canvas_image_from_json
	});

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

	retrieve_next_image(sequential, carryover);
	reload_canvas();
}

function submit_labels() {
	labels = mgr.formatLabels();

	$.ajax({
		url: "/post_annotation",
		type: "POST",
		data: {
			'uuid' : uuid,
			'frame_no' : frame_no,
			'annotation_data' : labels
		}
	});

	stats.complete_image(shapes = mgr.num_shapes());

	document.getElementById('localImages').innerText = stats.get_num_images();
	document.getElementById('localLabels').innerText = stats.get_num_labels();

	skipImage();
}

var settings_open = false;
$("#settingsBtn").on('click', function() {
	settings_open = !settings_open;

	var settings_panel = $("#settingsPanel");
	settings_panel.css({'left' : 'calc(100% - ' + (settings_open ? settings_panel.outerWidth() : '0') +'px)'});
	$("#settingsBtn").css({'transform' : 'rotate(' + (settings_open ? '-90' : '0') + 'deg)'});
});

var mapOpen = true;
$("#mapBtn").on('click', function() {
	mapOpen = !mapOpen;
	show_map_panel(mapOpen);
	if (mapOpen) {
		$("#mapBtn").addClass("mapOpenCtr");
		$("#mapBtn").removeClass("mapClosedCtr");
	} else {
		$("#mapBtn").removeClass("mapOpenCtr");
		$("#mapBtn").addClass("mapClosedCtr");
	}
	$("#mapBtn").css({'transform' : 'scaleX(' + (mapOpen ? '1' : '-1') + ')'});
});

$("#shapeDock").draggable();
$("#mapDock").draggable();
function show_map_panel(map_open) {
	if (!map_open) {
		$("#mapDock").fadeOut("fast", function() {});
	} else {
		$("#mapDock").fadeIn("fast", function() {});
	}
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

			$("#addPoly").removeAttr('style');
			$("#plusSign").css({'margin-top' : '1px'});

			cursorstyle = 'default';
			canvas.style.cursor = cursorstyle;
		}

		reload_canvas();
		if (added_shape) {
			mgr.draw_shape(added_shape, ctx, e.offsetX, e.offsetY);
		}
		return;
	}

	if (mgr.replace_closest_point(e.offsetX, e.offsetY)) {
		reload_canvas();
	}

	canvas_down = true;
}

canvas.onmousemove = function(e) {
	if (added_shape && added_shape.points.length > 0) {
		reload_canvas();
		mgr.draw_shape(added_shape, ctx, e.offsetX, e.offsetY);
	}

	drag = true;
	if (canvas_down) {
		if (mgr.replace_closest_point(e.offsetX, e.offsetY, 20)) {
			reload_canvas();
		}
	} else {
		hovering = mgr.mouseHover(e.offsetX, e.offsetY, reload_canvas);
		canvas.style.cursor = hovering ? 'pointer' : cursorstyle;
	}
}

canvas.onmouseup = function(e) {
	canvas_down = false;

	if (!drag && !added_shape) {
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

var savePoint = document.getElementById('savePoint');
var saveableIds = ['typeLabel', 'featuresLabel', 'producerLabel']

saveableIds.forEach(id => {
	document.getElementById(id).addEventListener("keyup", function(e) {
		if (e.keyCode == 13 && label_input_valid()) {
			if (!canExit) {
				shade_input_label($("#typeLabel"));
				$("#typeLabel").autocomplete('close');
				canExit = true;
			} else {
				savePoint.click();
			}
		}
	});
});

function set_canvas_image_from_json(result) {
	json_result = JSON.parse(result);

	if (!json_result.frame || !json_result.frame_no) {
	    return;
	}
	uuid = json_result.uuid;
	frame_no = parseInt(json_result.frame_no);
	metadata = json_result.metadata;

	try {
		load_map(json_result.latitude, json_result.longitude);
		base_img.src = "data:image/png;base64," + json_result.frame;
		//mgr.load_from_json(metadata);
		reload_canvas();
	} catch (err) { }
}

var hopped = null;
var modal_step = -1;
var modal_objs = ["#polyCanvas", '#addPoly', '#clearPoly',
				  '#skipFrame', '#submitLabels', '#settingsBtn',
				  '#mapBtn', '#statsPanel'];

function clear_hop() {
	$(".hop-outer").hide();
}

function advance_modal() {
	modal_step += 1;

	if (modal_step < modal_objs.length) {
		update_modal(modal_step);
		hopped = $(modal_objs[modal_step]).hop();
	} else {
		clear_hop();
	}
}

function reverse_modal() {
	if (modal_step > 0) {
		modal_step -= 1;
	}

	if (modal_step < modal_objs.length) {
		update_modal(modal_step);
		hopped = $(modal_objs[modal_step]).hop();
	} else {
		clear_hop();
	}
}

function update_modal(step) {
	$.ajax({
		url: "/modal_step",
		data: {
			'step' : step
		},
		success: function(response) {
			$('#modalWrapper').html(response);
		}
	});
}

function show_tutorial_modal() {
	$("#tutorialModal").modal("show");
}

function close_tutorial_modal() {
	clear_hop();
	$("#tutorialModal").remove();
}

$("#sequentialFrames").change(function() {
	$("#previousAnnotations").prop("disabled", !this.checked);
});

$(window).on('load', function() {
	var visited_before = sessionStorage.getItem("hasVisited");

	if (visited_before == 'false' || visited_before == false || visited_before == null) {
		sessionStorage.setItem("hasVisited", true);
		show_tutorial_modal();
	}

	//sessionStorage.removeItem("hasVisited");
});

$(document).ready(function() {
	$.ajax({
		url: "/request_image",
		success: set_canvas_image_from_json
	});

	load_statistics();
});

function label_input_valid() {
	input_val = $("#typeLabel").val();
	console.log(input_val);
	return input_val && x.includes(input_val);
}

var x = []

$.get("labels.txt", function(data) {
	x = data.split('\n')
	$("#typeLabel").autocomplete({
		source: x,
		autoFocus: true,
		open: function() { canExit = false; },
		close: function() { canExit = false; },
		close: shade_input,
		change: shade_input
	});
});

function shade_input() {
	shade_input_label($("#typeLabel"));
}
function shade_input_label(e) {
	e.css('background-color', (label_input_valid() ? 'rgba(10, 224, 69, .1)' : 'rgba(250, 67, 46, .1)'));
}

$("#typeLabel").on('input', function() {
	shade_input_label($(this));
});


$("#addPoly").on('click', addShape);
$("#clearPoly").on('click', clearShapes);
$("#skipFrame").on('click', skipImage);
$("#submitLabels").on('click', submit_labels);

setInterval(load_statistics, 5000);

function load_statistics() {
	$.get("/stats", function(data) {
		d = JSON.parse(data);
		$("#globalImages").text(d.total_images);
		$("#globalLabels").text(d.total_labels);
	});
}

$(document).keypress(function(e) {
	for (i = 0; i < saveableIds.length; i++) {
		if ($("#" + saveableIds[i]).is(":focus")) {
			return;
		}
	}

	var keycode = String.fromCharCode(e.which);

	if (keycode == 'a') {
		addShape();
	} else if (keycode == 'x') {
		clearShapes();
	} else if (keycode == 'n') {
		skipImage();
	} else if (keycode == 's') {
		submit_labels();
	}
 });
