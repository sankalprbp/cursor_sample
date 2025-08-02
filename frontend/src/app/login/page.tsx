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
  email: z.string().email(),
  password: z.string().min(6)
});

type FormData = z.infer<typeof schema>;

export default function LoginPage() {
  const { login, error: authError, loading } = useAuth();
  const router = useRouter();
  const { showToast } = useToast();
  const [errorMsg, setErrorMsg] = useState<string>('');
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
      const success = await login(data.email, data.password);
      if (success) {
        showToast('Login successful!', 'success');
        router.push('/dashboard');
      } else {
        setErrorMsg('Invalid email or password. Please try again.');
      }
    } catch (error) {
      console.error('Login error:', error);
      setErrorMsg('An error occurred during login. Please try again later.');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 w-full max-w-sm p-6 bg-white shadow-md rounded-lg">
        <h1 className="text-2xl font-bold text-center">Login</h1>
        {errorMsg && (
          <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {errorMsg}
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
              <span className="ml-2">Logging in...</span>
            </>
          ) : (
            'Login'
          )}
        </button>
        <div className="text-center text-sm">
          <Link href="/forgot-password" className="text-indigo-600 hover:underline">
            Forgot password?
          </Link>
        </div>
        <div className="text-center text-sm">
          Don't have an account?{' '}
          <Link href="/register" className="text-indigo-600 hover:underline">
            Register
          </Link>
        </div>
        <div className="text-center text-sm">
          Didn't receive verification email?{' '}
          <Link href="/resend-verification" className="text-indigo-600 hover:underline">
            Resend it
          </Link>
        </div>
      </form>
    </div>
  );
}
