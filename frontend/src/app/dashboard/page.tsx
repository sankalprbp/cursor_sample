"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Phone, PhoneCall, MessageSquare, BarChart3, Settings, Upload, FileText, Users, Clock } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { fetchCalls } from '@/services/api';
import AuthGuard from '@/components/AuthGuard';
import Link from 'next/link';

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

export default function Dashboard() {
  const router = useRouter();
  const { user } = useAuth();
  const [calls, setCalls] = useState<Call[]>([]);
  const [stats, setStats] = useState<Stats>({
    totalCalls: 0,
    activeCalls: 0,
    averageDuration: 0,
    successRate: 0
  });
  const [isStartingCall, setIsStartingCall] = useState(false);
  const [testPhoneNumber, setTestPhoneNumber] = useState('+1-555-0123');

  // Load calls from API
  useEffect(() => {
    fetchCalls()
      .then((data) => {
        setCalls(data);
        const completed = data.filter((c: any) => c.status === 'completed');
        const avg =
          completed.reduce((sum: number, c: any) => sum + (c.duration_seconds || 0), 0) /
          (completed.length || 1);
        setStats({
          totalCalls: data.length,
          activeCalls: data.filter((c: any) => c.status === 'active').length,
          averageDuration: avg,
          successRate: completed.length / (data.length || 1) * 100,
        });
      })
      .catch(() => {})
      .finally(() => {});
  }, [user]);

  const handleStartTestCall = async () => {
    setIsStartingCall(true);
    try {
      // In a real app, this would call the backend API
      // For now, simulate starting a call
      setTimeout(() => {
        const newCall: Call = {
          id: Date.now().toString(),
          caller_number: testPhoneNumber,
          status: 'active',
          started_at: new Date().toISOString(),
        };
        setCalls(prev => [newCall, ...prev]);
        setStats(prev => ({ ...prev, activeCalls: prev.activeCalls + 1, totalCalls: prev.totalCalls + 1 }));
        setIsStartingCall(false);
      }, 1000);
    } catch (error) {
      console.error('Failed to start call:', error);
      setIsStartingCall(false);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatTime = (isoString: string) => {
    return new Date(isoString).toLocaleString();
  };

  if (!user) {
    return <div className="p-4">Loading...</div>;
  }

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
      </div>
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Voice Agent Dashboard</h1>
              <p className="text-gray-600">Monitor and manage your AI phone agents</p>
            </div>
            <div className="flex items-center space-x-4">
              <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </button>
            </div>
          </div>
        </div>
      </header>

      {user && !user.is_verified && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 mt-4">
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-700">
                  Your email address is not verified. Please check your inbox for a verification email or 
                  <Link href="/resend-verification" className="font-medium underline text-yellow-700 hover:text-yellow-600 ml-1">
                    request a new verification link
                  </Link>.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Phone className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Calls</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.totalCalls}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <PhoneCall className="h-6 w-6 text-green-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Active Calls</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.activeCalls}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Clock className="h-6 w-6 text-blue-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Avg Duration</dt>
                    <dd className="text-lg font-medium text-gray-900">{formatDuration(Math.round(stats.averageDuration))}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BarChart3 className="h-6 w-6 text-purple-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Success Rate</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.successRate.toFixed(1)}%</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              
              {/* Start Test Call */}
              <div className="border border-gray-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Start Test Call</h4>
                <p className="text-sm text-gray-500 mb-3">Test your AI agent with a simulated call</p>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={testPhoneNumber}
                    onChange={(e) => setTestPhoneNumber(e.target.value)}
                    className="flex-1 min-w-0 block w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    placeholder="Phone number"
                  />
                  <button
                    onClick={handleStartTestCall}
                    disabled={isStartingCall}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {isStartingCall ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <PhoneCall className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

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
            </div>
          </div>
        </div>

        {/* Recent Calls */}
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
                  {calls.map((call) => (
                    <tr key={call.id} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {call.caller_number}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          call.status === 'active' 
                            ? 'bg-green-100 text-green-800'
                            : call.status === 'completed'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
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
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </AuthGuard>
  );
}