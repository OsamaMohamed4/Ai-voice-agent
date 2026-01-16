import React, { useState } from 'react';
import VoiceChat from './VoiceChat.js';
import './App.css';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [roomName, setRoomName] = useState('');

  const handleConnect = () => {
    if (roomName.trim()) {
      setIsConnected(true);
    }
  };

  const handleDisconnect = () => {
    setIsConnected(false);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>Voice Assistant</h1>
          <p className="subtitle">Powered by AI</p>
        </div>
      </header>

      <main className="app-main">
        {!isConnected ? (
          <div className="connect-container">
            <div className="connect-card">
              <div className="icon-container">
                <svg 
                  className="microphone-icon" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" 
                  />
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M19 10v2a7 7 0 0 1-14 0v-2" 
                  />
                  <line 
                    x1={12} 
                    y1={19} 
                    x2={12} 
                    y2={23} 
                    strokeLinecap="round" 
                    strokeWidth={2} 
                  />
                  <line 
                    x1={8} 
                    y1={23} 
                    x2={16} 
                    y2={23} 
                    strokeLinecap="round" 
                    strokeWidth={2} 
                  />
                </svg>
              </div>

              <h2>Start Voice Conversation</h2>
              <p className="description">
                Connect to start talking with your AI assistant
              </p>

              <div className="input-group">
                <input
                  type="text"
                  placeholder="Enter room name"
                  value={roomName}
                  onChange={(e) => setRoomName(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleConnect()}
                  className="room-input"
                />
              </div>

              <button 
                onClick={handleConnect} 
                className="connect-button"
                disabled={!roomName.trim()}
              >
                Join Voice Chat
              </button>

              <div className="info-text">
                <small>Your microphone will be activated after joining</small>
              </div>
            </div>
          </div>
        ) : (
          <VoiceChat 
            roomName={roomName} 
            onDisconnect={handleDisconnect} 
          />
        )}
      </main>

      <footer className="app-footer">
        <p>Real-time voice AI assistant</p>
      </footer>
    </div>
  );
}

export default App;