from poseestimation import process_video
from flask import Flask, request, jsonify, flash
import os
import uuid

app = Flask(__name__)
app.secret_key = "secretkey"

path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

RESULTS_FOLDER = os.path.join(path, 'result_videos')
if not os.path.isdir(RESULTS_FOLDER):
    os.mkdir(RESULTS_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/process', methods=['POST'])
def uploadfiles():
    response = "Failed"

    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No file ')

        video_file = request.files['file']
        uploaded_video_path = os.path.join(app.config['UPLOAD_FOLDER'], uuid.uuid4().hex + video_file.filename)
        video_file.save(uploaded_video_path)
        is_success = process_video(uploaded_video_path)
        if is_success:
            response = "Success"

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
