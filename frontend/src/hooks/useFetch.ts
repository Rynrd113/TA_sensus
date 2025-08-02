import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { LoadingState } from '../types/Common';

interface UseFetchOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
  deps?: any[]; // Dependencies untuk refetch otomatis
}

interface UseFetchReturn<T> extends LoadingState {
  data: T | null;
  refetch: () => Promise<void>;
  setData: (data: T | null) => void;
}

// Custom hook yang dioptimasi untuk performance
export function useFetch<T>(
  fetchFunction: () => Promise<T>,
  options: UseFetchOptions = {}
): UseFetchReturn<T> {
  const { immediate = true, onSuccess, onError, deps = [] } = options;
  
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(immediate);
  const [error, setError] = useState<string | null>(null);
  
  // Track if component has mounted and initial fetch has run
  const hasInitialFetchRun = useRef(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  
  // Use ref untuk menyimpan fetch function dan callbacks untuk menghindari stale closures
  const fetchFunctionRef = useRef(fetchFunction);
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);
  
  // Update refs when values change
  fetchFunctionRef.current = fetchFunction;
  onSuccessRef.current = onSuccess;
  onErrorRef.current = onError;

  // Memoized execute function yang stable
  const executeFetch = useCallback(async () => {
    // Cancel previous request jika masih berjalan
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    try {
      setLoading(true);
      setError(null);
      
      // Execute fetch dengan timeout dan abort signal
      const result = await Promise.race([
        fetchFunctionRef.current(),
        new Promise<never>((_, reject) => {
          const timeout = setTimeout(() => {
            reject(new Error('Request timeout'));
          }, 30000); // 30 second timeout
          
          abortControllerRef.current?.signal.addEventListener('abort', () => {
            clearTimeout(timeout);
            reject(new Error('Request aborted'));
          });
        })
      ]);

      // Check if component is still mounted
      if (!abortControllerRef.current?.signal.aborted) {
        setData(result);
        
        if (onSuccessRef.current) {
          onSuccessRef.current(result);
        }
      }
    } catch (err: any) {
      if (!abortControllerRef.current?.signal.aborted) {
        const errorMessage = err.name === 'AbortError' 
          ? 'Request cancelled'
          : err.response?.data?.message || err.message || 'Terjadi kesalahan';
        
        setError(errorMessage);
        
        if (onErrorRef.current) {
          onErrorRef.current(errorMessage);
        }
      }
    } finally {
      if (!abortControllerRef.current?.signal.aborted) {
        setLoading(false);
      }
    }
  }, []); // Empty deps - function is stable

  // Stable refetch reference menggunakan useMemo
  const stableRefetch = useMemo(() => {
    return async () => {
      await executeFetch();
    };
  }, [executeFetch]);

  // Run initial fetch dengan dependencies
  useEffect(() => {
    if (immediate && !hasInitialFetchRun.current) {
      hasInitialFetchRun.current = true;
      executeFetch();
    } else if (deps.length > 0) {
      // Re-fetch when dependencies change
      executeFetch();
    }
  }, [immediate, executeFetch, ...deps]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    data,
    loading,
    error,
    refetch: stableRefetch,
    setData
  };
}

// Hook optimized untuk pagination dengan memoization
export function useFetchWithPagination<T>(
  fetchFunction: (page: number, limit: number) => Promise<any>,
  initialPage: number = 1,
  initialLimit: number = 10
) {
  const [page, setPage] = useState(initialPage);
  const [limit, setLimit] = useState(initialLimit);
  
  // Memoized fetch function untuk menghindari re-creation
  const memoizedFetchFunction = useCallback(
    () => fetchFunction(page, limit),
    [fetchFunction, page, limit]
  );

  const { data, loading, error, refetch } = useFetch(
    memoizedFetchFunction,
    { immediate: true, deps: [page, limit] }
  );

  const goToPage = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  const changeLimit = useCallback((newLimit: number) => {
    setLimit(newLimit);
    setPage(1); // Reset ke halaman pertama
  }, []);

  return useMemo(() => ({
    data,
    loading,
    error,
    refetch,
    page,
    limit,
    goToPage,
    changeLimit
  }), [data, loading, error, refetch, page, limit, goToPage, changeLimit]);
}

export default useFetch;
