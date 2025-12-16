# 🎯 Online Coding Interview Platform

A real-time collaborative coding interview platform built with React. Create unique interview sessions, share links with candidates, and watch them code in real-time with syntax highlighting and live code execution.

## ✨ Features

- **🔗 Unique Session Links** - Create and share unique interview session URLs
- **🔄 Real-time Collaboration** - See code changes instantly across all connected users
- **💻 Multi-language Support** - JavaScript, Python, Java, and C++ with syntax highlighting
- **▶️ Live Code Execution** - Run JavaScript directly in the browser (other languages require backend)
- **🎨 Beautiful UI** - Clean, modern interface with dark theme
- **📱 Responsive Design** - Works on desktop, tablet, and mobile devices
- **👥 Participant Counter** - See how many people are in the session
- **⚡ Fast Performance** - Built with Vite for optimal development and build speed

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

### Installation

1. Clone the repository:
```bash
cd interview-platform
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to:
```
http://localhost:3000
```

## 📁 Project Structure

```
interview-platform/
├── src/
│   ├── components/       # Reusable React components
│   ├── pages/           # Page components (Landing, Session)
│   │   ├── LandingPage.jsx
│   │   └── SessionPage.jsx
│   ├── hooks/           # Custom React hooks
│   │   └── useWebSocket.js
│   ├── services/        # API and business logic
│   │   ├── api.js       # REST API client
│   │   ├── websocket.js # WebSocket client
│   │   └── codeExecution.js # Browser code execution
│   ├── styles/          # CSS files
│   │   ├── LandingPage.css
│   │   └── SessionPage.css
│   ├── utils/           # Utility functions and constants
│   │   └── constants.js
│   ├── App.jsx          # Main app component with routing
│   ├── main.jsx         # App entry point
│   └── index.css        # Global styles
├── public/              # Static assets
├── package.json         # Dependencies and scripts
└── vite.config.js      # Vite configuration
```

## 🎮 How to Use

### For Interviewers

1. **Create a Session**
   - Visit the landing page
   - Click "Create New Interview"
   - Share the generated URL with your candidate

2. **Conduct the Interview**
   - Select the programming language
   - Write or watch code in real-time
   - Run code to see output
   - All participants see changes instantly

### For Candidates

1. **Join a Session**
   - Open the session URL shared by your interviewer
   - Or paste the session ID on the landing page
   - Start coding immediately

## 🧪 Running Tests

```bash
# Run all tests
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

## 🏗️ Building for Production

```bash
# Build the application
npm run build

# Preview the production build
npm run preview
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# WebSocket URL
VITE_WS_BASE_URL=ws://localhost:8000
```

### Customizing Languages

Edit `src/utils/constants.js` to add or modify supported languages:

```javascript
export const LANGUAGES = [
  {
    id: 'javascript',
    name: 'JavaScript',
    defaultCode: '// Your default code',
    canRunInBrowser: true,
  },
  // Add more languages here
];
```

## 🔌 Backend Integration

The frontend is designed to work with a FastAPI backend that provides:

### Expected Endpoints

- `POST /sessions` - Create new session
- `GET /sessions/{sessionId}` - Get session details
- `GET /languages` - List supported languages
- `POST /sessions/{sessionId}/execute` - Execute code (for non-JS languages)
- `WS /ws/sessions/{sessionId}` - WebSocket connection for real-time updates

### WebSocket Events

The platform uses these WebSocket events:

- `join_session` - User joins a session
- `leave_session` - User leaves a session
- `code_update` - Code changes
- `language_change` - Language selection changes
- `execute_code` - Code execution request
- `execution_result` - Code execution output
- `session_state` - Full session state sync

## 🎨 Key Components Explained

### LandingPage
- Entry point for users
- Create new sessions or join existing ones
- Simple, user-friendly interface

### SessionPage
- Main coding environment
- Monaco Editor for code editing
- Real-time synchronization via WebSockets
- Code execution and output display

### useWebSocket Hook
- Custom hook for WebSocket management
- Handles connection, reconnection, and events
- Provides simple API for components

### Code Execution Service
- Sandboxed JavaScript execution in iframe
- Captures console output
- Timeout protection (5 seconds)
- Error handling

## 🚦 Development Tips

### Running Without Backend

The app can run without a backend server:
- Session IDs are generated client-side
- JavaScript execution works in-browser
- WebSocket features will be limited

### Testing WebSocket Features

To test real-time collaboration:
1. Open multiple browser tabs
2. Join the same session
3. Type in one tab and see updates in others

### Debugging

- Check browser console for errors
- WebSocket status is shown in the header
- Network tab shows API/WS connections

## 📝 Code Style Guidelines

- Use functional components with hooks
- Keep components focused and small
- Add comments for complex logic
- Use meaningful variable names
- Follow React best practices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Submit a pull request

## 📄 License

MIT License - feel free to use this project for learning or commercial purposes.

## 🆘 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Change port in vite.config.js
server: {
  port: 3001  // Use different port
}
```

**WebSocket connection fails:**
- Check if backend is running
- Verify WebSocket URL in constants.js
- Check browser console for errors

**Code execution not working:**
- JavaScript runs in browser (always works)
- Other languages need backend API
- Check browser console for errors

## 📚 Learning Resources

This project demonstrates:
- React hooks and functional components
- Real-time WebSocket communication
- Monaco Editor integration
- Safe code execution in browser
- Responsive web design
- Testing with Vitest

Perfect for learning modern web development!

---

Built with ❤️ using React, Vite, and Monaco Editor