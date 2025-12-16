import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { useWebSocket } from '../hooks/useWebSocket';
import { LANGUAGES, WS_EVENTS } from '../utils/constants';
import { executeJavaScript, formatExecutionResult } from '../services/codeExecution';
import { apiService } from '../services/api';
import '../styles/SessionPage.css';

// Main session page with collaborative code editor
export default function SessionPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const editorRef = useRef(null);
  const isRemoteUpdate = useRef(false);
  
  // State management
  const [code, setCode] = useState(LANGUAGES[0].defaultCode);
  const [language, setLanguage] = useState(LANGUAGES[0].id);
  const [output, setOutput] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [sessionUrl, setSessionUrl] = useState('');
  const [isCopied, setIsCopied] = useState(false);
  
  // WebSocket connection
  const {
    isConnected,
    participants,
    connectionError,
    sendCodeUpdate,
    sendLanguageChange,
    sendExecuteCode,
    subscribe,
  } = useWebSocket(sessionId);

  // Generate session URL on mount
  useEffect(() => {
    const url = `${window.location.origin}/session/${sessionId}`;
    setSessionUrl(url);
  }, [sessionId]);

  // Subscribe to WebSocket events
  useEffect(() => {
    // Listen for code updates from other users
    const unsubscribeCode = subscribe(WS_EVENTS.CODE_UPDATE, (data) => {
      if (data.code !== undefined) {
        isRemoteUpdate.current = true;
        setCode(data.code);
        
        // Update editor content if it exists
        if (editorRef.current) {
          const model = editorRef.current.getModel();
          if (model) {
            model.setValue(data.code);
          }
        }
        
        // Reset flag after a short delay
        setTimeout(() => {
          isRemoteUpdate.current = false;
        }, 100);
      }
    });

    // Listen for language changes from other users
    const unsubscribeLanguage = subscribe(WS_EVENTS.LANGUAGE_CHANGE, (data) => {
      if (data.language) {
        setLanguage(data.language);
        // Update code template if switching languages
        const newLang = LANGUAGES.find(l => l.id === data.language);
        if (newLang && !code.trim()) {
          setCode(newLang.defaultCode);
        }
      }
    });

    // Listen for execution results
    const unsubscribeExecution = subscribe(WS_EVENTS.EXECUTION_RESULT, (data) => {
      if (data.result) {
        const formatted = formatExecutionResult(data.result);
        setOutput(formatted);
      }
    });

    // Listen for session state updates (when joining an existing session)
    const unsubscribeState = subscribe(WS_EVENTS.SESSION_STATE, (data) => {
      if (data.code !== undefined) {
        setCode(data.code);
      }
      if (data.language) {
        setLanguage(data.language);
      }
    });

    // Cleanup subscriptions
    return () => {
      unsubscribeCode();
      unsubscribeLanguage();
      unsubscribeExecution();
      unsubscribeState();
    };
  }, [subscribe]);

  // Handle code changes in the editor
  const handleCodeChange = useCallback((value) => {
    // Ignore remote updates to avoid echo
    if (isRemoteUpdate.current) {
      return;
    }
    
    setCode(value || '');
    
    // Send update to other users via WebSocket
    if (isConnected) {
      sendCodeUpdate(value || '', language);
    }
  }, [isConnected, language, sendCodeUpdate]);

  // Handle language change
  const handleLanguageChange = useCallback((e) => {
    const newLanguage = e.target.value;
    setLanguage(newLanguage);
    
    // Update default code if current code is empty or default
    const oldLang = LANGUAGES.find(l => l.id === language);
    const newLang = LANGUAGES.find(l => l.id === newLanguage);
    
    if (oldLang && newLang && (code === oldLang.defaultCode || !code.trim())) {
      setCode(newLang.defaultCode);
      if (isConnected) {
        sendCodeUpdate(newLang.defaultCode, newLanguage);
      }
    }
    
    // Send language change to other users
    if (isConnected) {
      sendLanguageChange(newLanguage);
    }
  }, [code, language, isConnected, sendCodeUpdate, sendLanguageChange]);

  // Handle code execution
  const handleExecuteCode = async () => {
    setIsExecuting(true);
    setOutput('Running code...');
    
    try {
      const currentLang = LANGUAGES.find(l => l.id === language);
      
      if (currentLang?.canRunInBrowser && language === 'javascript') {
        // Execute JavaScript locally in the browser
        const result = await executeJavaScript(code);
        const formatted = formatExecutionResult(result);
        setOutput(formatted);
        
        // Share result with other users
        if (isConnected) {
          sendExecuteCode(code, language);
        }
      } else {
        // Execute on backend for other languages
        try {
          const result = await apiService.executeCode(sessionId, code, language);
          const formatted = formatExecutionResult(result);
          setOutput(formatted);
        } catch (error) {
          setOutput(`❌ Error: Cannot execute ${language} code. Backend service required.\n\nPlease ensure the backend server is running.`);
        }
      }
    } catch (error) {
      setOutput(`❌ Error: ${error.message}`);
    } finally {
      setIsExecuting(false);
    }
  };

  // Copy session URL to clipboard
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(sessionUrl);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Handle editor mount
  const handleEditorMount = (editor) => {
    editorRef.current = editor;
  };

  return (
    <div className="session-page">
      <header className="session-header">
        <div className="header-left">
          <button onClick={() => navigate('/')} className="btn-back">
            ← Back
          </button>
          <h1>Coding Interview Session</h1>
        </div>
        
        <div className="header-center">
          <div className="session-info">
            <input
              type="text"
              value={sessionUrl}
              readOnly
              className="url-input"
            />
            <button onClick={copyToClipboard} className="btn-copy">
              {isCopied ? '✓ Copied!' : '📋 Copy Link'}
            </button>
          </div>
        </div>
        
        <div className="header-right">
          <div className="connection-status">
            <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
            {isConnected ? 'Connected' : connectionError || 'Connecting...'}
          </div>
          <div className="participants">
            👥 {participants || 1} participant{participants !== 1 ? 's' : ''}
          </div>
        </div>
      </header>

      <div className="session-content">
        <div className="editor-panel">
          <div className="editor-toolbar">
            <select 
              value={language} 
              onChange={handleLanguageChange}
              className="language-selector"
            >
              {LANGUAGES.map(lang => (
                <option key={lang.id} value={lang.id}>
                  {lang.name}
                </option>
              ))}
            </select>
            
            <button
              onClick={handleExecuteCode}
              disabled={isExecuting || !code.trim()}
              className="btn-run"
            >
              {isExecuting ? '⏳ Running...' : '▶️ Run Code'}
            </button>
          </div>
          
          <div className="editor-container">
            <Editor
              height="100%"
              language={language}
              value={code}
              onChange={handleCodeChange}
              onMount={handleEditorMount}
              theme="vs-dark"
              options={{
                fontSize: 14,
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                wordWrap: 'on',
                automaticLayout: true,
                tabSize: 2,
                insertSpaces: true,
              }}
            />
          </div>
        </div>

        <div className="output-panel">
          <div className="output-header">
            <h3>📤 Output</h3>
            <button 
              onClick={() => setOutput('')}
              className="btn-clear"
              disabled={!output}
            >
              Clear
            </button>
          </div>
          <div className="output-content">
            <pre>{output || 'Output will appear here after running the code...'}</pre>
          </div>
        </div>
      </div>
    </div>
  );
}
