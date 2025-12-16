# 🚀 Browser-Based Code Execution with WebAssembly

## Overview

This Online Coding Interview Platform now features **secure browser-based code execution** using WebAssembly (WASM) technology. Code runs entirely in the user's browser, eliminating server-side security risks while providing a fast, responsive coding experience.

## ✨ Key Features

### Supported Languages

| Language | Technology | Status | Notes |
|----------|------------|--------|-------|
| **JavaScript** | Native Browser API | ✅ Ready | Runs in sandboxed iframe |
| **TypeScript** | TypeScript Compiler | ✅ Ready | Transpiled to JS in-browser |
| **Python** | Pyodide (WASM) | ✅ Ready | Full Python 3.x with NumPy, Matplotlib |
| **HTML** | Preview Generation | ✅ Ready | Rendered in sandboxed context |
| **CSS** | Validation Engine | ✅ Ready | Real-time CSS validation |
| Java | TeaVM/CheerpJ | 🚧 Planned | Syntax highlighting only |
| C++ | Emscripten | 🚧 Planned | Syntax highlighting only |
| Go | GopherJS/TinyGo | 🚧 Planned | Syntax highlighting only |
| Rust | wasm-bindgen | 🚧 Planned | Syntax highlighting only |

## 🔒 Security Architecture

### JavaScript Execution
- **Sandboxed iframe** with restricted permissions
- No access to parent window or cookies
- Execution timeout (5 seconds default)
- Console output capture and sanitization

### Python Execution (Pyodide)
- **WebAssembly isolation** - runs in browser's WASM sandbox
- **Web Worker** - executes in separate thread, non-blocking
- Memory and CPU limits enforced by browser
- No filesystem or network access
- 30-second timeout for complex computations

### TypeScript Execution
- In-browser transpilation using official TypeScript compiler
- Transpiled to JavaScript, then executed in sandbox
- Full type checking and error reporting

## 🏗️ Technical Implementation

### File Structure
```
interview-platform/
├── public/
│   └── pyodide-worker.js      # Web Worker for Python execution
├── src/services/
│   └── browserExecution.js    # Unified execution service
└── src/pages/
    └── SessionPage.jsx         # UI integration
```

### Core Components

#### 1. Browser Execution Service (`browserExecution.js`)
```javascript
class BrowserExecutionService {
  // Unified interface for all languages
  async execute(code, language, options)
  
  // Language-specific handlers
  async executeJavaScript(code, timeLimit)
  async executeTypeScript(code, timeLimit)
  async executePython(code, timeLimit)
  async executeHTML(code)
  async executeCSS(code)
}
```

#### 2. Pyodide Web Worker (`pyodide-worker.js`)
- Loads Python interpreter in background thread
- Pre-loads common packages (NumPy, Matplotlib)
- Handles stdout/stderr capture
- Implements execution timeout

#### 3. UI Integration (`SessionPage.jsx`)
- Loading indicators for Python initialization
- Real-time execution feedback
- Error handling and display
- Language-specific execution options

## 📦 Dependencies

### Frontend
```json
{
  "@monaco-editor/react": "^4.7.0",  // Code editor with syntax highlighting
  // Pyodide loaded via CDN (24MB compressed)
  // TypeScript compiler loaded via CDN (5MB)
}
```

### CDN Resources
- **Pyodide**: `https://cdn.jsdelivr.net/pyodide/v0.24.1/full/`
- **TypeScript**: `https://unpkg.com/typescript@5.0.4/lib/typescript.js`

## 🚀 Usage Examples

### JavaScript
```javascript
// Runs natively in browser
console.log("Hello, World!");
const result = [1,2,3].map(x => x * 2);
console.log(result); // [2, 4, 6]
```

### Python
```python
# Runs via Pyodide WebAssembly
print("Hello from Python!")
import numpy as np
arr = np.array([1, 2, 3])
print(f"Mean: {arr.mean()}")
```

### TypeScript
```typescript
// Transpiled to JavaScript in-browser
interface User {
  name: string;
  age: number;
}
const user: User = { name: "Alice", age: 30 };
console.log(user);
```

## 🎯 Performance

| Language | First Run | Subsequent Runs | Memory Usage |
|----------|-----------|-----------------|--------------|
| JavaScript | < 10ms | < 10ms | Minimal |
| TypeScript | 200-500ms | 50-100ms | ~5MB (compiler) |
| Python | 10-15s | < 100ms | ~50MB (Pyodide) |

## 🔧 Configuration

### Execution Timeouts
```javascript
// In browserExecution.js
const TIMEOUTS = {
  javascript: 5000,   // 5 seconds
  typescript: 5000,   // 5 seconds
  python: 30000,      // 30 seconds (includes loading time)
  html: 1000,         // 1 second
  css: 1000           // 1 second
};
```

### Python Packages
Pre-loaded packages in Pyodide:
- numpy
- matplotlib
- micropip (for installing additional packages)

To add more packages:
```javascript
// In pyodide-worker.js
await pyodide.loadPackage(["pandas", "scipy"]);
```

## 🧪 Testing

### Manual Testing
1. Open the platform: http://localhost:3000
2. Create a new session
3. Select a language from the dropdown
4. Write code and click "Run"
5. Verify output appears correctly

### Test File
Use `test-execution.html` for standalone testing:
```bash
# Open in browser
open test-execution.html
```

## 🐛 Troubleshooting

### Python Not Loading
- **Issue**: "Pyodide failed to load"
- **Solution**: Check internet connection (CDN access required)
- **Solution**: Clear browser cache and reload

### TypeScript Errors
- **Issue**: "TypeScript compiler not loaded"
- **Solution**: Ensure CDN is accessible
- **Solution**: Check browser console for network errors

### Execution Timeout
- **Issue**: Code execution times out
- **Solution**: Optimize code or increase timeout in `browserExecution.js`

## 🔮 Future Enhancements

### Planned Features
1. **More Languages**
   - Java via TeaVM or CheerpJ
   - C++ via Emscripten
   - Go via TinyGo
   - Rust via wasm-bindgen

2. **Advanced Features**
   - stdin support for interactive programs
   - File I/O simulation
   - Multiple file support
   - Package installation UI

3. **Performance**
   - Pyodide caching in IndexedDB
   - Lazy loading of language runtimes
   - Shared ArrayBuffer for faster execution

4. **Developer Tools**
   - Debugging support
   - Performance profiling
   - Memory usage tracking
   - Execution history

## 📚 Resources

- [Pyodide Documentation](https://pyodide.org/en/stable/)
- [TypeScript Playground](https://www.typescriptlang.org/play)
- [WebAssembly Security](https://webassembly.org/docs/security/)
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)

## 🤝 Contributing

To add support for a new language:

1. Add language configuration in `constants.js`
2. Implement execution handler in `browserExecution.js`
3. Add UI support in `SessionPage.jsx`
4. Update this documentation
5. Add tests

## 📄 License

MIT License - See LICENSE file for details

---

**Note**: Server-side execution has been disabled by default for security. To re-enable it, set `enable_server_execution: true` in `backend/app/core/config.py`.

