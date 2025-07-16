"use client";
import React, { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { fetchUsers } from '@/services/api';

interface User {
  id: string;
  email: string;
  username: string;
  role: string;
}

export default function AdminPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchUsers()
        .then(setUsers)
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
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id} className="border-t">
                <td className="px-4 py-2">{u.email}</td>
                <td className="px-4 py-2">{u.username}</td>
                <td className="px-4 py-2">{u.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
