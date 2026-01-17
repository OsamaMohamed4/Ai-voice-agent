"""
Simple token server for LiveKit + File Upload for RAG
Run this separately to generate tokens for frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from livekit import api
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

# Upload configuration
UPLOAD_FOLDER = './documents'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx', 'md'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload document for RAG indexing"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file type
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'error': f'File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB'
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        print(f"✅ File uploaded: {filepath}")
        
        # Trigger RAG rebuild
        try:
            from rag_llamaindex import build_index
            print("🔄 Rebuilding RAG index...")
            build_index(force_rebuild=True)
            print("✅ RAG index rebuilt")
            
            return jsonify({
                'success': True,
                'message': f'File "{filename}" uploaded and indexed successfully',
                'filename': filename,
                'size': file_size
            })
            
        except Exception as e:
            print(f"⚠️ File saved but RAG rebuild failed: {e}")
            return jsonify({
                'success': True,
                'message': f'File uploaded but indexing failed: {str(e)}',
                'filename': filename
            }), 500
        
    except Exception as e:
        print(f"Error uploading file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List uploaded documents"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath)
                })
        
        return jsonify({
            'documents': files,
            'count': len(files)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Token Server + Upload API")
    print("=" * 60)
    print(f"📡 LiveKit URL: {LIVEKIT_URL}")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"📋 Allowed files: {', '.join(ALLOWED_EXTENSIONS)}")
    print(f"📊 Max file size: {MAX_FILE_SIZE / 1024 / 1024}MB")
    print("=" * 60)
    print()
    app.run(port=5000, debug=True)