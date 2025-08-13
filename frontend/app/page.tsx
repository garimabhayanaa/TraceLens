'use client'
import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { 
  Shield, Brain, Heart, TrendingUp, MapPin, DollarSign, 
  Clock, Users, MessageCircle, Hash, Eye, AlertTriangle,
  CheckCircle, XCircle, Info, Download, Trash2, Lock,
  Star, ArrowRight, Globe, Zap, Database, UserCheck,
  Award, BarChart3, Smartphone, Monitor, Mail, Phone,
  Facebook, Twitter, Linkedin, Github, Home, FileText,
  HelpCircle, Settings, Building, Calendar
} from 'lucide-react'

export default function LandingPage() {
  const [email, setEmail] = useState('')
  const [isEmailValid, setIsEmailValid] = useState(false)

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const emailValue = e.target.value
    setEmail(emailValue)
    // Simple email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    setIsEmailValid(emailRegex.test(emailValue))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header/Navigation */}
      <header className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-16">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <span className="text-2xl font-bold text-gray-900">TraceLens</span>
              <div className="text-xs text-blue-600 font-medium">Enterprise Security</div>
            </div>
          </div>
          <div className="hidden md:flex items-center space-x-6">
            <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors">Features</a>
            <a href="#security" className="text-gray-600 hover:text-blue-600 transition-colors">Security</a>
            <a href="#compliance" className="text-gray-600 hover:text-blue-600 transition-colors">Compliance</a>
            <Link href="/login">
              <Button variant="outline">Log In</Button>
            </Link>
            <Link href="/login">
              <Button>Get Started</Button>
            </Link>
          </div>
          {/* Mobile menu button */}
          <div className="md:hidden">
            <Link href="/login">
              <Button size="sm">Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4">
        {/* Hero Section */}
        <section className="text-center mb-20">
          <div className="max-w-4xl mx-auto">
            <div className="mb-6">
              <span className="inline-flex items-center px-4 py-2 rounded-full bg-blue-100 text-blue-800 text-sm font-medium mb-4">
                <Shield className="h-4 w-4 mr-2" />
                7 Integrated Protection Frameworks
              </span>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              AI-Powered Social Media Analysis
              <span className="block text-blue-600">with Complete Privacy Protection</span>
            </h1>
            
            <p className="text-xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
              Comprehensive, ethical, and privacy-first analysis of social media profiles
              with advanced AI insights, enterprise-grade security, and complete user control.
            </p>
            
            {/* Email signup form */}
            <div className="max-w-md mx-auto mb-8">
              <Card className="p-6 shadow-lg border-0 bg-white/80 backdrop-blur-sm">
                <h3 className="text-lg font-semibold mb-4 text-gray-900">Start Your Secure Analysis</h3>
                <div className="space-y-4">
                  <div className="flex space-x-2">
                    <Input
                      type="email"
                      placeholder="Enter your email address"
                      value={email}
                      onChange={handleEmailChange}
                      className={`flex-1 ${isEmailValid ? 'border-green-500' : email ? 'border-red-300' : ''}`}
                    />
                    <Link href="/login">
                      <Button 
                        size="lg" 
                        className="whitespace-nowrap"
                        disabled={!isEmailValid}
                      >
                        Begin Analysis
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Email verification required</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Bot protection enabled</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>3 free analyses per day</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Zero data retention</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-center gap-4 text-xs text-gray-500 pt-2">
                    <span className="flex items-center gap-1">
                      <Shield className="h-3 w-3" />
                      GDPR Compliant
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Lock className="h-3 w-3" />
                      AES-256 Encryption
                    </span>
                  </div>
                </div>
              </Card>
            </div>

            {/* Trust indicators */}
            <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-600 mb-12">
              <div className="flex items-center gap-2">
                <div className="flex -space-x-1">
                  <div className="w-6 h-6 bg-blue-500 rounded-full border-2 border-white"></div>
                  <div className="w-6 h-6 bg-green-500 rounded-full border-2 border-white"></div>
                  <div className="w-6 h-6 bg-purple-500 rounded-full border-2 border-white"></div>
                </div>
                <span>500+ verified users</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="flex">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star key={star} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <span>4.9/5 rating</span>
              </div>
              <div className="flex items-center gap-1">
                <Award className="h-4 w-4 text-blue-500" />
                <span>Security certified</span>
              </div>
            </div>
          </div>
        </section>

        {/* 7 Framework Features Section */}
        <section id="features" className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Complete Protection & Analysis
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our comprehensive security system includes 7 integrated protection frameworks,
              ensuring your data is safe while providing deep insights.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-12">
            {/* Abuse Prevention Framework */}
            <Card className="framework-card border-2 border-red-200 bg-red-50 hover:border-red-300 transition-all duration-300">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-red-700">
                  <Shield className="h-5 w-5" />
                  Abuse Prevention
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2 text-red-600">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Email verification with secure 6-digit codes
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    reCAPTCHA v3 bot protection
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Usage limits (3/day, 1/hour max)
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Real-time IP monitoring & blocking
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Community abuse reporting system
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Legal & Ethical Framework */}
            <Card className="framework-card border-2 border-blue-200 bg-blue-50 hover:border-blue-300 transition-all duration-300">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-blue-700">
                  <AlertTriangle className="h-5 w-5" />
                  Legal & Ethical
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2 text-blue-600">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    AI-specific Terms of Service
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Transparent Privacy Policy
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    GDPR & CCPA full compliance
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    AI-powered content moderation
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Legal liability protection
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Risk Mitigation Framework */}
            <Card className="framework-card border-2 border-green-200 bg-green-50 hover:border-green-300 transition-all duration-300">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-700">
                  <Lock className="h-5 w-5" />
                  Risk Mitigation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2 text-green-600">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Advanced rate limiting with Redis
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Input validation & sanitization
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    XSS & SQL injection prevention
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    CSRF protection enabled
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Performance optimization
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Authorization Framework */}
            <Card className="framework-card border-2 border-purple-200 bg-purple-50 hover:border-purple-300 transition-all duration-300">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-purple-700">
                  <UserCheck className="h-5 w-5" />
                  Authorization
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2 text-purple-600">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Multi-factor identity verification
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Tiered access level control
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Self-analysis verification
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Third-party consent management
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Comprehensive audit logging
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Consent Control Framework */}
            <Card className="framework-card border-2 border-orange-200 bg-orange-50 hover:border-orange-300 transition-all duration-300">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-orange-700">
                  <Users className="h-5 w-5" />
                  Consent Control
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2 text-orange-600">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Multi-step consent process
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Granular permission controls
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Stage-by-stage opt-out
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Immediate data deletion
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Transparency reporting
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Ethical Boundaries Framework */}
            <Card className="framework-card border-2 border-cyan-200 bg-cyan-50 hover:border-cyan-300 transition-all duration-300">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-cyan-700">
                  <Heart className="h-5 w-5" />
                  Ethical Boundaries
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2 text-cyan-600">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Age verification system
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Professional ethics oversight
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Malicious use prevention
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Usage restriction enforcement
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Real-time compliance monitoring
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Privacy Framework */}
            <Card className="framework-card border-2 border-indigo-200 bg-indigo-50 hover:border-indigo-300 transition-all duration-300">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-indigo-700">
                  <Database className="h-5 w-5" />
                  Privacy Protection
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2 text-indigo-600">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Zero persistent data storage
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Advanced data anonymization
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    End-to-end AES-256 encryption
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Client-side processing options
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Secure cryptographic deletion
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* AI Analysis Framework */}
            <Card className="framework-card border-2 border-yellow-200 bg-yellow-50 hover:border-yellow-300 transition-all duration-300">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-yellow-700">
                  <Brain className="h-5 w-5" />
                  AI Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2 text-yellow-600">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Advanced sentiment analysis
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Behavioral pattern recognition
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Economic indicator analysis
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Mental wellbeing assessment
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    Cross-platform correlation
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Advanced Analysis Features */}
        <section id="analysis" className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Advanced AI Analysis Capabilities
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our sophisticated AI engine provides deep insights across multiple dimensions
              while maintaining complete privacy and security.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center group">
              <div className="bg-gradient-to-br from-pink-100 to-red-100 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <Heart className="h-10 w-10 text-red-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Sentiment Analysis</h3>
              <p className="text-sm text-gray-600">
                Comprehensive emotional analysis with confidence scoring and emotional indicator detection
              </p>
            </div>
            
            <div className="text-center group">
              <div className="bg-gradient-to-br from-green-100 to-emerald-100 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <Hash className="h-10 w-10 text-green-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Pattern Recognition</h3>
              <p className="text-sm text-gray-600">
                Hashtag trends, mention patterns, and behavioral analysis with trending score calculation
              </p>
            </div>
            
            <div className="text-center group">
              <div className="bg-gradient-to-br from-purple-100 to-violet-100 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <Clock className="h-10 w-10 text-purple-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Schedule Patterns</h3>
              <p className="text-sm text-gray-600">
                Temporal analysis, activity rhythm detection, and work-life balance insights
              </p>
            </div>
            
            <div className="text-center group">
              <div className="bg-gradient-to-br from-blue-100 to-cyan-100 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <DollarSign className="h-10 w-10 text-blue-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Economic Indicators</h3>
              <p className="text-sm text-gray-600">
                Brand analysis, spending patterns, professional insights, and economic profiling
              </p>
            </div>
          </div>

          <div className="mt-16 bg-gradient-to-br from-gray-900 to-blue-900 rounded-3xl p-8 md:p-12 text-white">
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-10">
                <h3 className="text-2xl md:text-3xl font-bold mb-4">
                  Real-time Processing with Complete Transparency
                </h3>
                <p className="text-blue-100 text-lg">
                  Watch your analysis unfold in real-time with complete visibility into every step
                </p>
              </div>
              
              <div className="grid md:grid-cols-3 gap-8">
                <div className="flex items-start space-x-4">
                  <div className="bg-blue-500 rounded-lg p-3">
                    <Zap className="h-6 w-6" />
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">Lightning Fast</h4>
                    <p className="text-blue-100 text-sm">
                      Analysis completed in under 60 seconds with real-time progress tracking
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="bg-green-500 rounded-lg p-3">
                    <Eye className="h-6 w-6" />
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">Full Transparency</h4>
                    <p className="text-blue-100 text-sm">
                      See exactly what data is processed and how insights are generated
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="bg-purple-500 rounded-lg p-3">
                    <BarChart3 className="h-6 w-6" />
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">Rich Insights</h4>
                    <p className="text-blue-100 text-sm">
                      Comprehensive dashboard with interactive charts and detailed breakdowns
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Security & Compliance Section */}
        <section id="security" className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Enterprise-Grade Security & Compliance
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Built with security-first principles and complete regulatory compliance
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-center mb-16">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Security Standards</h3>
              <div className="space-y-4">
                <div className="flex items-start space-x-4">
                  <div className="bg-green-100 rounded-lg p-2">
                    <Shield className="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold">AES-256 Encryption</h4>
                    <p className="text-gray-600 text-sm">End-to-end encryption for all data transmission and storage</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="bg-blue-100 rounded-lg p-2">
                    <Lock className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold">Zero Data Retention</h4>
                    <p className="text-gray-600 text-sm">All data automatically deleted within 24 hours maximum</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="bg-purple-100 rounded-lg p-2">
                    <Database className="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold">Secure Processing</h4>
                    <p className="text-gray-600 text-sm">All analysis performed on anonymized data with secure deletion</p>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Compliance Certifications</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded-xl border-2 border-green-200 text-center">
                  <div className="text-2xl mb-2">🇪🇺</div>
                  <div className="font-semibold text-green-700">GDPR</div>
                  <div className="text-xs text-gray-600">EU Compliant</div>
                </div>
                <div className="bg-white p-4 rounded-xl border-2 border-blue-200 text-center">
                  <div className="text-2xl mb-2">🇺🇸</div>
                  <div className="font-semibold text-blue-700">CCPA</div>
                  <div className="text-xs text-gray-600">California Compliant</div>
                </div>
                <div className="bg-white p-4 rounded-xl border-2 border-purple-200 text-center">
                  <div className="text-2xl mb-2">🛡️</div>
                  <div className="font-semibold text-purple-700">SOC 2</div>
                  <div className="text-xs text-gray-600">Type II Certified</div>
                </div>
                <div className="bg-white p-4 rounded-xl border-2 border-indigo-200 text-center">
                  <div className="text-2xl mb-2">⚖️</div>
                  <div className="font-semibold text-indigo-700">ISO 27001</div>
                  <div className="text-xs text-gray-600">Security Standard</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Responsive Design Showcase */}
        <section className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Seamless Experience Across All Devices
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Optimized for desktop, tablet, and mobile with consistent functionality
            </p>
          </div>

          <div className="flex justify-center items-end space-x-8">
            <div className="text-center">
              <div className="bg-gray-800 rounded-lg p-2 mb-3">
                <Monitor className="h-8 w-8 text-white mx-auto" />
              </div>
              <div className="text-sm font-medium">Desktop</div>
              <div className="text-xs text-gray-600">Full Features</div>
            </div>
            <div className="text-center">
              <div className="bg-gray-800 rounded-lg p-2 mb-3">
                <div className="w-6 h-8 bg-white rounded-sm mx-auto"></div>
              </div>
              <div className="text-sm font-medium">Tablet</div>
              <div className="text-xs text-gray-600">Touch Optimized</div>
            </div>
            <div className="text-center">
              <div className="bg-gray-800 rounded-lg p-2 mb-3">
                <Smartphone className="h-8 w-8 text-white mx-auto" />
              </div>
              <div className="text-sm font-medium">Mobile</div>
              <div className="text-xs text-gray-600">On-the-Go</div>
            </div>
          </div>
        </section>

        {/* Final CTA Section */}
        <section className="mb-20">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl p-8 md:p-16 text-white text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready for the Most Secure Analysis Available?
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Join hundreds of users who trust our platform for comprehensive,
              privacy-protected social media insights.
            </p>
            
            <div className="space-y-4 md:space-y-0 md:space-x-4 md:flex md:justify-center">
              <Link href="/login">
                <Button size="lg" variant="secondary" className="w-full md:w-auto text-lg px-8 py-4">
                  Start Free Analysis
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link href="/demo">
                <Button size="lg" variant="outline" className="w-full md:w-auto text-lg px-8 py-4 border-white text-white hover:bg-white hover:text-blue-600">
                  View Demo
                  <Globe className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>

            <div className="mt-8 flex flex-wrap justify-center gap-8 text-sm text-blue-200">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                <span>No Credit Card Required</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                <span>3 Free Analyses Daily</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                <span>Complete Privacy Protection</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                <span>Enterprise Security</span>
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* Comprehensive Footer */}
      <footer className="bg-white border-t border-gray-200">
        <div className="container mx-auto px-4 py-12">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Company Info */}
            <div className="col-span-1 lg:col-span-1">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
                  <Brain className="h-6 w-6 text-white" />
                </div>
                <div>
                  <span className="text-2xl font-bold text-gray-900">TraceLens</span>
                  <div className="text-xs text-blue-600 font-medium">Enterprise Security</div>
                </div>
              </div>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Enterprise-grade AI analysis with complete privacy protection. 
                Built with 7 integrated security frameworks for maximum user safety and legal compliance.
              </p>
              
              {/* Social Links */}
              <div className="flex space-x-4">
                <a href="#" className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-blue-100 hover:text-blue-600 transition-colors">
                  <Facebook className="h-5 w-5" />
                </a>
                <a href="#" className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-blue-100 hover:text-blue-600 transition-colors">
                  <Twitter className="h-5 w-5" />
                </a>
                <a href="#" className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-blue-100 hover:text-blue-600 transition-colors">
                  <Linkedin className="h-5 w-5" />
                </a>
                <a href="#" className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-blue-100 hover:text-blue-600 transition-colors">
                  <Github className="h-5 w-5" />
                </a>
              </div>
            </div>

            {/* Product */}
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Product</h3>
              <ul className="space-y-3 text-sm text-gray-600">
                <li>
                  <Link href="/login" className="hover:text-blue-600 transition-colors flex items-center">
                    <ArrowRight className="h-3 w-3 mr-2" />
                    Get Started
                  </Link>
                </li>
                <li>
                  <a href="#features" className="hover:text-blue-600 transition-colors">Features</a>
                </li>
                <li>
                  <a href="#" className="hover:text-blue-600 transition-colors">API Documentation</a>
                </li>
                <li>
                  <a href="#" className="hover:text-blue-600 transition-colors">Integrations</a>
                </li>
                <li>
                  <a href="#" className="hover:text-blue-600 transition-colors">Pricing</a>
                </li>
                <li>
                  <a href="#" className="hover:text-blue-600 transition-colors">Enterprise</a>
                </li>
              </ul>
            </div>

            {/* Legal & Security */}
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Legal & Security</h3>
              <ul className="space-y-3 text-sm text-gray-600">
                <li>
                  <a href="/privacy-policy" className="hover:text-blue-600 transition-colors">Privacy Policy</a>
                </li>
                <li>
                  <a href="/terms-of-service" className="hover:text-blue-600 transition-colors">Terms of Service</a>
                </li>
                <li>
                  <a href="/security" className="hover:text-blue-600 transition-colors">Security Overview</a>
                </li>
                <li>
                  <a href="/compliance" className="hover:text-blue-600 transition-colors">Compliance Center</a>
                </li>
                <li>
                  <a href="/data-protection" className="hover:text-blue-600 transition-colors">Data Protection</a>
                </li>
                <li>
                  <a href="/report-abuse" className="hover:text-blue-600 transition-colors">Report Abuse</a>
                </li>
              </ul>
            </div>

            {/* Support & Contact */}
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Support & Contact</h3>
              <ul className="space-y-3 text-sm text-gray-600">
                <li>
                  <a href="/help" className="hover:text-blue-600 transition-colors">Help Center</a>
                </li>
                <li>
                  <a href="/contact" className="hover:text-blue-600 transition-colors">Contact Support</a>
                </li>
                <li>
                  <a href="/status" className="hover:text-blue-600 transition-colors">System Status</a>
                </li>
                <li>
                  <a href="/blog" className="hover:text-blue-600 transition-colors">Blog</a>
                </li>
                <li>
                  <a href="/changelog" className="hover:text-blue-600 transition-colors">Changelog</a>
                </li>
              </ul>

              {/* Contact Info */}
              <div className="mt-6 space-y-2">
                <div className="flex items-center text-sm text-gray-600">
                  <Mail className="h-4 w-4 mr-2" />
                  <a href="mailto:support@tracelens.ai" className="hover:text-blue-600">
                    support@tracelens.ai
                  </a>
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <Phone className="h-4 w-4 mr-2" />
                  <a href="tel:+1-555-SECURE" className="hover:text-blue-600">
                    +1-555-SECURE
                  </a>
                </div>
              </div>
            </div>
          </div>

          {/* Security Badges */}
          <div className="border-t border-gray-200 mt-12 pt-8">
            <div className="text-center mb-6">
              <h4 className="font-semibold text-gray-900 mb-4">Security & Compliance Certifications</h4>
              <div className="flex flex-wrap justify-center gap-6">
                <div className="flex items-center space-x-2 text-sm text-gray-600 bg-gray-50 px-4 py-2 rounded-lg">
                  <Shield className="h-4 w-4 text-green-600" />
                  <span>SOC 2 Type II</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600 bg-gray-50 px-4 py-2 rounded-lg">
                  <Lock className="h-4 w-4 text-blue-600" />
                  <span>ISO 27001</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600 bg-gray-50 px-4 py-2 rounded-lg">
                  <CheckCircle className="h-4 w-4 text-purple-600" />
                  <span>GDPR Compliant</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600 bg-gray-50 px-4 py-2 rounded-lg">
                  <Award className="h-4 w-4 text-orange-600" />
                  <span>CCPA Compliant</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600 bg-gray-50 px-4 py-2 rounded-lg">
                  <Zap className="h-4 w-4 text-yellow-600" />
                  <span>NIST Framework</span>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-gray-200 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="text-sm text-gray-600 mb-4 md:mb-0">
                © 2024 TraceLens. All rights reserved. | 
                <span className="ml-1">Built with privacy-first principles</span>
              </div>
              
              <div className="flex items-center space-x-6 text-xs text-gray-500">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>System Status: Operational</span>
                </div>
                <span>|</span>
                <span>Version 5.2</span>
                <span>|</span>
                <span>Last Updated: {new Date().toLocaleDateString()}</span>
              </div>
            </div>

            {/* Made with privacy */}
            <div className="text-center mt-6 pt-6 border-t border-gray-100">
              <p className="text-xs text-gray-500 flex items-center justify-center">
                Made with <Heart className="h-3 w-3 mx-1 text-red-500" /> for privacy and security
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
