// app/layout.tsx - Server Component (NO 'use client')
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import ClientWrapper from '@/components/layout/ClientWrapper'

const inter = Inter({ subsets: ['latin'] })

// ✅ This works because it's a Server Component
export const metadata: Metadata = {
  title: 'AI Social Media Analyzer - Comprehensive Privacy-First Analysis',
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
    'secure analysis'
  ],
  authors: [{ name: 'AI Social Analyzer Team' }],
  creator: 'AI Social Analyzer',
  publisher: 'AI Social Analyzer',
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
    url: 'https://your-domain.com',
    title: 'AI Social Media Analyzer - Privacy-First Analysis',
    description: 'Comprehensive AI analysis with enterprise-grade security and complete user control',
    siteName: 'AI Social Media Analyzer',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'AI Social Media Analyzer - Secure Analysis Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI Social Media Analyzer - Privacy-First Analysis',
    description: 'Comprehensive AI analysis with enterprise-grade security and complete user control',
    images: ['/twitter-image.jpg'],
    creator: '@aisocialanalyzer',
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
  metadataBase: new URL('https://your-domain.com'),
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased`}>
        <ClientWrapper>
          {children}
        </ClientWrapper>
      </body>
    </html>
  )
}