"use client";
import { useState, useEffect, useContext, createContext } from 'react';
import api from '@/services/api';
import { AxiosError } from 'axios';

interface User {
  id: string;
  email: string;
  username: string;
  role?: string;
  first_name?: string;
  last_name?: string;
  is_verified?: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, username: string, password: string) => Promise<boolean>;
  updateProfile: (data: Partial<User>) => Promise<boolean>;
  verifyEmail: (token: string) => Promise<boolean>;
  resendVerification: (email: string) => Promise<boolean>;
  requestPasswordReset: (email: string) => Promise<boolean>;
  resetPassword: (token: string, newPassword: string) => Promise<boolean>;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMe = async (): Promise<User> => {
    const res = await api.get('/api/v1/auth/me');
    return res.data;
  };

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      setLoading(true);
      fetchMe()
        .then((u) => {
          setUser(u);
          setError(null);
        })
        .catch((err) => {
          console.error('Error fetching user profile:', err);
          logout();
          setError('Session expired. Please login again.');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.post('/api/v1/auth/login', { email, password });
      localStorage.setItem('accessToken', res.data.access_token);
      localStorage.setItem('refreshToken', res.data.refresh_token);
      setUser(await fetchMe());
      return true;
    } catch (err) {
      const axiosError = err as AxiosError<{detail: string}>;
      if (axiosError.response?.status === 401) {
        setError('Invalid credentials. Please check your email and password.');
      } else if (axiosError.response?.status === 403) {
        setError('Your account is disabled. Please contact support.');
      } else {
        setError('Login failed. Please try again later.');
      }
      console.error('Login error:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const registerUser = async (email: string, username: string, password: string) => {
    try {
      setLoading(true);
      setError(null);
      
      // First try to register the user
      try {
        await api.post('/api/v1/auth/register', { email, username, password });
      } catch (registerErr) {
        const axiosError = registerErr as AxiosError<{detail: string}>;
        if (axiosError.response?.status === 409) {
          setError('Email already registered. Please use a different email or try logging in.');
          console.error('Registration error: Email already registered');
          return false;
        }
        // For other registration errors, we'll still try to log in
        // This handles cases where the backend created the user but failed to send verification email
        console.warn('Registration API error, attempting login anyway:', registerErr);
      }
      
      // Try to log in regardless of registration result
      // This handles cases where user was created but email verification failed
      try {
        const loginSuccess = await login(email, password);
        if (loginSuccess) {
          return true;
        }
      } catch (loginErr) {
        console.error('Login after registration failed:', loginErr);
      }
      
      // If we get here, either registration or login failed
      setError('Registration completed but verification system is unavailable. You can try logging in or use the resend verification option.');
      return false;
    } catch (err) {
      setError('Registration failed. Please try again later.');
      console.error('Registration error:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (data: Partial<User>) => {
    if (!user) return false;
    try {
      const updated = await api.put(`/api/v1/users/${user.id}`, data);
      setUser(updated.data);
      return true;
    } catch {
      return false;
    }
  };

  const verifyEmail = async (token: string) => {
    try {
      await api.post('/api/v1/auth/verify-email', { token });
      if (user) {
        setUser({ ...user, is_verified: true });
      }
      return true;
    } catch {
      return false;
    }
  };

  const resendVerification = async (email: string) => {
    try {
      setLoading(true);
      await api.post('/api/v1/auth/resend-verification', { email });
      return true;
    } catch (error) {
      console.error('Error resending verification email:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const requestPasswordReset = async (email: string) => {
    try {
      await api.post('/api/v1/auth/forgot-password', { email });
      return true;
    } catch {
      return false;
    }
  };

  const resetPassword = async (token: string, newPassword: string) => {
    try {
      await api.post('/api/v1/auth/reset-password', { token, new_password: newPassword });
      return true;
    } catch {
      return false;
    }
  };

  const logout = () => {
    try {
      // Attempt to blacklist the refresh token on the server
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        api.post('/api/v1/auth/logout', { refresh_token: refreshToken })
          .catch(err => console.error('Error during logout:', err));
      }
    } finally {
      // Always clear local storage and state, even if server request fails
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      setUser(null);
      setError(null);
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      login, 
      register: registerUser, 
      updateProfile, 
      verifyEmail, 
      resendVerification,
      requestPasswordReset, 
      resetPassword, 
      logout,
      error 
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
