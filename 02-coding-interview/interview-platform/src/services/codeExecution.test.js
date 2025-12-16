import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { executeJavaScript, formatExecutionResult } from './codeExecution';

describe('Code Execution Service', () => {
  let iframeMock;
  let originalCreateElement;
  let originalRemoveChild;

  beforeEach(() => {
    // Mock iframe creation
    iframeMock = {
      style: {},
      sandbox: '',
      contentWindow: {
        postMessage: vi.fn(),
      },
      contentDocument: {
        createElement: vi.fn(() => ({
          textContent: '',
        })),
        body: {
          appendChild: vi.fn(),
        },
      },
    };

    originalCreateElement = document.createElement;
    originalRemoveChild = document.body.removeChild;

    document.createElement = vi.fn((tag) => {
      if (tag === 'iframe') {
        return iframeMock;
      }
      return originalCreateElement.call(document, tag);
    });

    document.body.appendChild = vi.fn();
    document.body.removeChild = vi.fn();
    document.body.contains = vi.fn(() => true);
  });

  afterEach(() => {
    document.createElement = originalCreateElement;
    document.body.removeChild = originalRemoveChild;
    vi.clearAllMocks();
  });

  describe('executeJavaScript', () => {
    it('executes simple code successfully', async () => {
      const code = 'console.log("test")';
      
      // Simulate successful execution
      const messageHandler = (event) => {
        if (event.listener) {
          event.listener({
            data: {
              type: 'execution-result',
              output: [{ type: 'log', message: 'test' }],
              error: null,
              executionTime: 10,
            },
          });
        }
      };

      window.addEventListener = vi.fn((type, listener) => {
        if (type === 'message') {
          setTimeout(() => messageHandler({ listener }), 0);
        }
      });

      window.removeEventListener = vi.fn();

      const result = await executeJavaScript(code);

      expect(result.success).toBe(true);
      expect(result.output).toContain('test');
      expect(result.error).toBe(null);
      expect(result.executionTime).toBe(10);
    });

    it('handles code execution errors', async () => {
      const code = 'throw new Error("Test error")';
      
      const messageHandler = (event) => {
        if (event.listener) {
          event.listener({
            data: {
              type: 'execution-result',
              output: [],
              error: {
                name: 'Error',
                message: 'Test error',
                stack: 'Error: Test error',
              },
              executionTime: 5,
            },
          });
        }
      };

      window.addEventListener = vi.fn((type, listener) => {
        if (type === 'message') {
          setTimeout(() => messageHandler({ listener }), 0);
        }
      });

      window.removeEventListener = vi.fn();

      const result = await executeJavaScript(code);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Test error');
      expect(result.executionTime).toBe(5);
    });

    it('handles timeout for long-running code', async () => {
      const code = 'while(true) {}';
      
      // Don't send any message to simulate timeout
      window.addEventListener = vi.fn();
      window.removeEventListener = vi.fn();

      const result = await executeJavaScript(code);

      expect(result.success).toBe(false);
      expect(result.error).toContain('timed out');
    }, 6000); // Increase test timeout since we're testing a 5s timeout
  });

  describe('formatExecutionResult', () => {
    it('formats successful execution with output', () => {
      const result = {
        success: true,
        output: 'Hello, World!',
        error: null,
        executionTime: 15.5,
      };

      const formatted = formatExecutionResult(result);
      
      expect(formatted).toContain('Hello, World!');
      expect(formatted).toContain('15.50ms');
      expect(formatted).not.toContain('Error');
    });

    it('formats error execution', () => {
      const result = {
        success: false,
        output: '',
        error: 'ReferenceError: x is not defined',
        executionTime: 5,
      };

      const formatted = formatExecutionResult(result);
      
      expect(formatted).toContain('❌ Error:');
      expect(formatted).toContain('x is not defined');
      expect(formatted).toContain('5.00ms');
    });

    it('formats successful execution with no output', () => {
      const result = {
        success: true,
        output: '',
        error: null,
        executionTime: 10,
      };

      const formatted = formatExecutionResult(result);
      
      expect(formatted).toContain('✅ Code executed successfully');
      expect(formatted).toContain('no output');
    });
  });
});
