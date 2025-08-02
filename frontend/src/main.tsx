import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './styles/medical.css'

// Create an optimized client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes (lebih lama)
      gcTime: 10 * 60 * 1000, // 10 minutes (lebih lama untuk cache)
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 1; // Kurangi retry untuk performance
      },
      refetchOnWindowFocus: false,
      refetchOnMount: false, // Jangan auto refetch
      refetchOnReconnect: false,
    },
    mutations: {
      retry: 1,
    },
  },
})

// Performance optimization: Skip strict mode in production
const AppWrapper = () => (
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
);

const root = ReactDOM.createRoot(document.getElementById('root')!);

// Use different render based on environment
if (process.env.NODE_ENV === 'development') {
  root.render(
    <React.StrictMode>
      <AppWrapper />
    </React.StrictMode>
  );
} else {
  root.render(<AppWrapper />);
}
