// Configuration constants for the application

// Backend API configuration
// Change these values to match your backend server
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'

// Supported programming languages
// Each language has a name, id (used by Monaco editor), and default code template
export const LANGUAGES = [
  {
    id: 'javascript',
    name: 'JavaScript',
    defaultCode: '// Welcome to the coding interview platform!\n// Start writing your JavaScript code here\n\nfunction solution() {\n  // Your code here\n  console.log("Hello, World!");\n}\n\nsolution();',
    canRunInBrowser: true,
  },
  {
    id: 'python',
    name: 'Python',
    defaultCode: '# Welcome to the coding interview platform!\n# Start writing your Python code here\n\ndef solution():\n    # Your code here\n    print("Hello, World!")\n\nsolution()',
    canRunInBrowser: false, // Python needs backend execution
  },
  {
    id: 'java',
    name: 'Java',
    defaultCode: '// Welcome to the coding interview platform!\n// Start writing your Java code here\n\npublic class Main {\n    public static void main(String[] args) {\n        // Your code here\n        System.out.println("Hello, World!");\n    }\n}',
    canRunInBrowser: false,
  },
  {
    id: 'cpp',
    name: 'C++',
    defaultCode: '// Welcome to the coding interview platform!\n// Start writing your C++ code here\n\n#include <iostream>\nusing namespace std;\n\nint main() {\n    // Your code here\n    cout << "Hello, World!" << endl;\n    return 0;\n}',
    canRunInBrowser: false,
  },
]

// WebSocket event types
export const WS_EVENTS = {
  JOIN_SESSION: 'join_session',
  LEAVE_SESSION: 'leave_session',
  CODE_UPDATE: 'code_update',
  LANGUAGE_CHANGE: 'language_change',
  EXECUTE_CODE: 'execute_code',
  EXECUTION_RESULT: 'execution_result',
  USER_JOINED: 'user_joined',
  USER_LEFT: 'user_left',
  SESSION_STATE: 'session_state',
  ERROR: 'error',
}
