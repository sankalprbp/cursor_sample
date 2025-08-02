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
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters')
});

type FormData = z.infer<typeof schema>;

export default function LoginPage() {
  const { login, error: authError, loading, clearError } = useAuth();
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
      // Clear the error from context after displaying it
      clearError();
    }
  }, [authError, clearError]);

  const onSubmit = async (data: FormData) => {
    try {
      setErrorMsg('');
      const success = await login(data.email, data.password);
      if (success) {
        showToast('Login successful! Welcome back.', 'success');
        router.push('/dashboard');
      } else {
        // Error message is already set by the auth hook
        showToast('Login failed. Please check your credentials.', 'error');
      }
    } catch (error) {
      console.error('Login error:', error);
      setErrorMsg('An unexpected error occurred. Please try again later.');
      showToast('An unexpected error occurred.', 'error');
    }
  };

  const handleInputChange = () => {
    // Clear error when user starts typing
    if (errorMsg) {
      setErrorMsg('');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4 bg-gray-50">
      <div className="w-full max-w-md">
        <div className="bg-white shadow-lg rounded-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h1>
            <p className="text-gray-600">Sign in to your account</p>
          </div>
          
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {errorMsg && (
              <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium">{errorMsg}</p>
                  </div>
                </div>
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="email">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                {...register('email')}
                onChange={(e) => {
                  register('email').onChange(e);
                  handleInputChange();
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Enter your email"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                {...register('password')}
                onChange={(e) => {
                  register('password').onChange(e);
                  handleInputChange();
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Enter your password"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>
            
            <button
              type="submit"
              disabled={isSubmitting || loading}
              className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center font-medium transition-colors duration-200"
            >
              {isSubmitting || loading ? (
                <>
                  <LoadingSpinner size="small" color="white" />
                  <span className="ml-2">Signing in...</span>
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>
          
          <div className="mt-6 space-y-4">
            <div className="text-center">
              <Link 
                href="/forgot-password" 
                className="text-sm text-indigo-600 hover:text-indigo-500 hover:underline transition-colors duration-200"
              >
                Forgot your password?
              </Link>
            </div>
            
            <div className="text-center">
              <span className="text-sm text-gray-600">Don&apos;t have an account? </span>
              <Link 
                href="/register" 
                className="text-sm text-indigo-600 hover:text-indigo-500 hover:underline transition-colors duration-200"
              >
                Sign up
              </Link>
            </div>
            
            <div className="text-center">
              <span className="text-sm text-gray-600">Didn&apos;t receive verification email? </span>
              <Link 
                href="/resend-verification" 
                className="text-sm text-indigo-600 hover:text-indigo-500 hover:underline transition-colors duration-200"
              >
                Resend it
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
