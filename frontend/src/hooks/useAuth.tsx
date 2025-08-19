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
  tenant_id?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDefaultUser = async () => {
      try {
        setLoading(true);
        const res = await api.get('/api/v1/auth/me');
        setUser(res.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching default user profile:', err);
        const axiosError = err as AxiosError<{ detail?: string }>;
        setError(axiosError.response?.data?.detail || 'Failed to load default user.');
      } finally {
        setLoading(false);
      }
    };

    fetchDefaultUser();
  }, []);

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading,
      error,
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
