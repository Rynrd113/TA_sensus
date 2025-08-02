// Security utilities for the frontend application

/**
 * Sanitize input string to prevent XSS attacks
 */
export const sanitizeInput = (input: string): string => {
  if (typeof input !== 'string') return '';
  
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
};

/**
 * Validate and sanitize URL to prevent open redirect attacks
 */
export const sanitizeUrl = (url: string): string => {
  if (!url) return '';
  
  // Only allow relative URLs or URLs from same origin
  if (url.startsWith('/')) {
    return url;
  }
  
  try {
    const urlObj = new URL(url);
    const currentOrigin = window.location.origin;
    
    if (urlObj.origin === currentOrigin) {
      return url;
    }
  } catch {
    // Invalid URL
  }
  
  return '/';
};

/**
 * Secure localStorage operations with error handling
 */
export const secureStorage = {
  get: (key: string): string | null => {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  
  set: (key: string, value: string): boolean => {
    try {
      localStorage.setItem(key, value);
      return true;
    } catch {
      return false;
    }
  },
  
  remove: (key: string): boolean => {
    try {
      localStorage.removeItem(key);
      return true;
    } catch {
      return false;
    }
  },
  
  clear: (): boolean => {
    try {
      localStorage.clear();
      return true;
    } catch {
      return false;
    }
  }
};

/**
 * Validate file upload security
 */
export const validateFileUpload = (file: File): { valid: boolean; error?: string } => {
  // Allowed file types
  const allowedTypes = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/pdf',
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ];
  
  // Maximum file size (10MB)
  const maxSize = 10 * 1024 * 1024;
  
  if (!allowedTypes.includes(file.type)) {
    return { valid: false, error: 'Tipe file tidak diizinkan' };
  }
  
  if (file.size > maxSize) {
    return { valid: false, error: 'Ukuran file terlalu besar (maksimal 10MB)' };
  }
  
  return { valid: true };
};

/**
 * Generate Content Security Policy
 */
export const getCSP = (): string => {
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline'",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: https:",
    "connect-src 'self' http://localhost:8000 https:",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'"
  ];
  
  return csp.join('; ');
};

/**
 * Validate input data types
 */
export const validateDataType = (value: any, expectedType: string): boolean => {
  switch (expectedType) {
    case 'number':
      return typeof value === 'number' && !isNaN(value);
    case 'string':
      return typeof value === 'string';
    case 'boolean':
      return typeof value === 'boolean';
    case 'date':
      return value instanceof Date || (typeof value === 'string' && !isNaN(Date.parse(value)));
    default:
      return false;
  }
};

/**
 * Rate limiting for API calls
 */
class RateLimiter {
  private attempts: Map<string, number[]> = new Map();
  private readonly maxAttempts: number = 10;
  private readonly timeWindow: number = 60000; // 1 minute

  isAllowed(identifier: string): boolean {
    const now = Date.now();
    const attempts = this.attempts.get(identifier) || [];
    
    // Remove old attempts outside time window
    const recentAttempts = attempts.filter(time => now - time < this.timeWindow);
    
    if (recentAttempts.length >= this.maxAttempts) {
      return false;
    }
    
    recentAttempts.push(now);
    this.attempts.set(identifier, recentAttempts);
    
    return true;
  }
}

export const rateLimiter = new RateLimiter();

/**
 * Generate secure random string
 */
export const generateSecureToken = (length: number = 32): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  
  return result;
};
