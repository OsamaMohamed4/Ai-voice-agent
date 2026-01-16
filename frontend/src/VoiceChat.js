import React, { useState, useEffect, useRef } from 'react';
import { 
  LiveKitRoom, 
  RoomAudioRenderer,
  useVoiceAssistant,
  BarVisualizer
} from '@livekit/components-react';
import '@livekit/components-styles';

function VoiceChat({ roomName, onDisconnect }) {
  const [token, setToken] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [transcript, setTranscript] = useState([]);

  useEffect(() => {
    // Generate access token
    generateToken();
  }, []);

  const generateToken = async () => {
    try {
      // Call backend token server
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
      />
      <RoomAudioRenderer />
    </LiveKitRoom>
  );
}

function VoiceInterface({ transcript, setTranscript, onDisconnect }) {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const addToTranscript = (speaker, text) => {
    setTranscript(prev => [...prev, { speaker, text, timestamp: new Date() }]);
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
                <p>Start speaking anytime</p>
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
          <p><strong>Tips:</strong> Speak clearly and naturally. The assistant can answer questions about products, pricing, and support.</p>
        </div>
      </div>
    </div>
  );
}

export default VoiceChat;