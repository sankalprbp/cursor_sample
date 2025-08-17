import React from 'react';

interface DashboardHeaderProps {
  onLoginClick: () => void;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({ onLoginClick }) => (
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