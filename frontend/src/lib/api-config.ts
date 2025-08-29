export const apiClient = {
  async getDemoCalls() {
    return { calls: [], total: 0 };
  },
  async getSystemStatus() {
    return { status: 'healthy', services: { database: 'connected', redis: 'connected' } };
  },
};
