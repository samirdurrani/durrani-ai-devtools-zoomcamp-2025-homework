import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('App Component', () => {
  it('renders without crashing', () => {
    render(<App />);
  });

  it('renders the landing page by default', () => {
    render(<App />);
    // Check for landing page heading
    expect(screen.getByText(/Coding Interview Platform/i)).toBeInTheDocument();
  });

  it('contains router elements', () => {
    const { container } = render(<App />);
    // App should have a router container
    expect(container.querySelector('.app')).toBeInTheDocument();
  });
});
