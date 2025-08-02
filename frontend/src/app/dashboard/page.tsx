"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Phone, PhoneCall, MessageSquare, BarChart3, Settings, Upload, FileText, Users, Clock } from 'lucide-react';
import AICallingPanel from '@/components/AICallingPanel';
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
  const [calls, setCalls] = useState<Call[]>([]);
  const [stats, setStats] = useState<Stats>({
    totalCalls: 0,
    activeCalls: 0,
    averageDuration: 0,
    successRate: 0
  });

  // Demo data for demonstration purposes
  useEffect(() => {
    // Simulate demo data
    const demoCalls: Call[] = [
      {
        id: '1',
        caller_number: '+1 (555) 123-4567',
        status: 'completed',
        started_at: new Date(Date.now() - 300000).toISOString(),
        ended_at: new Date(Date.now() - 240000).toISOString(),
        duration_seconds: 60,
        summary: 'Customer inquired about product pricing and features. AI agent provided detailed information and scheduled a follow-up call.'
      },
      {
        id: '2',
        caller_number: '+1 (555) 987-6543',
        status: 'active',
        started_at: new Date(Date.now() - 120000).toISOString(),
        duration_seconds: 120,
        summary: 'In progress...'
      },
      {
        id: '3',
        caller_number: '+1 (555) 456-7890',
        status: 'completed',
        started_at: new Date(Date.now() - 600000).toISOString(),
        ended_at: new Date(Date.now() - 540000).toISOString(),
        duration_seconds: 60,
        summary: 'Technical support call. AI agent resolved customer issue with account access.'
      }
    ];

    setCalls(demoCalls);
    const completed = demoCalls.filter(c => c.status === 'completed');
    const avg = completed.reduce((sum, c) => sum + (c.duration_seconds || 0), 0) / (completed.length || 1);
    setStats({
      totalCalls: demoCalls.length,
      activeCalls: demoCalls.filter(c => c.status === 'active').length,
      averageDuration: avg,
      successRate: completed.length / (demoCalls.length || 1) * 100,
    });
  }, []);

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatTime = (isoString: string) => {
    return new Date(isoString).toLocaleString();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
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
                onClick={() => router.push('/login')}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Login
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Demo Notice */}
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

        {/* AI Calling Panel */}
        <div className="mb-8">
          <AICallingPanel 
            onCallStarted={(callId) => {
              console.log('Call started:', callId);
              // Add demo call to the list
              const newCall: Call = {
                id: callId,
                caller_number: '+1 (555) 123-4567', // Demo number
                status: 'active',
                started_at: new Date().toISOString(),
                duration_seconds: 0,
                summary: 'In progress...'
              };
              setCalls(prev => [newCall, ...prev]);
              setStats(prev => ({
                ...prev,
                totalCalls: prev.totalCalls + 1,
                activeCalls: prev.activeCalls + 1
              }));
            }}
            onCallEnded={(callId) => {
              console.log('Call ended:', callId);
              // Update call status in demo data
              setCalls(prev => prev.map(call => 
                call.id === callId 
                  ? { ...call, status: 'completed', ended_at: new Date().toISOString() }
                  : call
              ));
              setStats(prev => ({
                ...prev,
                activeCalls: Math.max(0, prev.activeCalls - 1)
              }));
            }}
          />
        </div>

        {/* Quick Actions */}
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
    </div>
  );
}