from poseestimation import process_video
from flask import Flask, request, jsonify, flash
import os
import uuid
from firebase_admin import credentials, initialize_app, storage, firestore

app = Flask(__name__)
app.secret_key = "secretkey"

# Init firebase with your credentials
cred = credentials.Certificate("cric-d9771-firebase-adminsdk-pkadu-09ebdeeba3.json")
initialize_app(cred,
               {'storageBucket': 'cric-d9771.appspot.com'}
               )
bucket = storage.bucket() # storage bucket
store = firestore.client()

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
        result = request.form
        user_id = result.get('userId')

        if not user_id:
            return jsonify("Invalid user Id")
        if not request.files['file']:
            return jsonify("No file selected")

        video_file = request.files['file']
        fileid = uuid.uuid4().hex
        uploaded_video_path = os.path.join(app.config['UPLOAD_FOLDER'], fileid + video_file.filename)
        video_file.save(uploaded_video_path)

        # upload to firebase storage
        uploaded_video_blob = bucket.blob('uploads/' + fileid + video_file.filename)
        uploaded_video_blob.upload_from_filename(uploaded_video_path)
        uploaded_video_blob.make_public()

        result_video_file_path = process_video(uploaded_video_path)
        if result_video_file_path:
            # upload to firebase storage
            result_blob = bucket.blob(result_video_file_path)
            result_blob.upload_from_filename(result_video_file_path)
            result_blob.make_public()
            # return public url of result video file
            response = result_blob.public_url
            doc_ref = store.collection('legal-delivery-results')
            doc_ref.add({'userId': user_id, 'resultVideo': response})

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
