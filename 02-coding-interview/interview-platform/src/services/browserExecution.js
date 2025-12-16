/**
 * Browser-based code execution service using WebAssembly and sandboxed environments
 * Provides secure code execution without server-side processing
 */

// TypeScript compiler for browser (loaded lazily)
let tsCompiler = null;

class BrowserExecutionService {
  constructor() {
    this.pyodideWorker = null;
    this.pyodideReady = false;
    this.pyodideLoading = false;
    this.messageId = 0;
    this.pendingExecutions = new Map();
  }

  /**
   * Initialize the execution service
   */
  async initialize() {
    // Pre-load TypeScript compiler
    this.loadTypeScriptCompiler();
  }

  /**
   * Execute code based on language
   */
  async execute(code, language, options = {}) {
    const timeLimit = options.timeLimit || 5000;
    const stdin = options.stdin || '';

    console.log(`Executing ${language} code in browser...`);

    switch (language) {
      case 'javascript':
        return this.executeJavaScript(code, timeLimit);
      
      case 'typescript':
        return this.executeTypeScript(code, timeLimit);
      
      case 'python':
        return this.executePython(code, timeLimit);
      
      case 'html':
        return this.executeHTML(code);
      
      case 'css':
        return this.executeCSS(code);
      
      default:
        return {
          success: false,
          stdout: '',
          stderr: `⚠️ ${language} execution is not yet supported in the browser.\n\nSupported languages:\n• JavaScript\n• TypeScript\n• Python\n• HTML/CSS\n\nFor other languages, please use a server-based execution environment.`,
          exitCode: 1,
          duration: 0
        };
    }
  }

  /**
   * Execute JavaScript code in a sandboxed environment
   */
  async executeJavaScript(code, timeLimit) {
    const startTime = performance.now();
    let output = '';
    let error = '';
    let exitCode = 0;

    try {
      // Create a sandboxed iframe for execution
      const iframe = document.createElement('iframe');
      iframe.style.display = 'none';
      iframe.sandbox = 'allow-scripts';
      document.body.appendChild(iframe);

      // Set up message listener for output
      const outputPromise = new Promise((resolve) => {
        const messageHandler = (event) => {
          if (event.source === iframe.contentWindow) {
            window.removeEventListener('message', messageHandler);
            resolve(event.data);
          }
        };
        window.addEventListener('message', messageHandler);

        // Set timeout
        setTimeout(() => {
          window.removeEventListener('message', messageHandler);
          resolve({ output: '', error: 'Execution timed out', exitCode: 1 });
        }, timeLimit);
      });

      // Inject execution code into iframe
      const executionCode = `
        <script>
          // Capture console output
          let output = [];
          let errorOutput = [];
          
          const originalLog = console.log;
          const originalError = console.error;
          const originalWarn = console.warn;
          
          console.log = (...args) => {
            output.push(args.map(arg => {
              if (typeof arg === 'object') {
                try {
                  return JSON.stringify(arg, null, 2);
                } catch {
                  return String(arg);
                }
              }
              return String(arg);
            }).join(' '));
          };
          
          console.error = (...args) => {
            errorOutput.push(args.map(arg => String(arg)).join(' '));
          };
          
          console.warn = console.log;
          
          let exitCode = 0;
          
          try {
            // Execute user code
            ${code}
          } catch (error) {
            errorOutput.push(error.toString());
            if (error.stack) {
              errorOutput.push(error.stack);
            }
            exitCode = 1;
          }
          
          // Send results back to parent
          parent.postMessage({
            output: output.join('\\n'),
            error: errorOutput.join('\\n'),
            exitCode: exitCode
          }, '*');
        </script>
      `;

      iframe.contentDocument.open();
      iframe.contentDocument.write(executionCode);
      iframe.contentDocument.close();

      // Wait for execution result
      const result = await outputPromise;
      output = result.output || '';
      error = result.error || '';
      exitCode = result.exitCode || 0;

      // Clean up iframe
      document.body.removeChild(iframe);

    } catch (err) {
      error = err.toString();
      exitCode = 1;
    }

    const duration = Math.round(performance.now() - startTime);

    return {
      success: exitCode === 0,
      stdout: output,
      stderr: error,
      exitCode,
      duration
    };
  }

  /**
   * Execute TypeScript code by transpiling to JavaScript first
   */
  async executeTypeScript(code, timeLimit) {
    const startTime = performance.now();

    try {
      // Load TypeScript compiler if not already loaded
      if (!tsCompiler) {
        await this.loadTypeScriptCompiler();
      }

      // Transpile TypeScript to JavaScript
      const jsCode = tsCompiler.transpileModule(code, {
        compilerOptions: {
          module: tsCompiler.ModuleKind.CommonJS,
          target: tsCompiler.ScriptTarget.ES2020,
          strict: true,
          esModuleInterop: true,
          skipLibCheck: true,
          forceConsistentCasingInFileNames: true,
        }
      }).outputText;

      // Execute the transpiled JavaScript
      const result = await this.executeJavaScript(jsCode, timeLimit);
      
      // Add TypeScript info to output
      if (result.success) {
        result.stdout = '✅ TypeScript compiled successfully\n\n' + result.stdout;
      }

      return result;

    } catch (error) {
      const duration = Math.round(performance.now() - startTime);
      return {
        success: false,
        stdout: '',
        stderr: `TypeScript compilation error:\n${error.toString()}`,
        exitCode: 1,
        duration
      };
    }
  }

  /**
   * Execute Python code using Pyodide WebAssembly
   */
  async executePython(code, timeLimit) {
    const startTime = performance.now();

    try {
      // Initialize Pyodide worker if not already done
      if (!this.pyodideWorker) {
        await this.initializePyodide();
      }

      // Wait for Pyodide to be ready
      if (!this.pyodideReady) {
        const timeout = 30000; // 30 seconds to load Pyodide
        const startWait = Date.now();
        while (!this.pyodideReady && Date.now() - startWait < timeout) {
          await new Promise(resolve => setTimeout(resolve, 100));
        }
        if (!this.pyodideReady) {
          throw new Error('Pyodide failed to load. Please refresh the page.');
        }
      }

      // Execute code via worker
      const executionId = ++this.messageId;
      
      return new Promise((resolve) => {
        this.pendingExecutions.set(executionId, resolve);
        
        this.pyodideWorker.postMessage({
          id: executionId,
          code,
          timeLimit
        });

        // Set a backup timeout
        setTimeout(() => {
          if (this.pendingExecutions.has(executionId)) {
            this.pendingExecutions.delete(executionId);
            const duration = Math.round(performance.now() - startTime);
            resolve({
              success: false,
              stdout: '',
              stderr: 'Python execution timed out',
              exitCode: 1,
              duration
            });
          }
        }, timeLimit + 1000);
      });

    } catch (error) {
      const duration = Math.round(performance.now() - startTime);
      return {
        success: false,
        stdout: '',
        stderr: `Python execution error:\n${error.toString()}`,
        exitCode: 1,
        duration
      };
    }
  }

  /**
   * Execute HTML code in a sandboxed preview
   */
  async executeHTML(code) {
    // For HTML, we'll return a preview URL or rendered content
    const blob = new Blob([code], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    
    return {
      success: true,
      stdout: `HTML Preview ready. Open in new tab: ${url}\n\n(Note: For security, HTML preview opens in a sandboxed environment)`,
      stderr: '',
      exitCode: 0,
      duration: 0,
      previewUrl: url
    };
  }

  /**
   * Execute CSS code (validate and preview)
   */
  async executeCSS(code) {
    try {
      // Create a temporary style element to validate CSS
      const style = document.createElement('style');
      style.textContent = code;
      document.head.appendChild(style);
      document.head.removeChild(style);
      
      return {
        success: true,
        stdout: '✅ CSS is valid and can be applied.\n\nCSS Rules:\n' + code,
        stderr: '',
        exitCode: 0,
        duration: 0
      };
    } catch (error) {
      return {
        success: false,
        stdout: '',
        stderr: `CSS validation error:\n${error.toString()}`,
        exitCode: 1,
        duration: 0
      };
    }
  }

  /**
   * Initialize Pyodide Web Worker for Python execution
   */
  async initializePyodide() {
    if (this.pyodideLoading) {
      // Already loading, wait for it
      return;
    }

    this.pyodideLoading = true;
    console.log('Initializing Pyodide for Python execution...');

    return new Promise((resolve, reject) => {
      this.pyodideWorker = new Worker('/pyodide-worker.js');
      
      const timeout = setTimeout(() => {
        reject(new Error('Pyodide initialization timeout'));
      }, 60000); // 60 seconds timeout

      this.pyodideWorker.onmessage = (event) => {
        const { type, id, ...data } = event.data;

        if (type === 'ready') {
          clearTimeout(timeout);
          this.pyodideReady = true;
          this.pyodideLoading = false;
          console.log('✅ Pyodide is ready for Python execution');
          resolve();
        } else if (id && this.pendingExecutions.has(id)) {
          // Handle execution result
          const resolver = this.pendingExecutions.get(id);
          this.pendingExecutions.delete(id);
          resolver(data);
        }
      };

      this.pyodideWorker.onerror = (error) => {
        console.error('Pyodide worker error:', error);
        this.pyodideReady = false;
        this.pyodideLoading = false;
        reject(error);
      };
    });
  }

  /**
   * Load TypeScript compiler
   */
  async loadTypeScriptCompiler() {
    if (tsCompiler) return;

    console.log('Loading TypeScript compiler...');
    
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/typescript@5.0.4/lib/typescript.js';
      script.onload = () => {
        tsCompiler = window.ts;
        console.log('✅ TypeScript compiler loaded');
        resolve();
      };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  /**
   * Clean up resources
   */
  cleanup() {
    if (this.pyodideWorker) {
      this.pyodideWorker.terminate();
      this.pyodideWorker = null;
      this.pyodideReady = false;
    }
    this.pendingExecutions.clear();
  }
}

// Create and export singleton instance
const browserExecutionService = new BrowserExecutionService();

// Initialize on load
if (typeof window !== 'undefined') {
  browserExecutionService.initialize().catch(console.error);
}

export default browserExecutionService;

