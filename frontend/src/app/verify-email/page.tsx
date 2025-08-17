"use client";
export const dynamic = "force-dynamic";
import { Suspense, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ToastProvider';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

const emailSchema = z.object({
  email: z.string().email('Please enter a valid email address')
});

type EmailFormData = z.infer<typeof emailSchema>;

function ResendVerificationForm() {
  const { resendVerification } = useAuth();
  const { showToast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sent, setSent] = useState(false);
  
  const { register, handleSubmit, formState: { errors } } = useForm<EmailFormData>({
    resolver: zodResolver(emailSchema)
  });

  const onSubmit = async (data: EmailFormData) => {
    try {
      setIsSubmitting(true);
      const success = await resendVerification(data.email);
      if (success) {
        showToast('Verification email sent successfully!', 'success');
        setSent(true);
      } else {
        showToast('Failed to send verification email. Please try again.', 'error');
      }
    } catch (error) {
      console.error('Error sending verification email:', error);
      showToast('An error occurred. Please try again later.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (sent) {
    return (
      <div className="mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
        <p>Verification email sent! Please check your inbox.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="mt-4">
      <p className="mb-2 text-sm">Resend verification email to your address:</p>
      <div className="flex flex-col sm:flex-row gap-2">
        <div className="flex-grow">
          <input
            type="email"
            {...register('email')}
            placeholder="Enter your email"
            className="w-full border rounded px-3 py-2 text-sm"
          />
          {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
        </div>
        <button
          type="submit"
          disabled={isSubmitting}
          className="bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700 disabled:opacity-50 flex items-center justify-center"
        >
          {isSubmitting ? <LoadingSpinner size="sm" /> : 'Resend'}
        </button>
      </div>
    </form>
  );
}

function VerifyEmailContent() {
  const { verifyEmail } = useAuth();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { showToast } = useToast();
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');

  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      const verifyUserEmail = async () => {
        try {
          const ok = await verifyEmail(token);
          setStatus(ok ? 'success' : 'error');
          if (ok) {
            showToast('Email verified successfully!', 'success');
            setTimeout(() => router.push('/dashboard'), 2000);
          } else {
            showToast('Email verification failed. Invalid or expired token.', 'error');
          }
        } catch (error) {
          console.error('Email verification error:', error);
          setStatus('error');
          showToast('An error occurred during email verification.', 'error');
        }
      };
      
      verifyUserEmail();
    } else {
      setStatus('error');
      showToast('No verification token provided.', 'error');
    }
  }, [searchParams, router, verifyEmail, showToast]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      {status === 'verifying' && (
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4">Verifying your email address...</p>
        </div>
      )}
      {status === 'success' && (
        <div className="text-center p-6 bg-white shadow-md rounded-lg max-w-sm w-full">
          <div className="text-green-500 text-5xl mb-4">✓</div>
          <h2 className="text-2xl font-bold mb-2">Email Verified!</h2>
          <p className="mb-4">Your email has been successfully verified.</p>
          <p className="text-gray-500">Redirecting to dashboard...</p>
          <div className="mt-4">
            <LoadingSpinner size="sm" />
          </div>
        </div>
      )}
      {status === 'error' && (
        <div className="text-center p-6 bg-white shadow-md rounded-lg max-w-sm w-full">
          <div className="text-red-500 text-5xl mb-4">✗</div>
          <h2 className="text-2xl font-bold mb-2">Verification Failed</h2>
          <p className="text-red-500 mb-4">Invalid or expired verification token.</p>
          <ResendVerificationForm />
          <div className="mt-4">
            <Link href="/login" className="text-indigo-600 hover:underline">
              Return to Login
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense>
      <VerifyEmailContent />
    </Suspense>
  );
}
