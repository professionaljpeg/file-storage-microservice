import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Directory where files will be stored locally
UPLOAD_FOLDER = 'storage'
# Limit uploads to 16 Megabytes to prevent abuse
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure that the storage directory exists when the app starts
os.makedirs(UPLOAD_FOLDER, exist_ok=True)