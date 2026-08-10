import os
import secrets
import requests
import database.db_connector as db
from functools import wraps
from flask import Flask, request, jsonify, abort, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

db_connection = db.connect_to_database()

UPLOAD_FOLDER = 'storage'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
AUTH_SERVICE_URL = "http://classwork.engr.oregonstate.edu:12628/api/v1/auth/verify"

# Ensure that the storage directory exists when the app starts
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def find_client_name(client_name):
    """Checks if a client has already generated an API key"""
    query = "SELECT * FROM api_keys WHERE username = %s LIMIT 1;"
    cursor = db.execute_query(db_connection, query, (client_name,))
    client_name_record = cursor.fetchone()

    if client_name_record:
        query = "SELECT keyID, secretHash FROM api_keys WHERE username = %s;"
        cursor = db.execute_query(db_connection, query, (client_name,))
        clientAPIKey = cursor.fetchone()
        return True

def create_api_key(client_name: str) -> str:
    """Generates a secure API key, hashes the secret part, 
    and saves the record to the database."""
    
    # Generate the public KeyID (16 hex chars) and secret string
    keyID = secrets.token_hex(8) 
    secret = secrets.token_urlsafe(32)   
    
    # Hash the secret part using Werkzeug
    secret_hash = generate_password_hash(secret)
    
    query = f"INSERT INTO api_keys (keyID, username, secretHash) VALUES (%s, %s, %s);"

    cur = db.execute_query(db_connection, query, (keyID, client_name, secret_hash))
    print(cur)

    return f"{keyID}.{secret}"

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Sends the API key to the API Authenticator service (big pool)
        and returns the response"""
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({"error": "Missing API key in headers"}), 401
            
        try:
            # Send the API key to the auth microservice
            response = requests.post(
                AUTH_SERVICE_URL, 
                json={"api_key": api_key},
                timeout=5 # Prevents app.py from hanging if the auth service is down
            )
            
            if response.status_code == 200 and response.json().get('valid'):
                return f(*args, **kwargs)
            else:
                # Pass along the 401 Unauthorized if the key was invalid
                return jsonify({"error": "Invalid API key"}), 401
                
        except requests.exceptions.RequestException as e:
            # Handles the case where the auth microservice is offline
            return jsonify({"error": "Authentication service is currently unavailable"}), 503
            
    return decorated_function

@app.route('/')
def root():
    """Renders frontend directory"""
    return render_template('index.html', api_key='')

@app.route('/generate_key', methods=['POST'])
def generate_key():
    """Acts as a go-between for the front-end and the create_api_key
    function"""
    client_name = request.form.get('appName')
    if client_name.strip() == '':
        return render_template('index.html', api_key="Invalid App Name")

    if find_client_name(client_name):
        return render_template('index.html', api_key="App already has API key")

    api_key = create_api_key(client_name)
    
    return render_template('index.html', api_key=api_key)

@app.route('/api/v1/files', methods=['POST'])
@require_api_key
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
@require_api_key
def download_file(filename):
    """Endpoint to download a file."""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404


@app.route('/api/v1/files/<filename>', methods=['DELETE'])
@require_api_key
def delete_file(filename):
    """Endpoint to delete a file."""
    safe_filename = secure_filename(filename)

    if not safe_filename:
        return jsonify({'error': 'Invalid filename'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

    # Check if the file actually exists before trying to delete it
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
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
