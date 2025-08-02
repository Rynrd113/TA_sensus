import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// Base URL dari environment dengan fallback yang aman
const BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';

// Validasi URL untuk mencegah injection
const isValidUrl = (url: string): boolean => {
  try {
    const urlObj = new URL(url);
    return ['http:', 'https:'].includes(urlObj.protocol);
  } catch {
    return false;
  }
};

if (!isValidUrl(BASE_URL)) {
  console.error('Invalid API URL configuration');
}

class ApiClient {
  private instance: AxiosInstance;
  private isLoading: boolean = false;

  constructor() {
    this.instance = axios.create({
      baseURL: BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest', // CSRF protection
      },
      withCredentials: false, // Set true if using cookies
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.instance.interceptors.request.use(
      (config) => {
        this.isLoading = true;
        
        // Sanitize request data
        if (config.data && typeof config.data === 'object') {
          config.data = this.sanitizeData(config.data);
        }
        
        // Add authentication token if available
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        return config;
      },
      (error) => {
        this.isLoading = false;
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        this.isLoading = false;
        return response;
      },
      (error) => {
        this.isLoading = false;
        
        // Handle specific error cases securely
        if (error.response?.status === 401) {
          // Handle unauthorized - clear session and redirect
          this.handleUnauthorized();
        } else if (error.response?.status === 404) {
          console.warn('Resource not found:', error.config?.url);
        } else if (error.response?.status >= 500) {
          console.error('Server error occurred');
          // Don't expose internal server errors to user
        }

        return Promise.reject(this.sanitizeError(error));
      }
    );
  }

  private sanitizeData(data: any): any {
    if (typeof data !== 'object' || data === null) {
      return data;
    }
    
    const sanitized = { ...data };
    
    // Remove potentially dangerous properties
    delete sanitized.__proto__;
    delete sanitized.constructor;
    
    // Recursively sanitize nested objects
    Object.keys(sanitized).forEach(key => {
      if (typeof sanitized[key] === 'object' && sanitized[key] !== null) {
        sanitized[key] = this.sanitizeData(sanitized[key]);
      }
    });
    
    return sanitized;
  }

  private sanitizeError(error: any): Error {
    // Create a clean error object without exposing sensitive information
    const sanitizedError = new Error(
      error.response?.data?.message || 
      error.message || 
      'An error occurred'
    );
    
    return sanitizedError;
  }

  private getAuthToken(): string | null {
    try {
      // Safely get token from localStorage
      return localStorage.getItem('auth_token');
    } catch {
      return null;
    }
  }

  private handleUnauthorized(): void {
    // Clear any stored authentication data
    try {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
    } catch {
      // Ignore localStorage errors
    }
    
    // Redirect to login if in browser environment
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  // Generic request methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.put<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.delete<T>(url, config);
    return response.data;
  }

  // Utility methods
  getLoadingState(): boolean {
    return this.isLoading;
  }

  getBaseURL(): string {
    return BASE_URL;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient;
