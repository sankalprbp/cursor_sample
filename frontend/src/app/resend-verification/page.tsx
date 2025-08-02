"use client";
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ToastProvider';
import LoadingSpinner from '@/components/LoadingSpinner';
import Link from 'next/link';

const schema = z.object({
  email: z.string().email('Please enter a valid email address')
});

type FormData = z.infer<typeof schema>;

export default function ResendVerificationPage() {
  const { resendVerification, loading } = useAuth();
  const { showToast } = useToast();
  const [sent, setSent] = useState(false);
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema)
  });

  const onSubmit = async (data: FormData) => {
    try {
      const success = await resendVerification(data.email);
      if (success) {
        setSent(true);
        showToast('Verification email sent successfully!', 'success');
      } else {
        showToast('Failed to send verification email. Please try again.', 'error');
      }
    } catch (error) {
      console.error('Error sending verification email:', error);
      showToast('An error occurred. Please try again later.', 'error');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <div className="w-full max-w-md p-6 bg-white shadow-md rounded-lg">
        <h1 className="text-2xl font-bold text-center mb-6">Resend Verification Email</h1>
        
        {sent ? (
          <div className="text-center">
            <div className="text-green-500 text-5xl mb-4">✓</div>
            <h2 className="text-xl font-bold mb-2">Email Sent!</h2>
            <p className="mb-4">We&apos;ve sent a verification link to your email address.</p>
            <p className="text-sm text-gray-500 mb-4">
              If you don&apos;t receive an email within a few minutes, check your spam folder or try again.
            </p>
            <div className="mt-6 flex justify-center space-x-4">
              <Link href="/login" className="text-indigo-600 hover:underline">
                Return to Login
              </Link>
            </div>
          </div>
        ) : (
          <>
            <p className="mb-4 text-gray-600">
              Enter your email address below and we&apos;ll send you a new verification link.
            </p>
            
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="block mb-1 text-sm font-medium" htmlFor="email">Email Address</label>
                <input
                  id="email"
                  type="email"
                  {...register('email')}
                  className="w-full border rounded px-3 py-2 text-sm"
                  placeholder="your.email@example.com"
                />
                {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>}
              </div>
              
              <button
                type="submit"
                disabled={isSubmitting || loading}
                className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 disabled:opacity-50 flex justify-center items-center"
              >
                {(isSubmitting || loading) ? <LoadingSpinner size="small" /> : 'Send Verification Link'}
              </button>
            </form>
            
            <div className="mt-6 text-center">
              <Link href="/login" className="text-indigo-600 hover:underline text-sm">
                Return to Login
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}