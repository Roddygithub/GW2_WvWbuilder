/**
 * Authentication Hook
 * Manages user authentication state and operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { 
  login, 
  register, 
  getCurrentUser, 
  logout as apiLogout,
  type LoginRequest,
  type RegisterRequest,
  type User
} from '../api/auth';
import { removeAuthToken, getAuthToken } from '../api/client';
import { toast } from 'sonner';

// Re-export types for convenience
export type { LoginRequest as LoginCredentials, RegisterRequest as RegisterData, User };

/**
 * Main authentication hook
 */
export const useAuth = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  // Get current user query
  const { data: user, isLoading: isLoadingUser, error } = useQuery<User | null>({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const token = getAuthToken();
      if (!token) return null;
      try {
        return await getCurrentUser();
      } catch (error) {
        removeAuthToken();
        return null;
      }
    },
    retry: false,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: async (credentials: LoginRequest) => {
      const response = await login(credentials);
      return response;
    },
    onSuccess: () => {
      // Token already set by login function
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      toast.success('Connexion réussie!');
      navigate('/dashboard');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erreur de connexion');
    },
  });

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: async (data: RegisterRequest) => {
      const response = await register(data);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      toast.success('Compte créé avec succès! Veuillez vous connecter.');
      navigate('/login');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erreur lors de l\'inscription');
    },
  });

  // Logout function
  const logout = async () => {
    try {
      await apiLogout();
    } catch (error) {
      // Continue even if API call fails
    } finally {
      removeAuthToken();
      queryClient.clear();
      toast.success('Déconnexion réussie');
      navigate('/login');
    }
  };

  return {
    user,
    isAuthenticated: !!user && !!getAuthToken(),
    isLoading: isLoadingUser,
    error,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout,
    isLoginLoading: loginMutation.isPending,
    isRegisterLoading: registerMutation.isPending,
  };
};

/**
 * Hook to check if user is authenticated (for route protection)
 */
export const useRequireAuth = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  if (!isLoading && !isAuthenticated) {
    navigate('/login');
  }

  return { isAuthenticated, isLoading };
};
