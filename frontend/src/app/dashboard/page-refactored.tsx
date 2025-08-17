"use client";

import React from 'react';
import { useRouter } from 'next/navigation';
import { Settings, Upload, BarChart3 } from 'lucide-react';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { StatsGrid } from '@/components/dashboard/StatsGrid';
import { CallsTable } from '@/components/dashboard/CallsTable';
import { useDashboardData } from '@/hooks/use-dashboard-data';
import AICallingPanel from '@/components/AICallingPanel';

interface Call {
  id: string;
  caller_number: string;
  status: 'active' | 'completed' | 'failed';
  started_at: string;
  ended_at?: string;
  duration_seconds?: number;
  summary?: string;
}

interface Stats {
  totalCalls: number;
  activeCalls: number;
  averageDuration: number;
  successRate: number;
}

const DashboardHeader: React.FC<{ onLoginClick: () => void }> = ({ onLoginClick }) => (
  <header className="bg-white shadow-sm border-b">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center py-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Voice Agent Dashboard</h1>
          <p className="text-gray-600">Monitor and manage your AI phone agents</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
            Demo Mode
          </div>
          <button
            onClick={onLoginClick}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Login
          </button>
        </div>
      </div>
    </div>
  </header>
);

const DemoNotice: React.FC = () => (
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 mt-4">
    <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
      <div className="flex">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <p className="text-sm text-blue-700">
            <strong>Demo Mode:</strong> This is a demonstration of the AI calling functionality.
            The AI calling panel below is fully functional and can make real calls using Twilio.
            Login to access the full dashboard with authentication.
          </p>
        </div>
      </div>
    </div>
  </div>
);

const QuickActions: React.FC = () => (
  <div className="bg-white shadow rounded-lg mb-8">
    <div className="px-4 py-5 sm:p-6">
      <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Quick Actions</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        {/* Upload Knowledge */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Upload Knowledge</h4>
          <p className="text-sm text-gray-500 mb-3">Add documents to your knowledge base</p>
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <Upload className="h-4 w-4 mr-2" />
            Upload Files
          </button>
        </div>

        {/* View Analytics */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Analytics</h4>
          <p className="text-sm text-gray-500 mb-3">View detailed call analytics and insights</p>
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <BarChart3 className="h-4 w-4 mr-2" />
            View Reports
          </button>
        </div>

        {/* Settings */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Settings</h4>
          <p className="text-sm text-gray-500 mb-3">Configure your AI agent and preferences</p>
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <Settings className="h-4 w-4 mr-2" />
            Configure
          </button>
        </div>
      </div>
    </div>
  </div>
);

const ErrorDisplay: React.FC<{ error: string; onRetry: () => void }> = ({ error, onRetry }) => (
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div className="bg-red-50 border border-red-200 rounded-lg p-6">
      <div className="flex">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800">Error loading dashboard</h3>
          <div className="mt-2 text-sm text-red-700">
            <p>{error}</p>
          </div>
          <div className="mt-4">
            <button
              onClick={onRetry}
              className="bg-red-100 px-3 py-2 rounded-md text-sm font-medium text-red-800 hover:bg-red-200"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default function Dashboard() {
  const router = useRouter();
  const { calls, stats, systemStatus, isLoading, error, refetch } = useDashboardData();

  const handleCallStarted = (callId: string) => {
    console.log('Call started:', callId);
    // The custom hook will handle data updates automatically
  };

  const handleCallEnded = (callId: string) => {
    console.log('Call ended:', callId);
    // The custom hook will handle data updates automatically
  };

  if (error) {
    return (
      <ErrorBoundary>
        <div className="min-h-screen bg-gray-50">
          <DashboardHeader onLoginClick={() => router.push('/login')} />
          <ErrorDisplay error={error} onRetry={refetch} />
        </div>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader onLoginClick={() => router.push('/login')} />
        <DemoNotice />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Stats Grid */}
          <StatsGrid stats={stats} isLoading={isLoading} />

          {/* AI Calling Panel */}
          <div className="mb-8">
            <AICallingPanel
              onCallStarted={handleCallStarted}
              onCallEnded={handleCallEnded}
            />
          </div>

          {/* Quick Actions */}
          <QuickActions />

          {/* Recent Calls */}
          <CallsTable calls={calls} isLoading={isLoading} />
        </div>
      </div>
    </ErrorBoundary>
  );
}