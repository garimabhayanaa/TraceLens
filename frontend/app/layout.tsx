import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import ClientWrapper from '@/components/layout/ClientWrapper'

const inter = Inter({ subsets: ['latin'] })

// ✅ Separate viewport export (required for Next.js 14+)
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#3b82f6' },
    { media: '(prefers-color-scheme: dark)', color: '#1e40af' },
  ],
}

// ✅ Updated metadata export (removed viewport and themeColor)
export const metadata: Metadata = {
  title: 'TraceLens - AI Powered Personal Data Exposure Analyser',
  description: 'Advanced AI-powered data exposure analysis with complete privacy protection, legal compliance, and user control. Features 7 integrated security frameworks including abuse prevention, GDPR/CCPA compliance, and ethical boundaries.',
  keywords: [
    'AI analysis',
    'social media',
    'privacy protection',
    'GDPR compliant',
    'ethical AI',
    'data privacy',
    'secure analysis',
    'OSINT mirror',
    'digital footprint',
    'privacy awareness'
  ],
  authors: [{ name: 'TraceLens Team' }],
  creator: 'TraceLens',
  publisher: 'TraceLens',
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
    url: 'https://Tracelens.com',
    title: 'TraceLens',
    description: 'Comprehensive AI analysis with security and complete user control. Your personal OSINT mirror for privacy awareness.',
    siteName: 'TraceLens',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'TraceLens - AI Privacy Analysis Platform',
      },
    ],
  },
  manifest: '/manifest.json',
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  category: 'technology',
  classification: 'AI Analysis Platform',
  referrer: 'origin-when-cross-origin',
  metadataBase: new URL('https://tracelens.com'),
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
        <link rel="manifest" href="/manifest.json" />
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

