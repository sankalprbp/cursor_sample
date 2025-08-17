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
  email: z.string().email()
});

type FormData = z.infer<typeof schema>;

export default function ForgotPasswordPage() {
  const { requestPasswordReset, loading } = useAuth();
  const { showToast } = useToast();
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string>('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    try {
      setError('');
      const ok = await requestPasswordReset(data.email);
      if (ok) {
        setSent(true);
        showToast('Password reset instructions sent to your email', 'success');
      } else {
        setError('Failed to send reset instructions. Please try again.');
        showToast('Failed to send reset instructions', 'error');
      }
    } catch (error) {
      console.error('Password reset request error:', error);
      setError('An error occurred. Please try again later.');
      showToast('An error occurred', 'error');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      {sent ? (
        <div className="text-center p-6 bg-white shadow-md rounded-lg w-full max-w-sm">
          <div className="text-green-500 text-xl mb-4">✓</div>
          <h2 className="text-xl font-bold mb-2">Check Your Email</h2>
          <p className="mb-4">We&apos;ve sent password reset instructions to your email address.</p>
          <p className="text-sm text-gray-500 mb-4">If you don&apos;t receive an email within a few minutes, check your spam folder.</p>
          <Link href="/login" className="text-indigo-600 hover:underline">
            Return to login
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 w-full max-w-sm">
          <h1 className="text-2xl font-bold text-center">Forgot Password</h1>
          <div>
            <label className="block mb-1 text-sm font-medium" htmlFor="email">Email</label>
            <input id="email" type="email" {...register('email')} className="w-full border rounded px-3 py-2 text-sm" />
            {errors.email && <p className="text-red-500 text-sm">{errors.email.message}</p>}
          </div>
          {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
          <button 
            type="submit" 
            disabled={isSubmitting || loading} 
            className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 disabled:opacity-50 flex justify-center items-center"
          >
            {isSubmitting || loading ? (
              <>
                <LoadingSpinner size="sm" />
                <span className="ml-2">Sending...</span>
              </>
            ) : (
              'Send reset link'
            )}
          </button>
          <div className="text-center text-sm mt-4">
            <Link href="/login" className="text-indigo-600 hover:underline">
              Back to login
            </Link>
          </div>
        </form>
      )}
    </div>
  );
}
