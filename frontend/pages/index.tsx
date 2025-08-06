'use client'
import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import {
  Shield, Brain, Heart, TrendingUp, MapPin, DollarSign,
  Clock, Users, MessageCircle, Hash, Eye, AlertTriangle,
  CheckCircle, XCircle, Info, Download, Trash2, Lock
} from 'lucide-react'

export default function LandingPage() {
  const [email, setEmail] = useState('')

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-16">
          <div className="flex items-center space-x-2">
            <Brain className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">AI Social Analyzer</span>
          </div>
          <div className="space-x-4">
            <Link href="/auth">
              <Button variant="outline">Sign In</Button>
            </Link>
            <Link href="/auth">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>

        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            AI-Powered Social Media Analysis
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Comprehensive, ethical, and privacy-first analysis of social media profiles
            with advanced AI insights, complete user control, and enterprise-grade security.
          </p>

          <div className="flex justify-center mb-8">
            <div className="bg-white p-8 rounded-2xl shadow-lg max-w-md">
              <h3 className="text-lg font-semibold mb-4">Start Your Analysis</h3>
              <div className="space-y-4">
                <Input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <Link href="/auth">
                  <Button className="w-full" size="lg">
                    Begin Secure Analysis
                  </Button>
                </Link>

                <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <CheckCircle className="h-3 w-3 text-green-500" />
                    <span>Email verification</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <CheckCircle className="h-3 w-3 text-green-500" />
                    <span>Bot protection</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <CheckCircle className="h-3 w-3 text-green-500" />
                    <span>3 free analyses/day</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <CheckCircle className="h-3 w-3 text-green-500" />
                    <span>Zero data retention</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 7 Framework Features */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-12">Complete Protection & Analysis</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <Card className="border-2 border-red-200 bg-red-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-red-700">
                  <Shield className="h-5 w-5" />
                  Abuse Prevention
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1 text-red-600">
                  <li>• Email verification system</li>
                  <li>• reCAPTCHA bot protection</li>
                  <li>• Usage limits (3/day, 1/hour)</li>
                  <li>• IP monitoring & blocking</li>
                  <li>• User reporting system</li>
                  <li>• Real-time abuse detection</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-blue-700">
                  <AlertTriangle className="h-5 w-5" />
                  Legal & Ethical
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1 text-blue-600">
                  <li>• AI-specific Terms of Service</li>
                  <li>• Transparent Privacy Policy</li>
                  <li>• GDPR & CCPA compliance</li>
                  <li>• Content moderation</li>
                  <li>• Legal liability protection</li>
                  <li>• Regulatory monitoring</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 border-green-200 bg-green-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-700">
                  <Lock className="h-5 w-5" />
                  Risk Mitigation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1 text-green-600">
                  <li>• Rate limiting with Redis</li>
                  <li>• Input validation & sanitization</li>
                  <li>• XSS & injection prevention</li>
                  <li>• CSRF protection</li>
                  <li>• Performance optimization</li>
                  <li>• Error handling</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 border-purple-200 bg-purple-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-purple-700">
                  <Users className="h-5 w-5" />
                  Authorization
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1 text-purple-600">
                  <li>• Multi-factor verification</li>
                  <li>• Tiered access levels</li>
                  <li>• Identity verification</li>
                  <li>• Third-party consent</li>
                  <li>• Session management</li>
                  <li>• Access logging</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 border-orange-200 bg-orange-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-orange-700">
                  <CheckCircle className="h-5 w-5" />
                  Consent Control
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1 text-orange-600">
                  <li>• Multi-step consent process</li>
                  <li>• Granular permissions</li>
                  <li>• Stage-by-stage opt-out</li>
                  <li>• Immediate data deletion</li>
                  <li>• Consent withdrawal</li>
                  <li>• Transparency reporting</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 border-cyan-200 bg-cyan-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-cyan-700">
                  <Heart className="h-5 w-5" />
                  Ethical Boundaries
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1 text-cyan-600">
                  <li>• Age verification system</li>
                  <li>• Professional oversight</li>
                  <li>• Malicious use prevention</li>
                  <li>• Usage restrictions</li>
                  <li>• Compliance monitoring</li>
                  <li>• Ethics board review</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 border-indigo-200 bg-indigo-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-indigo-700">
                  <Lock className="h-5 w-5" />
                  Privacy Framework
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1 text-indigo-600">
                  <li>• Zero persistent storage</li>
                  <li>• Advanced anonymization</li>
                  <li>• End-to-end encryption</li>
                  <li>• Client-side processing</li>
                  <li>• Secure data deletion</li>
                  <li>• Privacy compliance</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2 border-yellow-200 bg-yellow-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-yellow-700">
                  <Brain className="h-5 w-5" />
                  AI Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1 text-yellow-600">
                  <li>• Comprehensive sentiment analysis</li>
                  <li>• Behavioral pattern recognition</li>
                  <li>• Economic indicator analysis</li>
                  <li>• Mental state assessment</li>
                  <li>• Cross-platform correlation</li>
                  <li>• Interest profiling</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Analysis Features */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-12">Advanced AI Analysis Features</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center p-6">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Heart className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="font-semibold mb-2">Sentiment Analysis</h3>
              <p className="text-sm text-gray-600">Comprehensive emotional analysis with confidence scoring</p>
            </div>

            <div className="text-center p-6">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Hash className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="font-semibold mb-2">Pattern Recognition</h3>
              <p className="text-sm text-gray-600">Hashtag trends, mention patterns, and behavioral analysis</p>
            </div>

            <div className="text-center p-6">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="font-semibold mb-2">Schedule Patterns</h3>
              <p className="text-sm text-gray-600">Temporal analysis and activity rhythm detection</p>
            </div>

            <div className="text-center p-6">
              <div className="bg-red-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <DollarSign className="h-8 w-8 text-red-600" />
              </div>
              <h3 className="font-semibold mb-2">Economic Indicators</h3>
              <p className="text-sm text-gray-600">Brand analysis, spending patterns, and professional insights</p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-white p-12 rounded-2xl shadow-xl">
          <h2 className="text-3xl font-bold mb-4">Ready for Comprehensive Analysis?</h2>
          <p className="text-xl text-gray-600 mb-8">
            Experience the most secure and comprehensive social media analysis available.
          </p>
          <Link href="/auth">
            <Button size="lg" className="px-8 py-3 text-lg">
              Start Your Secure Analysis Now
            </Button>
          </Link>

          <div className="mt-8 flex justify-center space-x-8 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <Shield className="h-4 w-4 text-green-500" />
              <span>Enterprise Security</span>
            </div>
            <div className="flex items-center gap-1">
              <Lock className="h-4 w-4 text-blue-500" />
              <span>Zero Data Retention</span>
            </div>
            <div className="flex items-center gap-1">
              <CheckCircle className="h-4 w-4 text-purple-500" />
              <span>GDPR & CCPA Compliant</span>
            </div>
            <div className="flex items-center gap-1">
              <Brain className="h-4 w-4 text-orange-500" />
              <span>Advanced AI Analysis</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

