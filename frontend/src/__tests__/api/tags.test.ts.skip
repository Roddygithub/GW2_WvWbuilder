/**
 * Tags API Tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { getTags, getTag, createTag, updateTag, deleteTag } from '../../api/tags';

// Mock fetch
global.fetch = vi.fn();

describe('Tags API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('access_token', 'test-token');
  });

  describe('getTags', () => {
    it('should fetch all tags', async () => {
      const mockTags = [
        { id: 1, name: 'WvW', description: 'World vs World' },
        { id: 2, name: 'PvE', description: 'Player vs Environment' },
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockTags,
      });

      const result = await getTags();

      expect(result).toEqual(mockTags);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/tags/'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token',
          }),
        })
      );
    });
  });

  describe('getTag', () => {
    it('should fetch a single tag by ID', async () => {
      const mockTag = { id: 1, name: 'WvW', description: 'World vs World' };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockTag,
      });

      const result = await getTag(1);

      expect(result).toEqual(mockTag);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/tags/1'),
        expect.any(Object)
      );
    });
  });

  describe('createTag', () => {
    it('should create a new tag', async () => {
      const newTag = { name: 'New Tag', description: 'Test tag' };
      const mockResponse = { id: 3, ...newTag };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await createTag(newTag);

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/tags/'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(newTag),
        })
      );
    });
  });

  describe('updateTag', () => {
    it('should update an existing tag', async () => {
      const updateData = { description: 'Updated description' };
      const mockResponse = { id: 1, name: 'WvW', description: 'Updated description' };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await updateTag(1, updateData);

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/tags/1'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(updateData),
        })
      );
    });
  });

  describe('deleteTag', () => {
    it('should delete a tag', async () => {
      const mockResponse = { msg: 'Tag deleted successfully' };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await deleteTag(1);

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/tags/1'),
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });
  });
});
