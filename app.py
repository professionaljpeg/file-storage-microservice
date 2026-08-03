import os
import database.db_connector as db
from functools import wraps
from flask import Flask, request, jsonify, abort, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

db_connection = db.connect_to_database()

# Directory where files will be stored locally
UPLOAD_FOLDER = 'storage'
# Limit uploads to 16 Megabytes to prevent abuse
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure that the storage directory exists when the app starts
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/api/v1/files', methods=['POST'])
def upload_file():
    """Endpoint to upload a file."""
    # Check if the HTTP request contains a file payload
    if 'file' not in request.files:
        return jsonify({'error': 'No file part found in request'}), 400

    file = request.files['file']

    # Check if a file was actually selected
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # secure_filename prevents directory traversal attacks
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        # Return a standard JSON response
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'url': f'/api/v1/files/{filename}'
        }), 201


@app.route('/api/v1/files/<filename>', methods=['GET'])
def download_file(filename):
    """Endpoint to download a file."""
    try:
        # send_from_directory safely serves files from the specified folder
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404


@app.route('/api/v1/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Endpoint to delete a file."""
    # Sanitize the filename to prevent directory traversal attacks
    safe_filename = secure_filename(filename)

    if not safe_filename:
        return jsonify({'error': 'Invalid filename'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

    # Check if the file actually exists before trying to delete it
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        # Remove the file from the filesystem
        os.remove(file_path)
        return jsonify(
            {'message': f'File {safe_filename} deleted successfully'}), 200
    except Exception:
        # Catch potential OS errors (e.g., file is locked by another process)
        return jsonify(
            {'error': 'An error occurred while deleting the file'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 12627))
    app.run(host="classwork.engr.oregonstate.edu", port=port, debug=True)
