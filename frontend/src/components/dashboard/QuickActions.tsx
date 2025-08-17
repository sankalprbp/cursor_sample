import React from 'react';
import { Settings, Upload, BarChart3 } from 'lucide-react';

export const QuickActions: React.FC = () => (
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