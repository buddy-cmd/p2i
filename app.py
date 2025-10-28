from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from utils import apply_filter

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/p2i', methods=['POST'])
def transform():
    image = request.files.get('image')
    prompt = request.form.get('prompt')
    filter_name = request.form.get('filter')
    size = request.form.get('size')
    control_image = request.files.get('control_image')
    control_type = request.form.get('control_type')

    if not image or not filter_name:
        return jsonify({'error': 'Missing image or filter'}), 400

    input_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(input_path)

    control_path = None
    if control_image:
        control_path = os.path.join(UPLOAD_FOLDER, "control_" + control_image.filename)
        control_image.save(control_path)

    output_files = apply_filter(input_path, UPLOAD_FOLDER, filter_name, prompt, control_path, control_type)
    preview_urls = [f"/uploads/{f}" for f in output_files]

    return jsonify({'preview_urls': preview_urls})

@app.route('/uploads/<path:filename>')
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)