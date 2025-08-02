"use client";
import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import AuthGuard from '@/components/AuthGuard';
import Link from 'next/link';

export default function SettingsPage() {
  const { user } = useAuth();
  return (
    <AuthGuard>
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Settings</h1>
      
      {user && !user.is_verified && (
        <div className="mb-6 bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                Your email address is not verified. Some features may be limited. Please check your inbox for a verification email or 
                <Link href="/resend-verification" className="font-medium underline text-yellow-700 hover:text-yellow-600 ml-1">
                  request a new verification link
                </Link>.
              </p>
            </div>
          </div>
        </div>
      )}
      
      <p>Configuration options will go here.</p>
    </div>
    </AuthGuard>
  );
}
