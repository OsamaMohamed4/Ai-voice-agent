
from flask import Flask, request, jsonify
from flask_cors import CORS
from livekit import api
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

@app.route('/api/token', methods=['POST'])
def create_token():
    """Generate LiveKit access token"""
    try:
        data = request.json
        room_name = data.get('roomName', 'default-room')
        participant_name = data.get('participantName', 'user')
        
        # Create access token
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(participant_name) \
            .with_name(participant_name) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            ))
        
        jwt_token = token.to_jwt()
        
        return jsonify({
            'token': jwt_token,
            'url': LIVEKIT_URL
        })
        
    except Exception as e:
        print(f"Error generating token: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("Token Server running on http://localhost:5000")
    print(f"LiveKit URL: {LIVEKIT_URL}")
    app.run(port=5000, debug=True)