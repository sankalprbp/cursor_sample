"use client";
import { useState, useEffect, useContext, createContext } from 'react';
import api from '@/services/api';

interface User {
  id: string;
  email: string;
  username: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, username: string, password: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      api.get('/api/v1/auth/me')
        .then(res => setUser(res.data))
        .catch(() => logout());
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const res = await api.post('/api/v1/auth/login', { email, password });
      localStorage.setItem('accessToken', res.data.access_token);
      setUser(await fetchMe());
      return true;
    } catch {
      return false;
    }
  };

  const registerUser = async (email: string, username: string, password: string) => {
    try {
      await api.post('/api/v1/auth/register', { email, username, password });
      return await login(email, password);
    } catch {
      return false;
    }
  };

  const fetchMe = async (): Promise<User> => {
    const res = await api.get('/api/v1/auth/me');
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register: registerUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
