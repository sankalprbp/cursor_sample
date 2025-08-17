import React from 'react';
import { Phone, PhoneCall, Clock, BarChart3 } from 'lucide-react';

interface Stats {
  totalCalls: number;
  activeCalls: number;
  averageDuration: number;
  successRate: number;
}

interface StatsGridProps {
  stats: Stats;
  isLoading?: boolean;
}

const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const StatCard: React.FC<{
  icon: React.ReactNode;
  title: string;
  value: string | number;
  isLoading?: boolean;
}> = ({ icon, title, value, isLoading }) => (
  <div className="bg-white overflow-hidden shadow rounded-lg">
    <div className="p-5">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          {icon}
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd className="text-lg font-medium text-gray-900">
              {isLoading ? (
                <div className="animate-pulse bg-gray-200 h-6 w-16 rounded"></div>
              ) : (
                value
              )}
            </dd>
          </dl>
        </div>
      </div>
    </div>
  </div>
);

export const StatsGrid: React.FC<StatsGridProps> = ({ stats, isLoading }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatCard
        icon={<Phone className="h-6 w-6 text-gray-400" />}
        title="Total Calls"
        value={stats.totalCalls}
        isLoading={isLoading}
      />
      <StatCard
        icon={<PhoneCall className="h-6 w-6 text-green-400" />}
        title="Active Calls"
        value={stats.activeCalls}
        isLoading={isLoading}
      />
      <StatCard
        icon={<Clock className="h-6 w-6 text-blue-400" />}
        title="Avg Duration"
        value={formatDuration(Math.round(stats.averageDuration))}
        isLoading={isLoading}
      />
      <StatCard
        icon={<BarChart3 className="h-6 w-6 text-purple-400" />}
        title="Success Rate"
        value={`${stats.successRate.toFixed(1)}%`}
        isLoading={isLoading}
      />
    </div>
  );
};