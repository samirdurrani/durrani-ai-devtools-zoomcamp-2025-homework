import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import SessionPage from './pages/SessionPage';
import './App.css';

// Main application component with routing
function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          {/* Landing page - create or join sessions */}
          <Route path="/" element={<LandingPage />} />
          
          {/* Session page - collaborative coding */}
          <Route path="/session/:sessionId" element={<SessionPage />} />
          
          {/* Redirect any unknown routes to landing page */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;