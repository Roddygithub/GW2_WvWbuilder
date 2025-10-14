/**
 * API Client Configuration
 * Centralized HTTP client for backend communication
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const API_V1_STR = '/api/v1';

export interface ApiError {
  detail?: string;
  msg?: string;
  status?: number;
}

export class ApiClientError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = 'ApiClientError';
    this.status = status;
    this.detail = detail;
  }
}

/**
 * Get authentication token from localStorage
 */
export const getAuthToken = (): string | null => {
  return localStorage.getItem('access_token');
};

/**
 * Set authentication token in localStorage
 */
export const setAuthToken = (token: string): void => {
  localStorage.setItem('access_token', token);
};

/**
 * Remove authentication token from localStorage
 */
export const removeAuthToken = (): void => {
  localStorage.removeItem('access_token');
};

/**
 * Get default headers for API requests
 */
export const getHeaders = (includeAuth = true): HeadersInit => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (includeAuth) {
    const token = getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  return headers;
};

/**
 * Handle API response
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorDetail = 'An error occurred';
    
    try {
      const errorData: ApiError = await response.json();
      // Backend may return 'detail' or 'msg'
      errorDetail = errorData.detail || errorData.msg || errorDetail;
    } catch {
      errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    }

    throw new ApiClientError(response.status, errorDetail);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

/**
 * Generic GET request
 */
export async function apiGet<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${API_V1_STR}${endpoint}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getHeaders(),
    ...options,
  });

  return handleResponse<T>(response);
}

/**
 * Generic POST request
 */
export async function apiPost<T, D = unknown>(
  endpoint: string,
  data?: D,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${API_V1_STR}${endpoint}`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: getHeaders(),
    body: data ? JSON.stringify(data) : undefined,
    ...options,
  });

  return handleResponse<T>(response);
}

/**
 * Generic PUT request
 */
export async function apiPut<T, D = unknown>(
  endpoint: string,
  data?: D,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${API_V1_STR}${endpoint}`;
  
  const response = await fetch(url, {
    method: 'PUT',
    headers: getHeaders(),
    body: data ? JSON.stringify(data) : undefined,
    ...options,
  });

  return handleResponse<T>(response);
}

/**
 * Generic DELETE request
 */
export async function apiDelete<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${API_V1_STR}${endpoint}`;
  
  const response = await fetch(url, {
    method: 'DELETE',
    headers: getHeaders(),
    ...options,
  });

  return handleResponse<T>(response);
}

/**
 * Health check endpoint
 */
export async function checkHealth(): Promise<{ status: string; version?: string }> {
  const url = `${API_BASE_URL}${API_V1_STR}/health`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  return handleResponse(response);
}

export default {
  get: apiGet,
  post: apiPost,
  put: apiPut,
  delete: apiDelete,
  checkHealth,
};
