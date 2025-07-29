"use client";
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '@/hooks/useAuth';

const schema = z.object({
  email: z.string().email()
});

type FormData = z.infer<typeof schema>;

export default function ForgotPasswordPage() {
  const { requestPasswordReset } = useAuth();
  const [sent, setSent] = useState(false);
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    const ok = await requestPasswordReset(data.email);
    if (ok) setSent(true);
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      {sent ? (
        <p>Check your email for reset instructions.</p>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 w-full max-w-sm">
          <h1 className="text-2xl font-bold text-center">Forgot Password</h1>
          <div>
            <label className="block mb-1 text-sm font-medium" htmlFor="email">Email</label>
            <input id="email" type="email" {...register('email')} className="w-full border rounded px-3 py-2 text-sm" />
            {errors.email && <p className="text-red-500 text-sm">{errors.email.message}</p>}
          </div>
          <button type="submit" disabled={isSubmitting} className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 disabled:opacity-50">
            {isSubmitting ? 'Sending...' : 'Send reset link'}
          </button>
        </form>
      )}
    </div>
  );
}
