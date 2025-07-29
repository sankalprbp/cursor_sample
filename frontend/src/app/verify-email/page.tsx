"use client";
import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

export default function VerifyEmailPage() {
  const { verifyEmail } = useAuth();
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');

  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      verifyEmail(token).then(ok => {
        setStatus(ok ? 'success' : 'error');
        if (ok) {
          setTimeout(() => router.push('/dashboard'), 2000);
        }
      });
    } else {
      setStatus('error');
    }
  }, [searchParams]);

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      {status === 'verifying' && <p>Verifying email...</p>}
      {status === 'success' && <p>Email verified! Redirecting...</p>}
      {status === 'error' && <p className="text-red-500">Invalid or expired token.</p>}
    </div>
  );
}
