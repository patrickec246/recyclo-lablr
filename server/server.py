from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/request_annotation', methods=['GET'])
def request_annotation():
    return ''

@app.route('/request_image', methods=['GET'])
def request_image():
    return ''

@app.route('/post_annotation', methods=['GET', 'POST'])
def post_annotation():
    return ''

if __name__ == "__main__":
    app.run(debug=True)
