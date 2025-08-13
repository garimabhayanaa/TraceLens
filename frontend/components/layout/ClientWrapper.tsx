'use client'
import React from 'react'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '@/lib/auth-context'

interface ClientWrapperProps {
  children: React.ReactNode
}

export default function ClientWrapper({ children }: ClientWrapperProps) {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {children}
      </div>

      {/* Toast notifications */}
      <Toaster
        position="top-right"
        reverseOrder={false}
        gutter={8}
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
            borderRadius: '8px',
            padding: '12px 16px',
            fontSize: '14px',
            maxWidth: '400px',
          },
          success: {
            duration: 3000,
            style: { background: '#10b981' },
          },
          error: {
            duration: 5000,
            style: { background: '#ef4444' },
          },
        }}
      />
    </AuthProvider>
  )
}
