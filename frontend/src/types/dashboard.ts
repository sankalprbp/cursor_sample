import { CallStatus, SystemStatusType } from '@/lib/constants';

/**
 * Core call data structure
 */
export interface Call {
  id: string;
  caller_number: string;
  status: CallStatus;
  started_at: string;
  ended_at?: string;
  duration_seconds?: number;
  summary?: string;
  direction?: 'inbound' | 'outbound';
  tenant_id?: string;
}

/**
 * Dashboard statistics
 */
export interface Stats {
  totalCalls: number;
  activeCalls: number;
  averageDuration: number;
  successRate: number;
}

/**
 * System health status
 */
export interface SystemStatus {
  status: SystemStatusType;
  services: {
    database: string;
    redis: string;
    [key: string]: string; // Allow for additional services
  };
  timestamp?: string;
  uptime?: number;
}

/**
 * Complete dashboard data structure
 */
export interface DashboardData {
  calls: Call[];
  stats: Stats;
  systemStatus: SystemStatus | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated?: Date;
}

/**
 * API response types
 */
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
  timestamp?: string;
}

export interface CallsApiResponse extends ApiResponse<{ calls: Call[] }> {
  total?: number;
  limit?: number;
  offset?: number;
  has_more?: boolean;
}

/**
 * Component prop types
 */
export interface StatsGridProps {
  stats: Stats;
  isLoading?: boolean;
}

export interface CallsTableProps {
  calls: Call[];
  isLoading?: boolean;
  onCallSelect?: (call: Call) => void;
}

export interface SystemStatusProps {
  systemStatus: SystemStatus | null;
  showDetails?: boolean;
}

/**
 * Hook return types
 */
export interface UseDashboardDataReturn extends DashboardData {
  refetch: () => Promise<void>;
  refresh: () => void;
}

/**
 * Filter and sort options
 */
export interface CallFilters {
  status?: CallStatus[];
  dateRange?: {
    start: Date;
    end: Date;
  };
  searchTerm?: string;
}

export interface SortOptions {
  field: keyof Call;
  direction: 'asc' | 'desc';
}