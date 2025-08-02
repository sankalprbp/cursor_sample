"use client";
import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ToastProvider';
import LoadingSpinner from '@/components/LoadingSpinner';
import Link from 'next/link';

const schema = z.object({
  email: z.string().email('Valid email is required'),
  username: z.string().min(2, 'Username must be at least 2 characters'),
  password: z.string().min(6, 'Password must be at least 6 characters')
});

type FormData = z.infer<typeof schema>;

export default function RegisterPage() {
  const { register: signup, error: authError, loading } = useAuth();
  const router = useRouter();
  const { showToast } = useToast();
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [successMsg, setSuccessMsg] = useState<string>('');
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  // Handle auth errors from the context
  useEffect(() => {
    if (authError) {
      setErrorMsg(authError);
    }
  }, [authError]);

  const onSubmit = async (data: FormData) => {
    try {
      setErrorMsg('');
      setSuccessMsg('');
      const success = await signup(data.email, data.username, data.password);
      if (success) {
        showToast('Registration successful!', 'success');
        setSuccessMsg('Registration successful! Redirecting to dashboard...');
        setTimeout(() => {
          router.push('/dashboard');
        }, 1500);
      } else {
        // More specific error message
        setErrorMsg('Registration failed. Email may already be in use or the verification system is temporarily unavailable.');
        showToast('Please try again or contact support if the issue persists.', 'error');
      }
    } catch (error) {
      console.error('Registration error:', error);
      setErrorMsg('An error occurred during registration. The server might be experiencing issues with the email verification system.');
      showToast('Please try again later or contact support.', 'error');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 w-full max-w-sm p-6 bg-white shadow-md rounded-lg">
        <h1 className="text-2xl font-bold text-center">Register</h1>
        {errorMsg && (
          <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {errorMsg}
          </div>
        )}
        {successMsg && (
          <div className="p-3 bg-green-100 border border-green-400 text-green-700 rounded">
            {successMsg}
          </div>
        )}
        <div>
          <label className="block mb-1 text-sm font-medium" htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            {...register('email')}
            className="w-full border rounded px-3 py-2 text-sm"
          />
          {errors.email && <p className="text-red-500 text-sm">{errors.email.message}</p>}
        </div>
        <div>
          <label className="block mb-1 text-sm font-medium" htmlFor="username">Username</label>
          <input
            id="username"
            type="text"
            {...register('username')}
            className="w-full border rounded px-3 py-2 text-sm"
          />
          {errors.username && <p className="text-red-500 text-sm">{errors.username.message}</p>}
        </div>
        <div>
          <label className="block mb-1 text-sm font-medium" htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            {...register('password')}
            className="w-full border rounded px-3 py-2 text-sm"
          />
          {errors.password && <p className="text-red-500 text-sm">{errors.password.message}</p>}
        </div>
        <button
          type="submit"
          disabled={isSubmitting || loading}
          className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 disabled:opacity-50 flex justify-center items-center"
        >
          {isSubmitting || loading ? (
            <>
              <LoadingSpinner size="small" color="white" />
              <span className="ml-2">Registering...</span>
            </>
          ) : (
            'Register'
          )}
        </button>
        <div className="text-center text-sm">
          Already have an account?{' '}
          <Link href="/login" className="text-indigo-600 hover:underline">
            Login
          </Link>
        </div>
        <div className="text-center text-sm mt-2">
          <p className="text-gray-600 mb-1">After registering, you'll need to verify your email.</p>
          <p className="text-gray-600">
            Didn't receive verification email?{' '}
            <Link href="/resend-verification" className="text-indigo-600 hover:underline">
              Resend it
            </Link>
          </p>
          <p className="text-gray-600 mt-1">
            <strong>Note:</strong> If you're experiencing registration issues, the email verification system might be temporarily unavailable. 
            You can still register and request verification later.
          </p>
        </div>
      </form>
    </div>
  );
}
