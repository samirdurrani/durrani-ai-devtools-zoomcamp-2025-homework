import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import '../styles/LandingPage.css';

// Landing page where users can create or join interview sessions
export default function LandingPage() {
  const [isCreating, setIsCreating] = useState(false);
  const [joinUrl, setJoinUrl] = useState('');
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Handle creating a new interview session
  const handleCreateSession = async () => {
    setIsCreating(true);
    setError(null);
    
    try {
      // Call backend to create a new session
      const response = await apiService.createSession();
      
      // Navigate to the session page
      navigate(`/session/${response.sessionId}`);
    } catch (err) {
      // If backend is not available, create a client-side session ID
      // This allows the app to work even without a backend
      const fallbackSessionId = generateSessionId();
      console.warn('Backend not available, using client-side session:', fallbackSessionId);
      navigate(`/session/${fallbackSessionId}`);
    } finally {
      setIsCreating(false);
    }
  };

  // Handle joining an existing session
  const handleJoinSession = (e) => {
    e.preventDefault();
    setError(null);
    
    if (!joinUrl.trim()) {
      setError('Please enter a valid session URL');
      return;
    }
    
    // Extract session ID from the URL
    const sessionId = extractSessionId(joinUrl);
    
    if (!sessionId) {
      setError('Invalid session URL. Please check and try again.');
      return;
    }
    
    // Navigate to the session
    navigate(`/session/${sessionId}`);
  };

  // Generate a random session ID (fallback when backend is not available)
  const generateSessionId = () => {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  };

  // Extract session ID from a URL
  const extractSessionId = (url) => {
    // Handle different URL formats
    // Full URL: http://localhost:3000/session/abc123
    // Relative URL: /session/abc123
    // Just the ID: abc123
    
    const patterns = [
      /\/session\/([a-zA-Z0-9-_]+)/,  // Match /session/ID
      /^[a-zA-Z0-9-_]+$/,              // Match just the ID
    ];
    
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) {
        return match[1] || match[0];
      }
    }
    
    return null;
  };

  return (
    <div className="landing-page">
      <div className="landing-container">
        <header className="landing-header">
          <h1>🎯 Coding Interview Platform</h1>
          <p className="subtitle">
            Real-time collaborative coding interviews made simple
          </p>
        </header>

        <div className="landing-content">
          <div className="action-card">
            <h2>Start a New Interview</h2>
            <p>Create a unique session and share the link with candidates</p>
            <button
              onClick={handleCreateSession}
              disabled={isCreating}
              className="btn btn-primary"
            >
              {isCreating ? 'Creating...' : '🚀 Create New Interview'}
            </button>
          </div>

          <div className="divider">
            <span>OR</span>
          </div>

          <div className="action-card">
            <h2>Join Existing Interview</h2>
            <p>Enter the session URL or ID to join an ongoing interview</p>
            <form onSubmit={handleJoinSession}>
              <input
                type="text"
                placeholder="Paste session URL or ID here..."
                value={joinUrl}
                onChange={(e) => setJoinUrl(e.target.value)}
                className="input-field"
              />
              <button type="submit" className="btn btn-secondary">
                🔗 Join Session
              </button>
            </form>
          </div>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}
        </div>

        <footer className="landing-footer">
          <div className="features">
            <div className="feature">
              <span className="feature-icon">💻</span>
              <span>Multi-language Support</span>
            </div>
            <div className="feature">
              <span className="feature-icon">🔄</span>
              <span>Real-time Collaboration</span>
            </div>
            <div className="feature">
              <span className="feature-icon">▶️</span>
              <span>Live Code Execution</span>
            </div>
            <div className="feature">
              <span className="feature-icon">🎨</span>
              <span>Syntax Highlighting</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
