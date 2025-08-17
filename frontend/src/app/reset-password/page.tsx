"use client";
export const dynamic = "force-dynamic";
import React, { Suspense, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useSearchParams, useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ToastProvider';
import { LoadingSpinner } from '@/components/LoadingSpinner';

const schema = z.object({ password: z.string().min(6) });

type FormData = z.infer<typeof schema>;

function ResetPasswordContent() {
  const { resetPassword, loading } = useAuth();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { showToast } = useToast();
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string>('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    try {
      setError('');
      const token = searchParams.get('token');
      if (!token) {
        setError('Invalid reset token');
        showToast('Invalid reset token', 'error');
        return;
      }

      const ok = await resetPassword(token, data.password);
      if (ok) {
        setDone(true);
        showToast('Password reset successful!', 'success');
        setTimeout(() => router.push('/login'), 2000);
      } else {
        setError('Failed to reset password. The token may be expired.');
        showToast('Failed to reset password', 'error');
      }
    } catch (error) {
      console.error('Password reset error:', error);
      setError('An error occurred. Please try again.');
      showToast('An error occurred during password reset', 'error');
    }
  };

  if (!searchParams.get('token')) {
    return (
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="p-4 text-red-500 text-center">
          <p className="font-bold text-xl mb-2">Invalid Reset Link</p>
          <p>The password reset link is invalid or has expired.</p>
          <button
            onClick={() => router.push('/login')}
            className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
          >
            Return to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      {done ? (
        <div className="text-center">
          <p className="text-green-500 font-bold mb-2">Password updated successfully!</p>
          <p>Redirecting to login page...</p>
          <LoadingSpinner size="sm" />
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 w-full max-w-sm">
          <h1 className="text-2xl font-bold text-center">Reset Password</h1>
          <div>
            <label className="block mb-1 text-sm font-medium" htmlFor="password">New Password</label>
            <input id="password" type="password" {...register('password')} className="w-full border rounded px-3 py-2 text-sm" />
            {errors.password && <p className="text-red-500 text-sm">{errors.password.message}</p>}
          </div>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button
            type="submit"
            disabled={isSubmitting || loading}
            className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 disabled:opacity-50 flex justify-center items-center"
          >
            {isSubmitting || loading ? (
              <>
                <LoadingSpinner size="sm" />
                <span className="ml-2">Updating...</span>
              </>
            ) : (
              'Update Password'
            )}
          </button>
        </form>
      )}
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense>
      <ResetPasswordContent />
    </Suspense>
  );
}
