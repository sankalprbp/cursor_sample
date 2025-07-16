"use client";
import React from 'react';
import { useAuth } from '@/hooks/useAuth';

export default function SettingsPage() {
  const { user } = useAuth();
  if (!user) return <div className="p-4">Loading...</div>;
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Settings</h1>
      <p>Configuration options will go here.</p>
    </div>
  );
}
