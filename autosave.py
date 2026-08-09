import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS so the frontend can send requests directly to this service
CORS(app)

# The URL and API key from your existing frontend save function
FILE_STORAGE_URL = "http://classwork.engr.oregonstate.edu:12627/api/v1/files"
API_KEY = "207e5700fda649ec.J1Zo90WtXk7b_RaLoxKqtyXEgmsCEK0oc4_LEuWfgSU"

@app.route('/api/v1/autosave', methods=['POST'])
def autosave():
    """
    Receives JSON game state from the frontend and REST-posts it 
    as a file to the main storage microservice.
    """
    game_state = request.get_json()
    
    if not game_state:
        return jsonify({"error": "No game state provided"}), 400

    # Convert the JSON payload back into a string to send as a file
    json_string = json.dumps(game_state)
    
    # Package it exactly how app.py expects the upload ('file' part)
    files = {'file': ('savegame.json', json_string, 'application/json')}
    headers = {"X-API-Key": API_KEY}
    
    try:
        # Communicate with the file storage microservice via REST
        response = requests.post(FILE_STORAGE_URL, headers=headers, files=files)
        
        # app.py returns 201 on a successful upload
        if response.status_code == 201:
            return jsonify({"message": "Autosave stored successfully"}), 200
        else:
            return jsonify({"error": "File storage microservice rejected the save"}), 502
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to storage service: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 12629))
    app.run(host="classwork.engr.oregonstate.edu", port=port, debug=True)