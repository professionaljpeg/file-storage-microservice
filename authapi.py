import os
from flask import Flask, request, jsonify
from werkzeug.security import check_password_hash
import database.db_connector as db

app = Flask(__name__)

# Connect to the database using your existing connector logic
db_connection = db.connect_to_database()

@app.route('/api/v1/auth/verify', methods=['POST'])
def verify_key():
    """
    REST endpoint to verify an API key. 
    Expects a JSON payload: {"api_key": "KeyID.Secret"}
    """
    data = request.get_json()
    
    if not data or 'api_key' not in data:
        return jsonify({"valid": False, "error": "Missing API key in payload"}), 400
        
    api_key = data['api_key']
    
    # Check if the key is correctly formatted with a period separating ID and secret
    if not api_key or '.' not in api_key:
        return jsonify({"valid": False, "error": "Invalid API key format"}), 401
        
    keyId, secret = api_key.split('.', 1)
    
    # Fetch the hashed secret from the database using the KeyID
    query = "SELECT * FROM api_keys WHERE keyID = %s LIMIT 1;"
    cursor = db.execute_query(db_connection, query, (keyId,))
    api_key_record = cursor.fetchone()
    
    # If the record exists, verify the hash against the provided secret
    if api_key_record and check_password_hash(api_key_record['secretHash'], secret):
        return jsonify({"valid": True, "message": "Authentication successful"}), 200
    else:
        return jsonify({"valid": False, "error": "Invalid or missing API key"}), 401

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 12628))
    app.run(host="classwork.engr.oregonstate.edu", port=port, debug=True)