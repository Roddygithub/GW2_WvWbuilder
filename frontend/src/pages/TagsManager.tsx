/**
 * Tags Manager Page
 * CRUD interface for tag management
 * Connected to production-ready Tags API (78% tested)
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { getTags, createTag, updateTag, deleteTag, type Tag, type CreateTagRequest } from '../api/tags';

export default function TagsManager() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user, isAuthenticated, logout } = useAuthStore();
  
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const [formData, setFormData] = useState<CreateTagRequest>({
    name: '',
    description: '',
    category: '',
  });

  // Check authentication
  if (!isAuthenticated) {
    navigate('/login');
    return null;
  }

  // Fetch tags
  const { data: tags, isLoading, error } = useQuery({
    queryKey: ['tags'],
    queryFn: getTags,
  });

  // Create tag mutation
  const createMutation = useMutation({
    mutationFn: createTag,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      setIsCreateModalOpen(false);
      resetForm();
    },
  });

  // Update tag mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: CreateTagRequest }) =>
      updateTag(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      setEditingTag(null);
      resetForm();
    },
  });

  // Delete tag mutation
  const deleteMutation = useMutation({
    mutationFn: deleteTag,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
    },
  });

  const resetForm = () => {
    setFormData({ name: '', description: '', category: '' });
  };

  const handleCreate = () => {
    if (!formData.name) return;
    createMutation.mutate(formData);
  };

  const handleUpdate = () => {
    if (!editingTag || !formData.name) return;
    updateMutation.mutate({ id: editingTag.id, data: formData });
  };

  const handleEdit = (tag: Tag) => {
    setEditingTag(tag);
    setFormData({
      name: tag.name,
      description: tag.description || '',
      category: tag.category || '',
    });
  };

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this tag?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-gray-700 bg-slate-800/50 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">Tags Manager</h1>
              <p className="text-sm text-gray-400">Manage your WvW composition tags</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="rounded-md bg-gray-600 px-4 py-2 text-sm font-semibold text-white hover:bg-gray-500"
              >
                Dashboard
              </button>
              <button
                onClick={handleLogout}
                className="rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-500"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Create Button */}
        {user?.is_superuser && (
          <div className="mb-6">
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="rounded-md bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-500"
            >
              + Create New Tag
            </button>
          </div>
        )}

        {/* Tags List */}
        <div className="rounded-lg bg-slate-800/50 p-6 shadow-xl backdrop-blur-sm">
          {isLoading && (
            <div className="text-center text-white">Loading tags...</div>
          )}

          {error && (
            <div className="rounded-md bg-red-500/10 border border-red-500/50 p-4">
              <p className="text-sm text-red-400">
                Error loading tags: {error instanceof Error ? error.message : 'Unknown error'}
              </p>
            </div>
          )}

          {tags && tags.length === 0 && (
            <div className="text-center text-gray-400">
              No tags found. Create your first tag!
            </div>
          )}

          {tags && tags.length > 0 && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {tags.map((tag) => (
                <div
                  key={tag.id}
                  className="rounded-lg bg-slate-700/50 p-4 hover:bg-slate-700 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-white">{tag.name}</h3>
                      {tag.description && (
                        <p className="mt-1 text-sm text-gray-400">{tag.description}</p>
                      )}
                      {tag.category && (
                        <span className="mt-2 inline-block rounded-full bg-purple-600/20 px-2 py-1 text-xs text-purple-400">
                          {tag.category}
                        </span>
                      )}
                    </div>
                    {user?.is_superuser && (
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEdit(tag)}
                          className="text-blue-400 hover:text-blue-300"
                          title="Edit"
                        >
                          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDelete(tag.id)}
                          className="text-red-400 hover:text-red-300"
                          title="Delete"
                          disabled={deleteMutation.isPending}
                        >
                          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Create/Edit Modal */}
      {(isCreateModalOpen || editingTag) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-lg bg-slate-800 p-6 shadow-2xl">
            <h2 className="text-xl font-bold text-white mb-4">
              {editingTag ? 'Edit Tag' : 'Create New Tag'}
            </h2>

            <div className="space-y-4">
              {/* Name */}
              <div>
                <label className="block text-sm font-medium text-gray-300">
                  Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="mt-1 block w-full rounded-md border border-gray-600 bg-slate-700 px-3 py-2 text-white"
                  placeholder="Tag name"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-300">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="mt-1 block w-full rounded-md border border-gray-600 bg-slate-700 px-3 py-2 text-white"
                  placeholder="Tag description"
                  rows={3}
                />
              </div>

              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-gray-300">
                  Category
                </label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="mt-1 block w-full rounded-md border border-gray-600 bg-slate-700 px-3 py-2 text-white"
                  placeholder="e.g., game_mode, role, etc."
                />
              </div>
            </div>

            {/* Error Messages */}
            {(createMutation.error || updateMutation.error) && (
              <div className="mt-4 rounded-md bg-red-500/10 border border-red-500/50 p-3">
                <p className="text-sm text-red-400">
                  {createMutation.error?.message || updateMutation.error?.message}
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setIsCreateModalOpen(false);
                  setEditingTag(null);
                  resetForm();
                }}
                className="rounded-md bg-gray-600 px-4 py-2 text-sm font-semibold text-white hover:bg-gray-500"
              >
                Cancel
              </button>
              <button
                onClick={editingTag ? handleUpdate : handleCreate}
                disabled={createMutation.isPending || updateMutation.isPending}
                className="rounded-md bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-500 disabled:opacity-50"
              >
                {createMutation.isPending || updateMutation.isPending
                  ? 'Saving...'
                  : editingTag
                  ? 'Update'
                  : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
