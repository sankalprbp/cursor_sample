"use client";
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';

export default function NavBar() {
  const { user, logout } = useAuth();
  return (
    <header className="px-4 lg:px-6 h-14 flex items-center border-b bg-white">
      <Link className="flex items-center justify-center" href="/">
        <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">VA</div>
        <span className="ml-2 text-lg font-semibold">Voice Agent</span>
      </Link>
      <nav className="ml-auto flex gap-4 sm:gap-6">
        <Link className="text-sm font-medium hover:underline" href="/dashboard">Dashboard</Link>
        <Link className="text-sm font-medium hover:underline" href="/admin">Admin</Link>
        <Link className="text-sm font-medium hover:underline" href="/docs">Docs</Link>
        {user ? (
          <button className="text-sm font-medium" onClick={logout}>Logout</button>
        ) : (
          <Link className="text-sm font-medium hover:underline" href="/login">Login</Link>
        )}
      </nav>
    </header>
  );
}
