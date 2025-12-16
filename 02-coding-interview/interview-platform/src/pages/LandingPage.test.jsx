import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import LandingPage from './LandingPage';

// Mock the navigation hook
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock the API service
vi.mock('../services/api', () => ({
  apiService: {
    createSession: vi.fn(),
  },
}));

describe('LandingPage Component', () => {
  const renderLandingPage = () => {
    return render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );
  };

  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('renders the main heading', () => {
    renderLandingPage();
    expect(screen.getByText(/Coding Interview Platform/i)).toBeInTheDocument();
  });

  it('renders create session button', () => {
    renderLandingPage();
    const createButton = screen.getByRole('button', { name: /Create New Interview/i });
    expect(createButton).toBeInTheDocument();
  });

  it('renders join session form', () => {
    renderLandingPage();
    const joinInput = screen.getByPlaceholderText(/Paste session URL or ID here/i);
    const joinButton = screen.getByRole('button', { name: /Join Session/i });
    expect(joinInput).toBeInTheDocument();
    expect(joinButton).toBeInTheDocument();
  });

  it('displays features section', () => {
    renderLandingPage();
    expect(screen.getByText(/Multi-language Support/i)).toBeInTheDocument();
    expect(screen.getByText(/Real-time Collaboration/i)).toBeInTheDocument();
    expect(screen.getByText(/Live Code Execution/i)).toBeInTheDocument();
    expect(screen.getByText(/Syntax Highlighting/i)).toBeInTheDocument();
  });

  it('handles create session click', async () => {
    const { apiService } = await import('../services/api');
    apiService.createSession.mockResolvedValueOnce({ sessionId: 'test-session-123' });

    renderLandingPage();
    const createButton = screen.getByRole('button', { name: /Create New Interview/i });
    
    fireEvent.click(createButton);
    
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/session/test-session-123');
    });
  });

  it('handles join session with valid URL', async () => {
    const user = userEvent.setup();
    renderLandingPage();
    
    const joinInput = screen.getByPlaceholderText(/Paste session URL or ID here/i);
    const joinButton = screen.getByRole('button', { name: /Join Session/i });
    
    await user.type(joinInput, 'http://localhost:3000/session/abc123');
    await user.click(joinButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('/session/abc123');
  });

  it('shows error for empty join URL', async () => {
    const user = userEvent.setup();
    renderLandingPage();
    
    const joinButton = screen.getByRole('button', { name: /Join Session/i });
    await user.click(joinButton);
    
    expect(screen.getByText(/Please enter a valid session URL/i)).toBeInTheDocument();
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('handles different URL formats for joining', async () => {
    const user = userEvent.setup();
    renderLandingPage();
    
    const joinInput = screen.getByPlaceholderText(/Paste session URL or ID here/i);
    const joinButton = screen.getByRole('button', { name: /Join Session/i });
    
    // Test with just session ID
    await user.clear(joinInput);
    await user.type(joinInput, 'session123');
    await user.click(joinButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('/session/session123');
  });
});
