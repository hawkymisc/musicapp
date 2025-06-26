import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import useApi from '../useApi';

// Mock API function
const mockApiSuccess = vi.fn(() => Promise.resolve({ data: 'success' }));
const mockApiError = vi.fn(() => Promise.reject(new Error('API Error')));

describe('useApi Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with correct default values', () => {
    const { result } = renderHook(() => useApi());
    
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(null);
    expect(typeof result.current.execute).toBe('function');
    expect(typeof result.current.reset).toBe('function');
  });

  it('should handle successful API calls', async () => {
    const { result } = renderHook(() => useApi());
    
    let response;
    await act(async () => {
      response = await result.current.execute(mockApiSuccess);
    });
    
    expect(mockApiSuccess).toHaveBeenCalledTimes(1);
    expect(response).toEqual({ data: 'success' });
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it('should handle API errors', async () => {
    const { result } = renderHook(() => useApi());
    
    await act(async () => {
      try {
        await result.current.execute(mockApiError);
      } catch (error) {
        expect(error.message).toBe('API Error');
      }
    });
    
    expect(mockApiError).toHaveBeenCalledTimes(1);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeInstanceOf(Error);
  });

  it('should set loading state during API call', async () => {
    const { result } = renderHook(() => useApi());
    
    // Start the API call
    act(() => {
      result.current.execute(mockApiSuccess);
    });
    
    // Check loading state is true during the call
    expect(result.current.loading).toBe(true);
    
    // Wait for the call to complete
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    expect(result.current.loading).toBe(false);
  });

  it('should reset state correctly', () => {
    const { result } = renderHook(() => useApi());
    
    act(() => {
      result.current.reset();
    });
    
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it('should pass arguments to API function', async () => {
    const { result } = renderHook(() => useApi());
    const mockApiWithArgs = vi.fn(() => Promise.resolve({ data: 'success' }));
    
    await act(async () => {
      await result.current.execute(mockApiWithArgs, 'arg1', 'arg2');
    });
    
    expect(mockApiWithArgs).toHaveBeenCalledWith('arg1', 'arg2');
  });
});