import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import React from 'react'
import { AuthProvider } from '@/hooks/useAuth'
import { ToastProvider } from '@/components/ToastProvider'
import NavBar from '@/components/NavBar'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Voice Agent Platform',
  description: 'Multi-tenant AI Voice Agent Platform for businesses',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <ToastProvider>
            <div className="min-h-screen bg-background font-sans antialiased">
              <NavBar />
              {children}
            </div>
          </ToastProvider>
        </AuthProvider>
      </body>
    </html>
  )}