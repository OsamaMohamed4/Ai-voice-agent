import React, { useState, useEffect, useRef } from 'react';
import { 
  LiveKitRoom, 
  RoomAudioRenderer,
} from '@livekit/components-react';
import '@livekit/components-styles';

function VoiceChat({ roomName, onDisconnect }) {
  const [token, setToken] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [transcript, setTranscript] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  useEffect(() => {
    generateToken();
    fetchUploadedFiles();
  }, []);

  const generateToken = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          roomName: roomName,
          participantName: 'User-' + Math.random().toString(36).substring(7),
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get token from server');
      }

      const data = await response.json();
      setToken(data.token);
      setIsLoading(false);
    } catch (error) {
      console.error('Error generating token:', error);
      alert('Cannot connect to server. Make sure backend is running on http://localhost:5000');
      setIsLoading(false);
    }
  };

  const fetchUploadedFiles = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/documents');
      const data = await response.json();
      setUploadedFiles(data.documents || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loader"></div>
        <p>Connecting to voice assistant...</p>
      </div>
    );
  }

  return (
    <LiveKitRoom
      serverUrl={process.env.REACT_APP_LIVEKIT_URL}
      token={token}
      connect={true}
      audio={true}
      video={false}
      className="voice-room"
    >
      <VoiceInterface 
        transcript={transcript}
        setTranscript={setTranscript}
        onDisconnect={onDisconnect}
        uploadedFiles={uploadedFiles}
        onFileUploaded={fetchUploadedFiles}
      />
      <RoomAudioRenderer />
    </LiveKitRoom>
  );
}

function VoiceInterface({ transcript, setTranscript, onDisconnect, uploadedFiles, onFileUploaded }) {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const fileInputRef = useRef(null);

  const addToTranscript = (speaker, text) => {
    setTranscript(prev => [...prev, { speaker, text, timestamp: new Date() }]);
  };

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|txt|doc|docx|md)$/i)) {
      setUploadMessage('❌ File type not allowed. Use PDF, TXT, DOC, or DOCX');
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setUploadMessage('❌ File too large. Max size: 10MB');
      return;
    }

    setIsUploading(true);
    setUploadMessage('📤 Uploading...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setUploadMessage(`✅ ${data.message}`);
        onFileUploaded(); // Refresh file list
        
        // Clear message after 3 seconds
        setTimeout(() => setUploadMessage(''), 3000);
      } else {
        setUploadMessage(`❌ ${data.error}`);
      }
    } catch (error) {
      setUploadMessage(`❌ Upload failed: ${error.message}`);
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="voice-interface">
      <div className="voice-header">
        <div className="status-indicator">
          <div className={`status-dot ${isListening ? 'active' : ''}`}></div>
          <span>{isListening ? 'Listening...' : 'Ready'}</span>
        </div>
        
        <button onClick={onDisconnect} className="disconnect-button">
          End Session
        </button>
      </div>

      {/* Upload Section */}
      <div className="upload-section">
        <div className="upload-header">
          <h4>📁 Upload Documents</h4>
          <label className="upload-button">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.doc,.docx,.md"
              onChange={handleFileSelect}
              disabled={isUploading}
              style={{ display: 'none' }}
            />
            {isUploading ? '⏳ Uploading...' : '📤 Upload File'}
          </label>
        </div>
        
        {uploadMessage && (
          <div className={`upload-message ${uploadMessage.includes('✅') ? 'success' : 'error'}`}>
            {uploadMessage}
          </div>
        )}

        {uploadedFiles.length > 0 && (
          <div className="uploaded-files">
            <p className="files-count">📚 {uploadedFiles.length} document(s) indexed</p>
            <div className="files-list">
              {uploadedFiles.slice(0, 3).map((file, index) => (
                <div key={index} className="file-item">
                  📄 {file.name}
                </div>
              ))}
              {uploadedFiles.length > 3 && (
                <div className="file-item">+ {uploadedFiles.length - 3} more...</div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="voice-content">
        <div className="visualizer-container">
          <div className="pulse-circle">
            <div className="pulse-ring"></div>
            <div className="pulse-ring"></div>
            <div className="pulse-ring"></div>
            
            <svg 
              className="center-icon" 
              viewBox="0 0 24 24" 
              fill="currentColor"
            >
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8" />
            </svg>
          </div>

          <div className="status-text">
            {isSpeaking ? (
              <>
                <h3>Assistant is speaking...</h3>
                <p>Listening to response</p>
              </>
            ) : isListening ? (
              <>
                <h3>I'm listening</h3>
                <p>Speak naturally</p>
              </>
            ) : (
              <>
                <h3>Ready to talk</h3>
                <p>Ask me anything about the uploaded documents</p>
              </>
            )}
          </div>
        </div>

        <div className="transcript-container">
          <h4>Conversation</h4>
          <div className="transcript-list">
            {transcript.length === 0 ? (
              <div className="empty-state">
                <p>Your conversation will appear here</p>
              </div>
            ) : (
              transcript.map((item, index) => (
                <div 
                  key={index} 
                  className={`transcript-item ${item.speaker === 'user' ? 'user' : 'assistant'}`}
                >
                  <div className="transcript-speaker">
                    {item.speaker === 'user' ? 'You' : 'Assistant'}
                  </div>
                  <div className="transcript-text">{item.text}</div>
                  <div className="transcript-time">
                    {item.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="voice-footer">
        <div className="tips">
          <p><strong>💡 Tips:</strong> Upload documents (PDF/TXT) and ask questions about them. The AI will search and provide answers based on your documents.</p>
        </div>
      </div>
    </div>
  );
}

export default VoiceChat;