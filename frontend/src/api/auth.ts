/**
 * Authentication API
 * Handles login, register, and token management
 */

import { apiPost, getHeaders, removeAuthToken, setAuthToken } from './client';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_V1_STR = '/api/v1';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

/**
 * Login user with username and password
 * Backend expects form-urlencoded data
 */
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const url = `${API_BASE_URL}${API_V1_STR}/auth/login`;
  
  console.log('[AUTH] Login attempt:', { username: credentials.username, url });
  
  // Backend expects form-urlencoded
  const formData = new URLSearchParams();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  try {
    console.log('[AUTH] Sending login request...');
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
      signal: AbortSignal.timeout(5000), // 5 second timeout
    });

    console.log('[AUTH] Response received:', response.status, response.statusText);

    if (!response.ok) {
      const error = await response.json();
      console.error('[AUTH] Login error:', error);
      throw new Error(error.detail || 'Login failed');
    }

    const data: LoginResponse = await response.json();
    console.log('[AUTH] Login successful, token received');
    
    // Store token
    setAuthToken(data.access_token);
    
    return data;
  } catch (error) {
    console.error('[AUTH] Login exception:', error);
    if (error instanceof Error && error.name === 'TimeoutError') {
      throw new Error('Login request timed out. Please check your connection.');
    }
    throw error;
  }
}

/**
 * Register new user
 */
export async function register(userData: RegisterRequest): Promise<User> {
  return apiPost<User, RegisterRequest>('/auth/register', userData);
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<User> {
  const url = `${API_BASE_URL}${API_V1_STR}/users/me`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get user');
  }

  return response.json();
}

/**
 * Logout user (clear token)
 */
export function logout(): void {
  removeAuthToken();
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  const token = localStorage.getItem('access_token');
  return !!token;
}

export default {
  login,
  register,
  getCurrentUser,
  logout,
  isAuthenticated,
};
