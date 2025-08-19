"use client";
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ToastProvider';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import Link from 'next/link';

const schema = z.object({
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  username: z.string().min(2).optional(),
});

type FormData = z.infer<typeof schema>;

export default function ProfilePage() {
  const { user, updateProfile, loading } = useAuth();
  const { showToast } = useToast();
  const [updateSuccess, setUpdateSuccess] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { first_name: user?.first_name ?? '', last_name: user?.last_name ?? '', username: user?.username ?? '' },
  });

  const onSubmit = async (data: FormData) => {
    try {
      setUpdateSuccess(false);
      await updateProfile(data);
      showToast('Profile updated successfully!', 'success');
      setUpdateSuccess(true);
    } catch (error) {
      console.error('Profile update error:', error);
      showToast('Failed to update profile. Please try again.', 'error');
    }
  };



  return (
    <div className="p-4 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-4">My Profile</h1>
      
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
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium" htmlFor="first_name">First Name</label>
          <input id="first_name" {...register('first_name')} className="w-full border rounded px-3 py-2 text-sm" />
          {errors.first_name && <p className="text-red-500 text-sm">{errors.first_name.message}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium" htmlFor="last_name">Last Name</label>
          <input id="last_name" {...register('last_name')} className="w-full border rounded px-3 py-2 text-sm" />
          {errors.last_name && <p className="text-red-500 text-sm">{errors.last_name.message}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium" htmlFor="username">Username</label>
          <input id="username" {...register('username')} className="w-full border rounded px-3 py-2 text-sm" />
          {errors.username && <p className="text-red-500 text-sm">{errors.username.message}</p>}
        </div>
        <button 
          type="submit" 
          disabled={isSubmitting || loading} 
          className="bg-indigo-600 text-white px-4 py-2 rounded flex items-center justify-center"
        >
          {isSubmitting || loading ? (
            <>
              <LoadingSpinner size="sm" />
              <span className="ml-2">Saving...</span>
            </>
          ) : (
            'Save'
          )}
        </button>
        {updateSuccess && (
          <p className="text-green-500 mt-2">Profile updated successfully!</p>
        )}
      </form>
    </div>
  );
}
