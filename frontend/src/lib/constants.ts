export type CallStatus = 'active' | 'completed' | 'failed';
export type SystemStatusType = 'healthy' | 'degraded' | 'unhealthy';

export const TIMING = {
  REFRESH_INTERVAL_MS: 30000,
};

export const DEFAULTS = {
  STATS: {
    totalCalls: 0,
    activeCalls: 0,
    averageDuration: 0,
    successRate: 0,
  },
};
