import React from 'react';

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

interface UserRowProps {
  user: User;
  tenants: Tenant[];
  onRoleChange: (userId: string, username: string, role: string) => void;
  onTenantChange: (userId: string, username: string, tenantId: string | null) => void;
}

export const UserRow: React.FC<UserRowProps> = ({
  user,
  tenants,
  onRoleChange,
  onTenantChange
}) => {
  return (
    <tr key={user.id} className="border-t hover:bg-gray-50">
      <td className="px-4 py-2 text-sm">{user.email}</td>
      <td className="px-4 py-2 text-sm">{user.username}</td>
      <td className="px-4 py-2">
        <select
          className="border border-gray-300 rounded px-2 py-1 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          value={user.role}
          onChange={(e) => onRoleChange(user.id, user.username, e.target.value)}
        >
          <option value="tenant_user">Tenant User</option>
          <option value="tenant_admin">Tenant Admin</option>
          <option value="super_admin">Super Admin</option>
          <option value="agent">Agent</option>
        </select>
      </td>
      <td className="px-4 py-2">
        <select
          className="border border-gray-300 rounded px-2 py-1 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          value={user.tenant_id || ''}
          onChange={(e) => onTenantChange(user.id, user.username, e.target.value || null)}
        >
          <option value="">None</option>
          {tenants.map(tenant => (
            <option key={tenant.id} value={tenant.id}>
              {tenant.name}
            </option>
          ))}
        </select>
      </td>
      <td className="px-4 py-2">
        <VerificationBadge isVerified={user.is_verified} />
      </td>
    </tr>
  );
};

const VerificationBadge: React.FC<{ isVerified?: boolean }> = ({ isVerified }) => {
  if (isVerified) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
        <svg className="-ml-0.5 mr-1.5 h-2 w-2 text-green-400" fill="currentColor" viewBox="0 0 8 8">
          <circle cx="4" cy="4" r="3" />
        </svg>
        Verified
      </span>
    );
  }
  
  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
      <svg className="-ml-0.5 mr-1.5 h-2 w-2 text-yellow-400" fill="currentColor" viewBox="0 0 8 8">
        <circle cx="4" cy="4" r="3" />
      </svg>
      Pending
    </span>
  );
};