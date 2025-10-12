/**
 * Authentication API Tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { login, logout, isAuthenticated } from '../../api/auth';

// Mock fetch
global.fetch = vi.fn();

describe('Authentication API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('login', () => {
    it('should login successfully and store token', async () => {
      const mockResponse = {
        access_token: 'test-token',
        token_type: 'bearer',
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await login({ username: 'testuser', password: 'testpass' });

      expect(result).toEqual(mockResponse);
      expect(localStorage.getItem('access_token')).toBe('test-token');
    });

    it('should throw error on failed login', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Invalid credentials' }),
      });

      await expect(
        login({ username: 'testuser', password: 'wrongpass' })
      ).rejects.toThrow('Invalid credentials');
    });
  });

  describe('logout', () => {
    it('should remove token from localStorage', () => {
      localStorage.setItem('access_token', 'test-token');
      
      logout();
      
      expect(localStorage.getItem('access_token')).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when token exists', () => {
      localStorage.setItem('access_token', 'test-token');
      
      expect(isAuthenticated()).toBe(true);
    });

    it('should return false when token does not exist', () => {
      expect(isAuthenticated()).toBe(false);
    });
  });
});
