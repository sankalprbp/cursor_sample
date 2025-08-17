"use client";

import React from 'react';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { StatsGrid } from '@/components/dashboard/StatsGrid';
import { CallsTable } from '@/components/dashboard/CallsTable';
import { useDashboardData } from '@/hooks/use-dashboard-data';
import { getSystemStatusColor } from '@/lib/utils';
import type { SystemStatus } from '@/types/dashboard';

// Reusable components for better maintainability
const DashboardHeader: React.FC = () => (
  <header className="bg-white shadow-sm border-b">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center py-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Voice Agent Dashboard</h1>
          <p className="text-gray-600">Monitor and manage your AI phone agents</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
            Demo Mode - No Authentication Required
          </div>
        </div>
      </div>
    </div>
  </header>
);

const SystemStatusCard: React.FC<{ systemStatus: SystemStatus | null }> = ({ systemStatus }) => (
  <div className="bg-white shadow rounded-lg mb-8">
    <div className="px-4 py-5 sm:p-6">
      <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">System Status</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="flex items-center">
          <div className={`w-3 h-3 rounded-full mr-2 ${getSystemStatusColor(systemStatus?.status || 'unknown')}`}></div>
          <span className="text-sm text-gray-600">
            Overall: {systemStatus?.status || 'Unknown'}
          </span>
        </div>
        <div className="flex items-center">
          <div className={`w-3 h-3 rounded-full mr-2 ${
            systemStatus?.services?.database === 'connected' ? 'bg-green-500' : 'bg-red-500'
          }`}></div>
          <span className="text-sm text-gray-600">
            Database: {systemStatus?.services?.database || 'Unknown'}
          </span>
        </div>
        <div className="flex items-center">
          <div className={`w-3 h-3 rounded-full mr-2 ${
            systemStatus?.services?.redis === 'connected' ? 'bg-green-500' : 'bg-red-500'
          }`}></div>
          <span className="text-sm text-gray-600">
            Redis: {systemStatus?.services?.redis || 'Unknown'}
          </span>
        </div>
      </div>
    </div>
  </div>
);

const AccessInfoCard: React.FC = () => (
  <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
    <div className="flex items-center">
      <div className="flex-shrink-0">
        <div className="h-5 w-5 text-blue-400">ℹ️</div>
      </div>
      <div className="ml-3">
        <h3 className="text-sm font-medium text-blue-800">Dashboard Access</h3>
        <div className="mt-2 text-sm text-blue-700">
          <p>✅ <strong>No Authentication Required</strong> - This dashboard is accessible without login</p>
          <p>🔄 <strong>Real-time Data</strong> - Automatically refreshes every 30 seconds</p>
          <p>📱 <strong>Mobile Responsive</strong> - Works on all devices</p>
          <p>🔗 <strong>API Integration</strong> - Fetches live data from backend at http://localhost:8000</p>
        </div>
      </div>
    </div>
  </div>
);

const LoadingSpinner: React.FC = () => (
  <div className="min-h-screen bg-gray-50 flex items-center justify-center">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
  </div>
);

export default function Dashboard() {
  const { calls, stats, systemStatus, isLoading, error } = useDashboardData();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <ErrorBoundary>
        <div className="min-h-screen bg-gray-50">
          <DashboardHeader />
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-red-800">Error Loading Dashboard</h3>
              <p className="mt-2 text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Stats Grid - Using existing component */}
          <StatsGrid stats={stats} isLoading={isLoading} />
          
          {/* System Status */}
          <SystemStatusCard systemStatus={systemStatus} />
          
          {/* Recent Calls - Using existing component */}
          <CallsTable calls={calls} isLoading={isLoading} />
          
          {/* Access Info */}
          <AccessInfoCard />
        </div>
      </div>
    </ErrorBoundary>
  );
}