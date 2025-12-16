// Service for executing code safely in the browser

// Execute JavaScript code in a sandboxed environment
export const executeJavaScript = (code) => {
  return new Promise((resolve) => {
    try {
      // Create a sandboxed iframe for code execution
      const iframe = document.createElement('iframe');
      iframe.style.display = 'none';
      iframe.sandbox = 'allow-scripts'; // Only allow scripts, no other permissions
      document.body.appendChild(iframe);

      // Prepare the code to capture console output
      const wrappedCode = `
        (function() {
          let output = [];
          const originalConsole = {
            log: console.log,
            error: console.error,
            warn: console.warn,
            info: console.info
          };
          
          // Override console methods to capture output
          console.log = (...args) => {
            output.push({ type: 'log', message: args.map(arg => {
              if (typeof arg === 'object') {
                try {
                  return JSON.stringify(arg, null, 2);
                } catch (e) {
                  return String(arg);
                }
              }
              return String(arg);
            }).join(' ') });
          };
          
          console.error = (...args) => {
            output.push({ type: 'error', message: args.map(arg => String(arg)).join(' ') });
          };
          
          console.warn = (...args) => {
            output.push({ type: 'warn', message: args.map(arg => String(arg)).join(' ') });
          };
          
          console.info = (...args) => {
            output.push({ type: 'info', message: args.map(arg => String(arg)).join(' ') });
          };
          
          let error = null;
          const startTime = performance.now();
          
          try {
            // Execute the user's code
            ${code}
          } catch (e) {
            error = {
              name: e.name,
              message: e.message,
              stack: e.stack
            };
          }
          
          const executionTime = performance.now() - startTime;
          
          // Send results back to parent
          window.parent.postMessage({
            type: 'execution-result',
            output: output,
            error: error,
            executionTime: executionTime
          }, '*');
        })();
      `;

      // Listen for the execution result
      const messageHandler = (event) => {
        if (event.data.type === 'execution-result') {
          window.removeEventListener('message', messageHandler);
          document.body.removeChild(iframe);
          
          // Format the result
          if (event.data.error) {
            resolve({
              success: false,
              output: event.data.output.map(o => o.message).join('\n'),
              error: `${event.data.error.name}: ${event.data.error.message}`,
              executionTime: event.data.executionTime,
            });
          } else {
            resolve({
              success: true,
              output: event.data.output.map(o => o.message).join('\n'),
              error: null,
              executionTime: event.data.executionTime,
            });
          }
        }
      };

      window.addEventListener('message', messageHandler);

      // Set a timeout for execution
      setTimeout(() => {
        window.removeEventListener('message', messageHandler);
        if (document.body.contains(iframe)) {
          document.body.removeChild(iframe);
        }
        resolve({
          success: false,
          output: '',
          error: 'Code execution timed out (5 seconds)',
          executionTime: 5000,
        });
      }, 5000); // 5 second timeout

      // Execute the code in the iframe
      iframe.contentWindow.postMessage({ type: 'execute', code: wrappedCode }, '*');
      
      // Actually run the code in iframe
      const script = iframe.contentDocument.createElement('script');
      script.textContent = wrappedCode;
      iframe.contentDocument.body.appendChild(script);
      
    } catch (error) {
      resolve({
        success: false,
        output: '',
        error: error.message,
        executionTime: 0,
      });
    }
  });
};

// Helper function to format execution results
export const formatExecutionResult = (result) => {
  const lines = [];
  
  if (result.output) {
    lines.push(result.output);
  }
  
  if (result.error) {
    lines.push(`\n❌ Error: ${result.error}`);
  }
  
  if (result.executionTime !== undefined) {
    lines.push(`\n⏱️ Execution time: ${result.executionTime.toFixed(2)}ms`);
  }
  
  if (result.success && !result.output) {
    lines.push('✅ Code executed successfully (no output)');
  }
  
  return lines.join('\n');
};
