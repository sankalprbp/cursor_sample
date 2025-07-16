"use client";
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '@/hooks/useAuth';

const schema = z.object({
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  username: z.string().min(2).optional(),
});

type FormData = z.infer<typeof schema>;

export default function ProfilePage() {
  const { user, updateProfile } = useAuth();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { first_name: user?.first_name ?? '', last_name: user?.last_name ?? '', username: user?.username ?? '' },
  });

  const onSubmit = async (data: FormData) => {
    await updateProfile(data);
  };

  if (!user) return <div className="p-4">Loading...</div>;

  return (
    <div className="p-4 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-4">My Profile</h1>
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
        <button type="submit" disabled={isSubmitting} className="bg-indigo-600 text-white px-4 py-2 rounded">
          {isSubmitting ? 'Saving...' : 'Save'}
        </button>
      </form>
    </div>
  );
}
