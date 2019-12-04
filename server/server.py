from flask import Flask, render_template, request
from utils import *

app = Flask(__name__)

@app.route('/')
def render_landing_page():
    return render_template('landing.html')

@app.route('/label')
def render_label_page():
	return render_template('label.html')

@app.route('/donate')
def render_donate_page():
	return render_template('donate.html')

@app.route('/about')
def render_about_page():
	return render_template('about.html')

@app.route('/request_annotation', methods=['GET'])
def request_annotation():
    return ''

@app.route('/request_image', methods=['GET'])
def request_image():
	last_uuid = request.args.get('uuid')
	frame = request.args.get('frame')
	sequential = request.args.get('sequential')
	annotations = request.args.get('annotations')

	if any(element is None for element in [last_uuid, frame, sequential, annotations]):
		return 'ERR: Invalid parameters'

	last_uuid = str(last_uuid)
	frame = int(frame)
	sequential = True if sequential.lower() == 'true' else False
	annotations = True if annotations.lower() == 'true' else False

	return generate_image_labeling_json(last_uuid, frame, sequential, annotations)

@app.route('/post_annotation', methods=['GET', 'POST'])
def post_annotation():
    return ''

@app.route('/trash_data')
def request_trash_data():
	return '{"total_trash": 1506, "total_recyclables":1294}'

if __name__ == "__main__":
    app.run(debug=True)
