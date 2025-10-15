/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 */

import { useEffect } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { isAuthenticated as tokenAuthenticated } from "../api/auth";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const {
    isAuthenticated: storeIsAuthenticated,
    loadUser,
    user,
  } = useAuthStore();
  const location = useLocation();
  const hasToken = tokenAuthenticated();

  useEffect(() => {
    if (hasToken && !user) {
      loadUser();
    }
  }, [hasToken, user, loadUser]);

  if (!hasToken && !storeIsAuthenticated) {
    // Redirect to login with return URL
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
