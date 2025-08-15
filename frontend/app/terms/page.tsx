'use client';

import React from 'react';
import { Shield, FileText, Scale, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

const TermsOfServicePage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-blue-600" />
              <span className="text-2xl font-bold text-blue-600">TraceLens</span>
            </Link>
            <Link href="/">
              <Button variant="ghost">← Back to Home</Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-gray-100 rounded-full">
              <Scale className="h-12 w-12 text-gray-600" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Terms of Service</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Please read these terms carefully before using TraceLens. By using our service, you agree to these terms.
          </p>
          <div className="flex items-center justify-center space-x-4 mt-6">
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              📜 Legal Agreement
            </span>
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
              ⚖️ Fair Use Policy
            </span>
          </div>
        </div>

        {/* Quick Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          <Card className="border-green-200 bg-green-50">
            <CardContent className="p-6">
              <h3 className="flex items-center font-semibold text-gray-900 mb-3">
                <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                What You Can Do
              </h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Analyze public profiles</li>
                <li>• Get privacy insights and recommendations</li>
                <li>• Use our AI-powered analysis tools</li>
              </ul>
            </CardContent>
          </Card>
          <Card className="border-red-200 bg-red-50">
            <CardContent className="p-6">
              <h3 className="flex items-center font-semibold text-gray-900 mb-3">
                <XCircle className="h-5 w-5 text-red-600 mr-2" />
                What's Prohibited
              </h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Analyzing private or restricted profiles</li>
                <li>• Using data for harassment or stalking</li>
                <li>• Violating platform terms of service</li>
                <li>• Commercial use without permission</li>
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* Terms Content */}
        <div className="space-y-8">
          {/* Acceptance of Terms */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-blue-600" />
                <span>1. Acceptance of Terms</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-gray max-w-none">
              <p className="mb-4">
                By accessing or using TraceLens ("Service"), you agree to be bound by these Terms of Service ("Terms"). 
                If you disagree with any part of these terms, you may not access the Service.
              </p>
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-blue-800">
                  <strong>Important:</strong> These Terms constitute a legally binding agreement between you and TraceLens. 
                  Please read them carefully and keep a copy for your records.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Description of Service */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-green-600" />
                <span>2. Description of Service</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-gray max-w-none">
              <h4 className="text-lg font-semibold mb-3">What TraceLens Does</h4>
              <ul className="list-disc pl-6 space-y-2 mb-6">
                <li>Analyzes provided public URLs for privacy insights</li>
                <li>Provides AI-powered analysis</li>
                <li>Generates privacy recommendations and risk assessments</li>
              </ul>

              <h4 className="text-lg font-semibold mb-3">Service Limitations</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <h5 className="font-semibold text-yellow-800 mb-2">Free Tier Limits</h5>
                  <ul className="text-sm text-yellow-700 space-y-1">
                    <li>• 10 analyses per day</li>
                    <li>• 24-hour data retention</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* User Responsibilities */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-orange-600" />
                <span>3. User Responsibilities & Prohibited Uses</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-gray max-w-none">
              <h4 className="text-lg font-semibold mb-3">You Must</h4>
              <ul className="list-disc pl-6 space-y-2 mb-6">
                <li>Only analyze publicly available URLs</li>
                <li>Comply with all applicable laws and regulations</li>
                <li>Respect the privacy and rights of others</li>
                <li>Use the Service for legitimate research or personal purposes</li>
                <li>Maintain the confidentiality of your account credentials</li>
              </ul>

              <h4 className="text-lg font-semibold mb-3">You Must NOT</h4>
              <div className="bg-red-50 p-4 rounded-lg mb-6">
                <ul className="list-disc pl-6 space-y-2 text-red-800">
                  <li>Use the Service for stalking, harassment, or any harmful activities</li>
                  <li>Attempt to access private or restricted social media content</li>
                  <li>Share, sell, or redistribute analysis results without consent</li>
                  <li>Use automated tools to access the Service beyond normal usage</li>
                  <li>Reverse engineer or attempt to compromise our security</li>
                  <li>Violate any third-party platform's terms of service</li>
                </ul>
              </div>

              <h4 className="text-lg font-semibold mb-3">Account Security</h4>
              <p className="mb-4">
                You are responsible for maintaining the security of your account and password. TraceLens cannot and will not 
                be liable for any loss or damage from your failure to comply with this security obligation.
              </p>
            </CardContent>
          </Card>

          {/* Privacy and Data */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-indigo-600" />
                <span>4. Privacy & Data Handling</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-gray max-w-none">
              <h4 className="text-lg font-semibold mb-3">Data Collection</h4>
              <p className="mb-4">
                We collect and process data as outlined in our <Link href="/privacy" className="text-blue-600 underline">Privacy Policy</Link>. 
                By using TraceLens, you consent to such processing and you warrant that all data provided by you is accurate.
              </p>

              <h4 className="text-lg font-semibold mb-3">Automatic Data Deletion</h4>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-green-800">
                  <strong>Privacy Protection:</strong> All analysis results and temporary data are automatically deleted 
                  after 24 hours. We do not retain your analysis data beyond this period.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Intellectual Property */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-purple-600" />
                <span>5. Intellectual Property Rights</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-gray max-w-none">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-lg font-semibold mb-3">Our Rights</h4>
                  <ul className="list-disc pl-6 space-y-1 text-sm">
                    <li>TraceLens service and technology</li>
                    <li>AI algorithms and analysis methods</li>
                    <li>User interface and design</li>
                    <li>Documentation and content</li>
                    <li>Trademarks and branding</li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-3">Your Rights</h4>
                  <ul className="list-disc pl-6 space-y-1 text-sm">
                    <li>Your original input data</li>
                    <li>Analysis results for personal use</li>
                    <li>Right to export your data</li>
                    <li>Right to delete your data</li>
                    <li>Account information ownership</li>
                  </ul>
                </div>
              </div>

              <div className="mt-6 p-4 bg-purple-50 rounded-lg">
                <h4 className="text-lg font-semibold mb-2 text-purple-800">License Grant</h4>
                <p className="text-purple-700 text-sm">
                  We grant you a limited, non-exclusive, non-transferable license to use TraceLens for your personal or 
                  internal business purposes, subject to these Terms.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Disclaimer and Limitation */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <span>6. Disclaimers & Limitations</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-gray max-w-none">
              <h4 className="text-lg font-semibold mb-3">Service Disclaimer</h4>
              <div className="bg-yellow-50 p-4 rounded-lg mb-6">
                <p className="text-yellow-800 text-sm">
                  <strong>IMPORTANT:</strong> TraceLens is provided "AS IS" without warranties of any kind. 
                  Analysis results are for informational purposes only and should not be considered as professional advice.
                </p>
              </div>

              <h4 className="text-lg font-semibold mb-3">Limitation of Liability</h4>
              <p className="mb-4 text-sm">
                IN NO EVENT SHALL TRACELENS BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, 
                OR PUNITIVE DAMAGES, INCLUDING WITHOUT LIMITATION, LOSS OF PROFITS, DATA, USE, GOODWILL, 
                OR OTHER INTANGIBLE LOSSES.
              </p>

              <h4 className="text-lg font-semibold mb-3">Accuracy Disclaimer</h4>
              <p className="text-sm">
                While we strive for accuracy, we cannot guarantee that all analysis results are completely accurate 
                or up-to-date. Users should verify important information independently.
              </p>
            </CardContent>
          </Card>

          {/* Contact and Changes */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-blue-600" />
                <span>7. Modifications</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
                <div>
                  <h4 className="text-lg font-semibold mb-3">Changes to Terms</h4>
                  <p className="text-sm text-gray-600">
                    We may update these Terms from time to time. We will notify you of any changes by posting 
                    the new Terms on this page and updating the "Effective Date."
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default TermsOfServicePage;
