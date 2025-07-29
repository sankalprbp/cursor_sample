
"use client";
import React, { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { fetchUsers, fetchTenants, changeUserRole, changeUserTenant } from '@/services/api';

interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  tenant_id?: string | null;
}

interface Tenant {
  id: string;
  name: string;
}

export default function AdminPage() {
  const { user } = useAuth();
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
        .finally(() => setLoading(false));
    }
  }, [user]);

  if (!user) {
    return <div className="p-4">Loading...</div>;
  }
  
  if (user.role !== 'tenant_admin' && user.role !== 'super_admin') {
    return <div className="p-4">Access denied</div>;
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>
      {loading ? (
        <p>Loading users...</p>
      ) : (
        <table className="min-w-full text-sm">
          <thead>
            <tr>
              <th className="px-4 py-2">Email</th>
              <th className="px-4 py-2">Username</th>
              <th className="px-4 py-2">Role</th>
              <th className="px-4 py-2">Tenant</th>
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
                      await changeUserRole(u.id, role);
                      setUsers(prev => prev.map(x => x.id === u.id ? { ...x, role } : x));
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
                      await changeUserTenant(u.id, tid);
                      setUsers(prev => prev.map(x => x.id === u.id ? { ...x, tenant_id: tid } : x));
                    }}
                  >
                    <option value="">None</option>
                    {tenants.map(t => (
                      <option key={t.id} value={t.id}>{t.name}</option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
