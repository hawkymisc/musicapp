import { useState, useCallback } from 'react';

const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (apiFunction, ...args) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiFunction(...args);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
  }, []);

  return {
    loading,
    error,
    execute,
    reset
  };
};

export default useApi;