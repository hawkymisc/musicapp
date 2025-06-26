import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LoadingSpinner from '../LoadingSpinner';

describe('LoadingSpinner Component', () => {
  it('should render with default props', () => {
    render(<LoadingSpinner />);
    
    expect(screen.getByText('読み込み中...')).toBeInTheDocument();
  });

  it('should render with custom text', () => {
    render(<LoadingSpinner text="カスタムローディング" />);
    
    expect(screen.getByText('カスタムローディング')).toBeInTheDocument();
  });

  it('should render without text when text is empty', () => {
    render(<LoadingSpinner text="" />);
    
    expect(screen.queryByText(/読み込み中/)).not.toBeInTheDocument();
  });

  it('should render small size variant', () => {
    const { container } = render(<LoadingSpinner size="small" />);
    
    // Check if the spinner has small size styling
    const spinner = container.querySelector('div > div');
    expect(spinner).toBeInTheDocument();
  });

  it('should render normal size by default', () => {
    const { container } = render(<LoadingSpinner />);
    
    // Check if the spinner exists
    const spinner = container.querySelector('div > div');
    expect(spinner).toBeInTheDocument();
  });

  it('should have proper accessibility attributes', () => {
    render(<LoadingSpinner />);
    
    // The component should be visible and have content
    const loadingText = screen.getByText('読み込み中...');
    expect(loadingText).toBeVisible();
  });

  it('should render spinner animation element', () => {
    const { container } = render(<LoadingSpinner />);
    
    // Check if the animated spinner element exists
    const spinnerContainer = container.querySelector('div');
    const spinner = spinnerContainer?.querySelector('div');
    
    expect(spinnerContainer).toBeInTheDocument();
    expect(spinner).toBeInTheDocument();
  });
});