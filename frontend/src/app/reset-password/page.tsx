"use client";
export const dynamic = "force-dynamic";
import React, { Suspense, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useSearchParams, useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

const schema = z.object({ password: z.string().min(6) });

type FormData = z.infer<typeof schema>;

function ResetPasswordContent() {
  const { resetPassword } = useAuth();
  const searchParams = useSearchParams();
  const router = useRouter();
  const [done, setDone] = useState(false);
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    const token = searchParams.get('token');
    if (!token) return;
    const ok = await resetPassword(token, data.password);
    if (ok) {
      setDone(true);
      setTimeout(() => router.push('/login'), 2000);
    }
  };

  if (!searchParams.get('token')) {
    return <div className="p-4 text-red-500">Invalid reset link.</div>;
  }

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      {done ? (
        <p>Password updated. Redirecting to login...</p>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 w-full max-w-sm">
          <h1 className="text-2xl font-bold text-center">Reset Password</h1>
          <div>
            <label className="block mb-1 text-sm font-medium" htmlFor="password">New Password</label>
            <input id="password" type="password" {...register('password')} className="w-full border rounded px-3 py-2 text-sm" />
            {errors.password && <p className="text-red-500 text-sm">{errors.password.message}</p>}
          </div>
          <button type="submit" disabled={isSubmitting} className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 disabled:opacity-50">
            {isSubmitting ? 'Saving...' : 'Update Password'}
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
