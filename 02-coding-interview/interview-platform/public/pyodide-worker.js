// Web Worker for running Python code with Pyodide
// This runs in a separate thread to avoid blocking the main UI

importScripts("https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js");

let pyodideReadyPromise = null;
let pyodide = null;

// Initialize Pyodide
async function loadPyodideAndPackages() {
  pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/",
  });
  
  // Pre-load commonly used packages
  await pyodide.loadPackage(["numpy", "matplotlib", "micropip"]);
  
  // Redirect stdout and stderr to capture output
  pyodide.runPython(`
    import sys
    from io import StringIO
    
    class OutputCapture:
        def __init__(self):
            self.stdout = StringIO()
            self.stderr = StringIO()
            
        def __enter__(self):
            self.old_stdout = sys.stdout
            self.old_stderr = sys.stderr
            sys.stdout = self.stdout
            sys.stderr = self.stderr
            return self
            
        def __exit__(self, *args):
            sys.stdout = self.old_stdout
            sys.stderr = self.old_stderr
            
        def get_output(self):
            return {
                'stdout': self.stdout.getvalue(),
                'stderr': self.stderr.getvalue()
            }
  `);
  
  return pyodide;
}

pyodideReadyPromise = loadPyodideAndPackages();

// Handle messages from the main thread
self.onmessage = async function(e) {
  const { id, code, timeLimit = 30000 } = e.data;
  
  // Make sure Pyodide is loaded
  await pyodideReadyPromise;
  
  let timeoutId;
  const startTime = performance.now();
  
  try {
    // Set up timeout
    const timeoutPromise = new Promise((_, reject) => {
      timeoutId = setTimeout(() => {
        reject(new Error(`Execution timed out after ${timeLimit}ms`));
      }, timeLimit);
    });
    
    // Execute the code
    const executionPromise = new Promise((resolve) => {
      try {
        const result = pyodide.runPython(`
import sys
from io import StringIO
import traceback

# Capture output
output_capture = StringIO()
error_capture = StringIO()
old_stdout = sys.stdout
old_stderr = sys.stderr

result = None
error = None
exit_code = 0

try:
    sys.stdout = output_capture
    sys.stderr = error_capture
    
    # Execute user code
    exec('''${code.replace(/'/g, "\\'")}''')
    
except Exception as e:
    error = traceback.format_exc()
    exit_code = 1
    
finally:
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    
output = {
    'stdout': output_capture.getvalue(),
    'stderr': error_capture.getvalue() + (error or ''),
    'exit_code': exit_code
}

output
        `);
        
        const output = result.toJs();
        resolve({
          stdout: output.stdout || '',
          stderr: output.stderr || '',
          exitCode: output.exit_code || 0
        });
      } catch (error) {
        resolve({
          stdout: '',
          stderr: error.toString(),
          exitCode: 1
        });
      }
    });
    
    // Race between execution and timeout
    const result = await Promise.race([executionPromise, timeoutPromise]);
    clearTimeout(timeoutId);
    
    const duration = Math.round(performance.now() - startTime);
    
    self.postMessage({
      id,
      success: true,
      stdout: result.stdout,
      stderr: result.stderr,
      exitCode: result.exitCode,
      duration
    });
    
  } catch (error) {
    clearTimeout(timeoutId);
    const duration = Math.round(performance.now() - startTime);
    
    self.postMessage({
      id,
      success: false,
      error: error.message,
      duration
    });
  }
};

// Notify that the worker is ready
self.postMessage({ type: 'ready' });

