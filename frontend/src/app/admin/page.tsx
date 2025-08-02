
"use client";
import React, { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { fetchUsers, fetchTenants, changeUserRole, changeUserTenant } from '@/services/api';
import AuthGuard from '@/components/AuthGuard';
import { useToast } from '@/components/ToastProvider';
import LoadingSpinner from '@/components/LoadingSpinner';
import Link from 'next/link';

interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  tenant_id?: string | null;
  is_verified?: boolean;
}

interface Tenant {
  id: string;
  name: string;
}

export default function AdminPage() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [users, setUsers] = useState<User[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      Promise.all([fetchUsers(), fetchTenants()])
        .then(([u, t]) => {
          setUsers(u);
          setTenants(t);
        })
        .catch(error => {
          console.error('Error fetching admin data:', error);
          showToast('Failed to load admin data', 'error');
        })
        .finally(() => setLoading(false));
    }
  }, [user, showToast]);

  if (user && user.role !== 'tenant_admin' && user.role !== 'super_admin') {
    return <div className="p-4">Access denied. You need admin privileges to view this page.</div>;
  }

  return (
    <AuthGuard>
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>
      
      {user && !user.is_verified && (
        <div className="mb-6 bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                Your email address is not verified. Some admin features may be limited. Please check your inbox for a verification email or 
                <Link href="/resend-verification" className="font-medium underline text-yellow-700 hover:text-yellow-600 ml-1">
                  request a new verification link
                </Link>.
              </p>
            </div>
          </div>
        </div>
      )}
      {loading ? (
        <div className="flex justify-center items-center py-10">
          <LoadingSpinner size="large" />
        </div>
      ) : (
        <table className="min-w-full text-sm">
          <thead>
            <tr>
              <th className="px-4 py-2">Email</th>
              <th className="px-4 py-2">Username</th>
              <th className="px-4 py-2">Role</th>
              <th className="px-4 py-2">Tenant</th>
              <th className="px-4 py-2">Verified</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id} className="border-t">
                <td className="px-4 py-2">{u.email}</td>
                <td className="px-4 py-2">{u.username}</td>
                <td className="px-4 py-2">
                  <select
                    className="border px-2 py-1 text-sm"
                    value={u.role}
                    onChange={async e => {
                      const role = e.target.value;
                      try {
                        await changeUserRole(u.id, role);
                        setUsers(prev => prev.map(x => x.id === u.id ? { ...x, role } : x));
                        showToast(`Changed ${u.username}'s role to ${role}`, 'success');
                      } catch (error) {
                        console.error('Error changing role:', error);
                        showToast('Failed to change user role', 'error');
                      }
                    }}
                  >
                    <option value="tenant_user">tenant_user</option>
                    <option value="tenant_admin">tenant_admin</option>
                    <option value="super_admin">super_admin</option>
                    <option value="agent">agent</option>
                  </select>
                </td>
                <td className="px-4 py-2">
                  <select
                    className="border px-2 py-1 text-sm"
                    value={u.tenant_id || ''}
                    onChange={async e => {
                      const tid = e.target.value || null;
                      try {
                        await changeUserTenant(u.id, tid);
                        setUsers(prev => prev.map(x => x.id === u.id ? { ...x, tenant_id: tid } : x));
                        showToast(`Changed ${u.username}'s tenant`, 'success');
                      } catch (error) {
                        console.error('Error changing tenant:', error);
                        showToast('Failed to change user tenant', 'error');
                      }
                    }}
                  >
                    <option value="">None</option>
                    {tenants.map(t => (
                      <option key={t.id} value={t.id}>{t.name}</option>
                    ))}
                  </select>
                </td>
                <td className="px-4 py-2">
                  {u.is_verified ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      <svg className="-ml-0.5 mr-1.5 h-2 w-2 text-green-400" fill="currentColor" viewBox="0 0 8 8">
                        <circle cx="4" cy="4" r="3" />
                      </svg>
                      Verified
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      <svg className="-ml-0.5 mr-1.5 h-2 w-2 text-yellow-400" fill="currentColor" viewBox="0 0 8 8">
                        <circle cx="4" cy="4" r="3" />
                      </svg>
                      Pending
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
    </AuthGuard>
  );
}
