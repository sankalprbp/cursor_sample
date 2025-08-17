export interface User {
  id: string;
  email: string;
  username: string;
  role: 'tenant_user' | 'tenant_admin' | 'super_admin' | 'agent';
  tenant_id?: string | null;
  is_verified?: boolean;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Tenant {
  id: string;
  name: string;
  created_at?: string;
  updated_at?: string;
  is_active?: boolean;
}

export interface AdminPageState {
  users: User[];
  tenants: Tenant[];
  loading: boolean;
  error: string | null;
  searchTerm: string;
  roleFilter: string;
}

export type UserRole = User['role'];

export interface UserUpdatePayload {
  role?: UserRole;
  tenant_id?: string | null;
  is_active?: boolean;
}