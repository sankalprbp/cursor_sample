import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/lib/api-config';
import { safeAsync, logError, getErrorMessage } from '@/lib/error-handling';
import { TIMING, DEFAULTS } from '@/lib/constants';
import type { Call, Stats, SystemStatus, UseDashboardDataReturn } from '@/types/dashboard';
import type { SystemStatusType } from '@/lib/constants';

// Remove duplicate interfaces - now imported from types

const DEMO_CALLS: Call[] = [
  {
    id: '1',
    caller_number: '+1 (555) 123-4567',
    status: 'completed',
    started_at: new Date(Date.now() - 300000).toISOString(),
    ended_at: new Date(Date.now() - 240000).toISOString(),
    duration_seconds: 180,
    summary: 'Customer inquired about product pricing and features. AI agent provided detailed information and scheduled a follow-up call.'
  },
  {
    id: '2',
    caller_number: '+1 (555) 987-6543',
    status: 'active',
    started_at: new Date(Date.now() - 120000).toISOString(),
    duration_seconds: 120,
    summary: 'Call in progress - Customer asking about services...'
  },
  {
    id: '3',
    caller_number: '+1 (555) 456-7890',
    status: 'completed',
    started_at: new Date(Date.now() - 600000).toISOString(),
    ended_at: new Date(Date.now() - 540000).toISOString(),
    duration_seconds: 180,
    summary: 'Technical support call. AI agent resolved customer issue with account access.'
  }
];

const calculateStats = (calls: Call[]): Stats => {
  const completed = calls.filter(c => c.status === 'completed');
  const active = calls.filter(c => c.status === 'active');
  const avg = completed.length > 0 
    ? completed.reduce((sum, c) => sum + (c.duration_seconds || 0), 0) / completed.length
    : 0;
  
  return {
    totalCalls: calls.length,
    activeCalls: active.length,
    averageDuration: avg,
    successRate: calls.length > 0 ? (completed.length / calls.length) * 100 : 0,
  };
};

export const useDashboardData = (): UseDashboardDataReturn => {
  const [calls, setCalls] = useState<Call[]>([]);
  const [stats, setStats] = useState<Stats>(DEFAULTS.STATS);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    // Fetch calls data with error handling
    const { data: callsData, error: callsError } = await safeAsync(
      () => apiClient.getDemoCalls(),
      { calls: DEMO_CALLS, total: DEMO_CALLS.length }
    );

    // Fetch health data with error handling
    const { data: healthData, error: healthError } = await safeAsync(
      () => apiClient.getSystemStatus(),
      {
        status: 'healthy' as 'healthy' | 'degraded' | 'unhealthy',
        services: { database: 'connected', redis: 'connected' }
      }
    );

    // Process calls data
    if (callsData) {
      const apiCalls = callsData.calls || [];
      
      // Convert API format to component format with proper type safety
      const formattedCalls: Call[] = apiCalls.map((call: any) => ({
        id: call.id,
        caller_number: call.caller_number,
        status: call.status as 'active' | 'completed' | 'failed',
        started_at: call.started_at,
        ended_at: call.ended_at,
        duration_seconds: call.duration_seconds,
        summary: call.summary
      }));

      setCalls(formattedCalls);
      setStats(calculateStats(formattedCalls));
    }

    // Process health data
    if (healthData) {
      setSystemStatus({
        ...healthData,
        status: healthData.status as SystemStatusType,
        services: {
          database: healthData.services?.database || 'unknown',
          redis: healthData.services?.redis || 'unknown',
          ...healthData.services
        }
      });
    }

    // Set error if both critical operations failed
    if (callsError && healthError) {
      const errorMessage = getErrorMessage(callsError);
      setError(errorMessage);
      logError(callsError, { context: 'dashboard_data_fetch' });
    }

    setIsLoading(false);
  }, []);

  // Refresh function for manual updates
  const refresh = useCallback(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, TIMING.REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  return {
    calls,
    stats,
    systemStatus,
    isLoading,
    error,
    refetch: fetchDashboardData,
    refresh,
    lastUpdated: new Date()
  };
};