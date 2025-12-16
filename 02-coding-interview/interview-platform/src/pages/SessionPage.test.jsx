import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import SessionPage from './SessionPage';

// Mock react-router-dom hooks
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ sessionId: 'test-session-123' }),
    useNavigate: () => vi.fn(),
  };
});

// Mock Monaco Editor
vi.mock('@monaco-editor/react', () => ({
  default: ({ value, onChange, onMount }) => {
    // Simulate editor mount
    if (onMount) {
      onMount({
        getModel: () => ({
          setValue: vi.fn(),
        }),
      });
    }
    return (
      <textarea
        data-testid="code-editor"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    );
  },
}));

// Mock WebSocket hook
vi.mock('../hooks/useWebSocket', () => ({
  useWebSocket: () => ({
    isConnected: true,
    participants: 2,
    connectionError: null,
    sendCodeUpdate: vi.fn(),
    sendLanguageChange: vi.fn(),
    sendExecuteCode: vi.fn(),
    subscribe: vi.fn(() => () => {}),
  }),
}));

describe('SessionPage Component', () => {
  const renderSessionPage = () => {
    return render(
      <BrowserRouter>
        <SessionPage />
      </BrowserRouter>
    );
  };

  it('renders the session page with all main elements', () => {
    renderSessionPage();
    
    // Check for header elements
    expect(screen.getByText(/Coding Interview Session/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Back/i })).toBeInTheDocument();
    
    // Check for code editor
    expect(screen.getByTestId('code-editor')).toBeInTheDocument();
    
    // Check for language selector
    expect(screen.getByRole('combobox')).toBeInTheDocument();
    
    // Check for run button
    expect(screen.getByRole('button', { name: /Run Code/i })).toBeInTheDocument();
    
    // Check for output panel - using getAllByText since "Output" appears multiple times
    const outputElements = screen.getAllByText(/Output/i);
    expect(outputElements.length).toBeGreaterThan(0);
  });

  it('displays session URL correctly', () => {
    renderSessionPage();
    const urlInput = screen.getByDisplayValue(/\/session\/test-session-123/);
    expect(urlInput).toBeInTheDocument();
  });

  it('shows connection status', () => {
    renderSessionPage();
    expect(screen.getByText(/Connected/i)).toBeInTheDocument();
  });

  it('displays participant count', () => {
    renderSessionPage();
    expect(screen.getByText(/2 participants/i)).toBeInTheDocument();
  });

  it('handles language selection change', async () => {
    const user = userEvent.setup();
    renderSessionPage();
    
    const languageSelector = screen.getByRole('combobox');
    await user.selectOptions(languageSelector, 'python');
    
    expect(languageSelector.value).toBe('python');
  });

  it('handles code input in editor', async () => {
    const user = userEvent.setup();
    renderSessionPage();
    
    const editor = screen.getByTestId('code-editor');
    const testCode = 'console.log("Hello, World!");';
    
    await user.clear(editor);
    await user.type(editor, testCode);
    
    expect(editor.value).toBe(testCode);
  });

  it('disables run button when code is empty', () => {
    renderSessionPage();
    
    const editor = screen.getByTestId('code-editor');
    fireEvent.change(editor, { target: { value: '' } });
    
    const runButton = screen.getByRole('button', { name: /Run Code/i });
    expect(runButton).toBeDisabled();
  });

  it('handles copy URL button click', async () => {
    // Mock clipboard API
    const mockWriteText = vi.fn().mockResolvedValue();
    Object.defineProperty(navigator, 'clipboard', {
      value: {
        writeText: mockWriteText,
      },
      writable: true,
    });

    renderSessionPage();
    const copyButton = screen.getByRole('button', { name: /Copy Link/i });
    
    fireEvent.click(copyButton);
    
    await waitFor(() => {
      expect(mockWriteText).toHaveBeenCalled();
    });
    
    // Should show "Copied!" message temporarily
    expect(screen.getByText(/Copied!/i)).toBeInTheDocument();
  });

  it('handles clear output button', () => {
    renderSessionPage();
    
    const clearButton = screen.getByRole('button', { name: /Clear/i });
    expect(clearButton).toBeInTheDocument();
    
    // Initially disabled when no output
    expect(clearButton).toBeDisabled();
  });

  it('has all supported languages in selector', () => {
    renderSessionPage();
    
    const languageSelector = screen.getByRole('combobox');
    const options = languageSelector.querySelectorAll('option');
    
    // Should have at least JavaScript and Python
    const languages = Array.from(options).map(opt => opt.textContent);
    expect(languages).toContain('JavaScript');
    expect(languages).toContain('Python');
    expect(languages).toContain('Java');
    expect(languages).toContain('C++');
  });
});
