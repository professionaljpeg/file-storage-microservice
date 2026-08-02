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


if __name__ == '__main__':
    # Run the microservice on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
