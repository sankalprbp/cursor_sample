import { useState, useEffect, useCallback, useMemo } from 'react';
import { User, Tenant } from '@/types/admin';
import { fetchUsers, fetchTenants, changeUserRole, changeUserTenant } from '@/services/api';
import { useToast } from '@/components/ToastProvider';

export const useAdminData = () => {
  const { showToast } = useToast();
  const [users, setUsers] = useState<User[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('all');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [usersData, tenantsData] = await Promise.all([
        fetchUsers(),
        fetchTenants()
      ]);
      setUsers(usersData);
      setTenants(tenantsData);
    } catch (err) {
      const errorMessage = 'Failed to load admin data. Please try again.';
      setError(errorMessage);
      showToast(errorMessage, 'error');
      console.error('Error fetching admin data:', err);
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleRoleChange = useCallback(async (userId: string, username: string, newRole: string) => {
    try {
      await changeUserRole(userId, newRole);
      setUsers(prev => prev.map(user => 
        user.id === userId ? { ...user, role: newRole as User['role'] } : user
      ));
      showToast(`Changed ${username}'s role to ${newRole}`, 'success');
    } catch (error) {
      console.error('Error changing role:', error);
      showToast('Failed to change user role', 'error');
    }
  }, [showToast]);

  const handleTenantChange = useCallback(async (userId: string, username: string, tenantId: string | null) => {
    try {
      await changeUserTenant(userId, tenantId);
      setUsers(prev => prev.map(user => 
        user.id === userId ? { ...user, tenant_id: tenantId } : user
      ));
      showToast(`Changed ${username}'s tenant`, 'success');
    } catch (error) {
      console.error('Error changing tenant:', error);
      showToast('Failed to change user tenant', 'error');
    }
  }, [showToast]);

  const filteredUsers = useMemo(() => {
    return users.filter(user => {
      const matchesSearch = user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           user.username.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesRole = roleFilter === 'all' || user.role === roleFilter;
      return matchesSearch && matchesRole;
    });
  }, [users, searchTerm, roleFilter]);

  const sortedUsers = useMemo(() => {
    return [...filteredUsers].sort((a, b) => a.email.localeCompare(b.email));
  }, [filteredUsers]);

  return {
    users: sortedUsers,
    tenants,
    loading,
    error,
    searchTerm,
    setSearchTerm,
    roleFilter,
    setRoleFilter,
    handleRoleChange,
    handleTenantChange,
    refetch: loadData
  };
};