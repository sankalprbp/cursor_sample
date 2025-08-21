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
  name: z.string().max(100).optional(),
  phone: z.string().max(30).optional(),
  avatarUrl: z.string().url().optional(),
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
    defaultValues: { name: user?.name ?? '', phone: user?.phone ?? '', avatarUrl: user?.avatarUrl ?? '' },
  });

  const onSubmit = async (data: FormData) => {
    setUpdateSuccess(false);
    const result = await updateProfile(data);
    if (!result.ok) {
      showToast(result.error ?? 'Failed to update profile', 'error');
      return;
    }
    showToast('Profile updated successfully!', 'success');
    setUpdateSuccess(true);
  };

  if (loading) {
    return (
      <div className="p-4 max-w-md mx-auto">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="p-4 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-4">My Profile</h1>

      {user && !user.is_verified && (
        <div className="mb-6 bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                Your email address is not verified. Some features may be limited. Please check your inbox for a verification email or
                <Link
                  href="/resend-verification"
                  className="font-medium underline text-yellow-700 hover:text-yellow-600 ml-1"
                >
                  request a new verification link
                </Link>
                .
              </p>
            </div>
          </div>
        </div>
      )}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium" htmlFor="name">
            Name
          </label>
          <input id="name" {...register('name')} className="w-full border rounded px-3 py-2 text-sm" />
          {errors.name && <p className="text-red-500 text-sm">{errors.name.message}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium" htmlFor="phone">
            Phone
          </label>
          <input id="phone" {...register('phone')} className="w-full border rounded px-3 py-2 text-sm" />
          {errors.phone && <p className="text-red-500 text-sm">{errors.phone.message}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium" htmlFor="avatarUrl">
            Avatar URL
          </label>
          <input id="avatarUrl" {...register('avatarUrl')} className="w-full border rounded px-3 py-2 text-sm" />
          {errors.avatarUrl && <p className="text-red-500 text-sm">{errors.avatarUrl.message}</p>}
        </div>
        <button
          type="submit"
          disabled={isSubmitting}
          className="bg-indigo-600 text-white px-4 py-2 rounded flex items-center justify-center"
        >
          {isSubmitting ? (
            <>
              <LoadingSpinner size="sm" />
              <span className="ml-2">Saving...</span>
            </>
          ) : (
            'Save'
          )}
        </button>
        {updateSuccess && <p className="text-green-500 mt-2">Profile updated successfully!</p>}
      </form>
    </div>
  );
}
