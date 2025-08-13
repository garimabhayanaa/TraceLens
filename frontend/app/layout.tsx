// app/layout.tsx - Server Component (NO 'use client')
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import ClientWrapper from '@/components/layout/ClientWrapper'

const inter = Inter({ subsets: ['latin'] })

// ✅ This works because it's a Server Component
export const metadata: Metadata = {
  title: 'LeakPeek - AI Social Media Privacy Analyzer',
  description: 'Advanced AI-powered social media analysis with complete privacy protection, legal compliance, and user control. Features 7 integrated security frameworks including abuse prevention, GDPR/CCPA compliance, and ethical boundaries.',
  keywords: [
    'AI analysis',
    'social media',
    'privacy protection',
    'GDPR compliant',
    'sentiment analysis',
    'behavioral analysis',
    'abuse prevention',
    'ethical AI',
    'data privacy',
    'secure analysis',
    'OSINT mirror',
    'digital footprint',
    'privacy awareness'
  ],
  authors: [{ name: 'LeakPeek Team' }],
  creator: 'LeakPeek',
  publisher: 'LeakPeek',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://leakpeek.com',
    title: 'LeakPeek - See What AI Can Infer About You',
    description: 'Comprehensive AI analysis with enterprise-grade security and complete user control. Your personal OSINT mirror for privacy awareness.',
    siteName: 'LeakPeek',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'LeakPeek - AI Privacy Analysis Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'LeakPeek - See What AI Can Infer About You',
    description: 'Your personal OSINT mirror. Discover what patterns AI can extract from your public data.',
    images: ['/twitter-image.jpg'],
    creator: '@leakpeek',
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#3b82f6' },
    { media: '(prefers-color-scheme: dark)', color: '#1e40af' },
  ],
  manifest: '/manifest.json',
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  category: 'technology',
  classification: 'AI Analysis Platform',
  referrer: 'origin-when-cross-origin',
  metadataBase: new URL('https://leakpeek.com'),
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.className}>
      <head>
        <meta name="format-detection" content="telephone=no" />
        <meta name="msapplication-TileColor" content="#3b82f6" />
        <meta name="theme-color" content="#3b82f6" />
      </head>
      <body className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900">
        {/* Client-side components wrapper */}
        <ClientWrapper>
          {children}
        </ClientWrapper>

        {/* Background elements */}
        <div className="fixed inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-1/2 -right-1/2 w-full h-full bg-gradient-to-bl from-blue-100/20 to-transparent rounded-full blur-3xl" />
          <div className="absolute -bottom-1/2 -left-1/2 w-full h-full bg-gradient-to-tr from-purple-100/20 to-transparent rounded-full blur-3xl" />
        </div>
      </body>
    </html>
  )
}
