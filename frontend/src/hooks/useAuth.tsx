"use client";
import { useState, useEffect, useContext, createContext } from 'react';
import api from '@/services/api';
import { AxiosError } from 'axios';

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  phone?: string;
  avatarUrl?: string;
  username?: string;
  role?: string;
  first_name?: string;
  last_name?: string;
  is_verified?: boolean;
  tenant_id?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export type UpdateProfileInput = Partial<Pick<UserProfile, 'name' | 'phone' | 'avatarUrl'>>;

export interface AuthContextType {
  user: UserProfile | null;
  loading: boolean;
  error: string | null;
  logout: () => void;
  updateProfile: (input: UpdateProfileInput) => Promise<{ ok: boolean; error?: string }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDefaultUser = async () => {
      try {
        setLoading(true);
        const res = await api.get('/api/v1/auth/me');
        const data = res.data;
        const name =
          data.name ||
          [data.first_name, data.last_name].filter(Boolean).join(' ') ||
          data.username;
        setUser({ ...data, name });
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

  const logout = () => {
    setUser(null);
  };

  const updateProfile: AuthContextType['updateProfile'] = async (input) => {
    try {
      const payload = {
        name: input.name?.trim(),
        phone: input.phone?.trim(),
        avatarUrl: input.avatarUrl?.trim(),
      };

      const res = await fetch('/api/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        credentials: 'include',
      });

      if (!res.ok) {
        if (res.status === 401 || res.status === 403) {
          return { ok: false, error: 'Unauthorized' };
        }
        const text = await res.text().catch(() => '');
        return { ok: false, error: text || `HTTP ${res.status}` };
      }

      const updated: UserProfile = await res.json();
      setUser((prev) => ({ ...(prev ?? updated), ...updated }));
      return { ok: true };
    } catch (e: any) {
      return { ok: false, error: e?.message || 'Unknown error' };
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
