import React from 'react';
import { Call } from '@/types/dashboard';

interface CallsTableProps {
  calls: Call[];
  isLoading?: boolean;
}

const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const formatTime = (isoString: string): string => {
  return new Date(isoString).toLocaleString();
};

const getStatusBadgeClass = (status: string): string => {
  switch (status) {
    case 'active':
      return 'bg-green-100 text-green-800';
    case 'completed':
      return 'bg-blue-100 text-blue-800';
    case 'failed':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const LoadingRow: React.FC = () => (
  <tr className="animate-pulse">
    <td className="px-4 py-4 whitespace-nowrap">
      <div className="h-4 bg-gray-200 rounded w-32"></div>
    </td>
    <td className="px-4 py-4 whitespace-nowrap">
      <div className="h-6 bg-gray-200 rounded w-20"></div>
    </td>
    <td className="px-4 py-4 whitespace-nowrap">
      <div className="h-4 bg-gray-200 rounded w-16"></div>
    </td>
    <td className="px-4 py-4 whitespace-nowrap">
      <div className="h-4 bg-gray-200 rounded w-24"></div>
    </td>
    <td className="px-4 py-4">
      <div className="h-4 bg-gray-200 rounded w-48"></div>
    </td>
  </tr>
);

export const CallsTable: React.FC<CallsTableProps> = ({ calls, isLoading }) => {
  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Calls</h3>
          <button className="text-sm text-indigo-600 hover:text-indigo-500">View all</button>
        </div>
        
        <div className="overflow-hidden">
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Caller
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Started
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Summary
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {isLoading ? (
                Array.from({ length: 3 }).map((_, index) => (
                  <LoadingRow key={index} />
                ))
              ) : (
                calls.map((call) => (
                  <tr key={call.id} className="hover:bg-gray-50">
                    <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {call.caller_number}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadgeClass(call.status)}`}>
                        {call.status}
                      </span>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                      {call.duration_seconds ? formatDuration(call.duration_seconds) : '-'}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatTime(call.started_at)}
                    </td>
                    <td className="px-4 py-4 text-sm text-gray-500 max-w-xs truncate">
                      {call.summary || 'In progress...'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};