// 🚀 Performance Optimization Utilities
import React, { useMemo, useCallback, useState, useEffect } from 'react';

// Debounce hook for search inputs
export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Optimized data fetching hook
export const useOptimizedFetch = <T>(
  url: string,
  dependencies: any[] = [],
  options?: RequestInit
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [url, ...dependencies]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch };
};

// Memoized chart data processor
export const useChartDataProcessor = (rawData: any[], transformFn: (data: any) => any) => {
  return useMemo(() => {
    if (!rawData || rawData.length === 0) return [];
    return rawData.map(transformFn);
  }, [rawData, transformFn]);
};

// Performance monitoring hook
export const usePerformanceMonitor = (componentName: string) => {
  useEffect(() => {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      if (renderTime > 100) { // Log slow renders
        console.warn(`⚠️ Slow render detected in ${componentName}: ${renderTime.toFixed(2)}ms`);
      }
    };
  });
};

// Optimized data formatter
export const useDataFormatter = () => {
  return useMemo(() => ({
    formatNumber: (num: number, decimals = 1) => {
      if (isNaN(num)) return '0';
      return Number(num).toFixed(decimals);
    },
    
    formatPercentage: (num: number) => {
      if (isNaN(num)) return '0%';
      return `${Number(num).toFixed(1)}%`;
    },
    
    formatDate: (dateString: string, options?: Intl.DateTimeFormatOptions) => {
      try {
        return new Date(dateString).toLocaleDateString('id-ID', options);
      } catch {
        return dateString;
      }
    },
    
    formatCurrency: (num: number) => {
      if (isNaN(num)) return 'Rp 0';
      return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
      }).format(num);
    }
  }), []);
};

// Virtualized list component for large datasets
interface VirtualizedListProps {
  items: any[];
  renderItem: (item: any, index: number) => React.ReactNode;
  itemHeight: number;
  containerHeight: number;
  className?: string;
}

export const VirtualizedList: React.FC<VirtualizedListProps> = React.memo(({
  items,
  renderItem,
  itemHeight,
  containerHeight,
  className = ''
}) => {
  const [scrollTop, setScrollTop] = useState(0);
  
  const visibleStart = Math.floor(scrollTop / itemHeight);
  const visibleEnd = Math.min(visibleStart + Math.ceil(containerHeight / itemHeight) + 1, items.length);
  
  const visibleItems = useMemo(() => 
    items.slice(visibleStart, visibleEnd),
    [items, visibleStart, visibleEnd]
  );
  
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);
  
  return (
    <div
      className={`overflow-auto ${className}`}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
    >
      <div style={{ height: items.length * itemHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${visibleStart * itemHeight}px)` }}>
          {visibleItems.map((item, index) => 
            renderItem(item, visibleStart + index)
          )}
        </div>
      </div>
    </div>
  );
});

VirtualizedList.displayName = 'VirtualizedList';

// Optimized image component with lazy loading
interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  placeholder?: string;
  onLoad?: () => void;
  onError?: () => void;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = React.memo(({
  src,
  alt,
  className = '',
  placeholder,
  onLoad,
  onError
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);

  const handleLoad = useCallback(() => {
    setIsLoaded(true);
    onLoad?.();
  }, [onLoad]);

  const handleError = useCallback(() => {
    setHasError(true);
    onError?.();
  }, [onError]);

  if (hasError && placeholder) {
    return <img src={placeholder} alt={alt} className={className} />;
  }

  return (
    <img
      src={src}
      alt={alt}
      className={`transition-opacity duration-300 ${isLoaded ? 'opacity-100' : 'opacity-0'} ${className}`}
      onLoad={handleLoad}
      onError={handleError}
      loading="lazy"
    />
  );
});

OptimizedImage.displayName = 'OptimizedImage';

// Performance metrics context
interface PerformanceMetrics {
  renderCount: number;
  lastRenderTime: number;
  averageRenderTime: number;
}

export const PerformanceContext = React.createContext<PerformanceMetrics | null>(null);

export const PerformanceProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    renderCount: 0,
    lastRenderTime: 0,
    averageRenderTime: 0
  });

  const updateMetrics = useCallback((renderTime: number) => {
    setMetrics(prev => ({
      renderCount: prev.renderCount + 1,
      lastRenderTime: renderTime,
      averageRenderTime: (prev.averageRenderTime * prev.renderCount + renderTime) / (prev.renderCount + 1)
    }));
  }, []);

  return (
    <PerformanceContext.Provider value={metrics}>
      {children}
    </PerformanceContext.Provider>
  );
};

export const usePerformanceMetrics = () => {
  const context = React.useContext(PerformanceContext);
  if (!context) {
    throw new Error('usePerformanceMetrics must be used within a PerformanceProvider');
  }
  return context;
};

export default {
  useDebounce,
  useOptimizedFetch,
  useChartDataProcessor,
  usePerformanceMonitor,
  useDataFormatter,
  VirtualizedList,
  OptimizedImage,
  PerformanceProvider,
  usePerformanceMetrics
};