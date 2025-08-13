// components/layout/ClientWrapper.tsx
'use client'

import { AuthProvider } from '../../lib/auth-context'
import { Toaster } from 'react-hot-toast'
import ConnectionStatus from '@/components/ConnectionStatus'
import { useEffect, useState } from 'react'

export default function ClientWrapper({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <AuthProvider>
      {/* Connection Status Banner - Shows at top when there are issues */}
      <ConnectionStatus />

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />

      {/* Main Application Content */}
      <main className="relative min-h-screen">
        {children}
      </main>

      {/* Global Loading Overlay */}
      <div id="loading-overlay" className="hidden fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
        <div className="bg-white rounded-lg p-6 flex items-center space-x-3">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span className="text-gray-700">Processing...</span>
        </div>
      </div>
    </AuthProvider>
  )
}

