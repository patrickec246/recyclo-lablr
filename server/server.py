import sys
sys.path.insert(0, './src')

from flask import Flask, render_template, request
from utils import *
from sentinel import *
from settings import *

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

@app.route('/modal_step')
def retrieve_modal_step():
    step = int(request.args.get('step'))
    return render_template('modal_steps/step{}.html'.format(step))

@app.route('/request_image', methods=['GET'])
def request_image():
    last_uuid = request.args.get('uuid')
    frame = request.args.get('frame')
    sequential = request.args.get('sequential')
    annotations = request.args.get('annotations')

    # If the user did not provide enough data, make a blank query for the next image
    if any(element is None for element in [last_uuid, frame, sequential, annotations]):
        return generate_image_labeling_json()

    # Use user data to guide next image query
    last_uuid = str(last_uuid)
    frame = int(frame)
    sequential = True if sequential.lower() == 'true' else False
    annotations = True if annotations.lower() == 'true' else False

    return generate_image_labeling_json(last_uuid, frame, sequential, annotations)

@app.route('/post_annotation', methods=['GET', 'POST'])
def post_annotation():
    annotation_json = request.form.get('annotation_data')

    uuid = request.form.get('uuid')
    frame_no = request.form.get('frame_no')

    return add_annotation(uuid, frame_no, annotation_json)

@app.route('/stats')
def request_trash_data():
    return json.dumps(load_labeled_stats(in_memory=True), indent=4, sort_keys=True)

@app.route('/labels.txt')
def get_labels():
    with open('static/labels.txt', 'r') as f:
        return f.read()
    return ''

if __name__ == "__main__":
    # Start server backend process
    sentinel = ServerSentinel()
    sentinel.run()

    # Stand up web server for front end
    app.run(debug=True)
