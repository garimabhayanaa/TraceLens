// components/ConnectionStatus.tsx
'use client'

import { useAuth } from '../lib/auth-context'
import { useState } from 'react'
import { X, Wifi, WifiOff, RotateCcw } from 'lucide-react'

export default function ConnectionStatus() {
  const { firestoreError, retryConnection } = useAuth()
  const [isDismissed, setIsDismissed] = useState(false)
  const [isRetrying, setIsRetrying] = useState(false)

  if (!firestoreError || isDismissed) return null

  const handleRetry = async () => {
    setIsRetrying(true)
    try {
      await retryConnection()
    } finally {
      setIsRetrying(false)
    }
  }

  return (
    <div className="fixed top-0 left-0 right-0 bg-red-500 text-white shadow-lg z-50 animate-slide-down">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <WifiOff className="h-5 w-5" />
            <span className="font-medium">Connection Issue</span>
            <span className="text-red-100">•</span>
            <span className="text-sm">{firestoreError}</span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleRetry}
              disabled={isRetrying}
              className="flex items-center space-x-1 bg-white/20 hover:bg-white/30 disabled:opacity-50 disabled:cursor-not-allowed px-3 py-1 rounded text-sm font-medium transition-colors"
            >
              <RotateCcw className={`h-4 w-4 ${isRetrying ? 'animate-spin' : ''}`} />
              <span>{isRetrying ? 'Retrying...' : 'Retry'}</span>
            </button>

            <button
              onClick={() => setIsDismissed(true)}
              className="p-1 hover:bg-white/20 rounded transition-colors"
              aria-label="Dismiss notification"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

