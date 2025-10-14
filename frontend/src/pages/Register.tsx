/**
 * Register Page
 * New user registration interface
 */

import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export default function Register() {
  const navigate = useNavigate();
  const { register, isLoading, error, clearError } = useAuthStore();
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
  });
  const [localError, setLocalError] = useState('');
  const [fieldErrors, setFieldErrors] = useState<{
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});
  const [touched, setTouched] = useState<{
    email?: boolean;
    password?: boolean;
    confirmPassword?: boolean;
  }>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    
    // Clear field error when user starts typing
    if (fieldErrors[name as keyof typeof fieldErrors]) {
      setFieldErrors({
        ...fieldErrors,
        [name]: undefined,
      });
    }
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setTouched({
      ...touched,
      [name]: true,
    });

    // Validate on blur
    if (name === 'email' && value) {
      if (!validateEmail(value)) {
        setFieldErrors({
          ...fieldErrors,
          email: 'Please enter a valid email address',
        });
      }
    } else if (name === 'password' && value) {
      const passwordError = validatePassword(value);
      if (passwordError) {
        setFieldErrors({
          ...fieldErrors,
          password: passwordError,
        });
      }
    } else if (name === 'confirmPassword' && value) {
      if (value !== formData.password) {
        setFieldErrors({
          ...fieldErrors,
          confirmPassword: 'Passwords do not match',
        });
      }
    }
  };

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validatePassword = (password: string): string | null => {
    if (password.length < 8) {
      return 'Password must be at least 8 characters (minimum 8 characters required)';
    }
    if (!/[A-Z]/.test(password)) {
      return 'Password must contain at least one uppercase letter';
    }
    if (!/[a-z]/.test(password)) {
      return 'Password must contain at least one lowercase letter';
    }
    if (!/[0-9]/.test(password)) {
      return 'Password must contain at least one number';
    }
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
      return 'Password must contain at least one special character';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');
    clearError();

    // Validation des champs requis
    if (!formData.email || !formData.password || !formData.confirmPassword) {
      setLocalError('All required fields must be filled');
      return;
    }

    // Validation de l'email
    if (!validateEmail(formData.email)) {
      setLocalError('Please enter a valid email address');
      return;
    }

    // Validation de la correspondance des mots de passe
    if (formData.password !== formData.confirmPassword) {
      setLocalError('Passwords do not match');
      return;
    }

    // Validation de la force du mot de passe
    const passwordError = validatePassword(formData.password);
    if (passwordError) {
      setLocalError(passwordError);
      return;
    }

    try {
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.fullName || undefined,
      });
      navigate('/dashboard');
    } catch (err) {
      // Error is already set in store
      console.error('Registration error:', err);
    }
  };

  const displayError = error || localError;

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12 px-4">
      <div className="w-full max-w-md space-y-8 rounded-lg bg-slate-800/50 p-8 shadow-2xl backdrop-blur-sm">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white">Register</h1>
          <p className="mt-2 text-sm text-gray-400">
            Sign up to join the GW2 WvW Builder community
          </p>
        </div>

        {/* Registration Form */}
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          {/* Error Message */}
          {displayError && (
            <div className="rounded-md bg-red-500/10 border border-red-500/50 p-3">
              <p className="text-sm text-red-400">{displayError}</p>
            </div>
          )}

          {/* Username Field */}
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-300">
              Username <span className="text-gray-500 text-xs">(optional)</span>
            </label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              value={formData.username}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border border-gray-600 bg-slate-700 px-3 py-2 text-white placeholder-gray-400 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Choose a username (optional)"
            />
          </div>

          {/* Email Field */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-300">
              Email *
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              value={formData.email}
              onChange={handleChange}
              onBlur={handleBlur}
              className={`mt-1 block w-full rounded-md border ${
                touched.email && fieldErrors.email
                  ? 'border-red-500'
                  : 'border-gray-600'
              } bg-slate-700 px-3 py-2 text-white placeholder-gray-400 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500`}
              placeholder="your.email@example.com"
            />
            {touched.email && fieldErrors.email && (
              <p className="mt-1 text-sm text-red-400">{fieldErrors.email}</p>
            )}
          </div>

          {/* Full Name Field (Optional) */}
          <div>
            <label htmlFor="fullName" className="block text-sm font-medium text-gray-300">
              Full Name (Optional)
            </label>
            <input
              id="fullName"
              name="fullName"
              type="text"
              autoComplete="name"
              value={formData.fullName}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border border-gray-600 bg-slate-700 px-3 py-2 text-white placeholder-gray-400 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Your full name"
            />
          </div>

          {/* Password Field */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-300">
              Password *
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="new-password"
              value={formData.password}
              onChange={handleChange}
              onBlur={handleBlur}
              className={`mt-1 block w-full rounded-md border ${
                touched.password && fieldErrors.password
                  ? 'border-red-500'
                  : 'border-gray-600'
              } bg-slate-700 px-3 py-2 text-white placeholder-gray-400 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500`}
              placeholder="At least 8 characters"
            />
            {touched.password && fieldErrors.password && (
              <p className="mt-1 text-sm text-red-400">{fieldErrors.password}</p>
            )}
          </div>

          {/* Confirm Password Field */}
          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300">
              Confirm Password *
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              autoComplete="new-password"
              value={formData.confirmPassword}
              onChange={handleChange}
              onBlur={handleBlur}
              className={`mt-1 block w-full rounded-md border ${
                touched.confirmPassword && fieldErrors.confirmPassword
                  ? 'border-red-500'
                  : 'border-gray-600'
              } bg-slate-700 px-3 py-2 text-white placeholder-gray-400 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500`}
              placeholder="Confirm your password"
            />
            {touched.confirmPassword && fieldErrors.confirmPassword && (
              <p className="mt-1 text-sm text-red-400">{fieldErrors.confirmPassword}</p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-md bg-purple-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-slate-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Creating account...' : 'Create account'}
          </button>

          {/* Login Link */}
          <div className="text-center text-sm">
            <span className="text-gray-400">Already have an account? </span>
            <Link
              to="/login"
              className="font-medium text-purple-400 hover:text-purple-300"
            >
              Sign in here
            </Link>
          </div>
        </form>

        {/* Footer */}
        <div className="text-center text-xs text-gray-500">
          <p>© 2025 GW2 WvW Builder. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
}
