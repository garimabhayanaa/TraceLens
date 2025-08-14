'use client';

import React from 'react';
import { Shield, Eye, Lock, Database, UserCheck, FileText } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

const PrivacyPolicyPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
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
            <div className="p-3 bg-blue-100 rounded-full">
              <Eye className="h-12 w-12 text-blue-600" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Privacy Policy</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Your privacy is our top priority. Learn how we collect, use, and protect your personal information.
          </p>
          <div className="flex items-center justify-center space-x-4 mt-6">
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
              🔐 GDPR Compliant
            </span>
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              🛡️ Privacy First
            </span>
            <span className="text-sm text-gray-500">Last Updated: August 14, 2025</span>
          </div>
        </div>

        {/* Quick Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Card className="border-blue-200 bg-blue-50">
            <CardContent className="p-6 text-center">
              <Lock className="h-8 w-8 text-blue-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">Data Encryption</h3>
              <p className="text-sm text-gray-600">All data is encrypted in transit and at rest</p>
            </CardContent>
          </Card>
          <Card className="border-green-200 bg-green-50">
            <CardContent className="p-6 text-center">
              <Database className="h-8 w-8 text-green-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">24-Hour Deletion</h3>
              <p className="text-sm text-gray-600">Analysis data automatically deleted after 24 hours</p>
            </CardContent>
          </Card>
          <Card className="border-purple-200 bg-purple-50">
            <CardContent className="p-6 text-center">
              <UserCheck className="h-8 w-8 text-purple-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">User Control</h3>
              <p className="text-sm text-gray-600">You control what data we analyze and when</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Policy Content */}
        <div className="space-y-8">
          {/* Information We Collect */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-blue-600" />
                <span>1. Information We Collect</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-gray max-w-none">
              <h4 className="text-lg font-semibold mb-3">Account Information</h4>
              <ul className="list-disc pl-6 space-y-2">
                <li>Email address (for authentication and account management)</li>
                <li>Display name (optional, for personalization)</li>
                <li>Authentication tokens (managed by Firebase)</li>
                <li>Account creation and last login timestamps</li>
              </ul>

              <h4 className="text-lg font-semibold mb-3 mt-6">Analysis Data</h4>
              <ul className="list-disc pl-6 space-y-2">
                <li>Social media URLs you choose to analyze</li>
                <li>Analysis type preferences (comprehensive, privacy-only, etc.)</li>
                <li>Generated analysis results (automatically deleted after 24 hours)</li>
                <li>Usage statistics (number of analyses performed)</li>
              </ul>

              <h4 className="text-lg font-semibold mb-3 mt-6">Technical Information</h4>
              <ul className="list-disc pl-6 space-y-2">
                <li>IP address (for security and fraud prevention)</li>
                <li>Browser type and version</li>
                <li>Device information (for optimization purposes)</li>
                <li>Error logs and performance metrics</li>
              </ul>
            </CardContent>
          </Card>

          {/* How We Use Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Database className="h-5 w-5 text-green-600" />
                <span>2. How We Use Your Information</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-gray max-w-none">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-lg font-semibold mb-3">Service Delivery</h4>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Perform social media analysis</li>
                    <li>Generate privacy insights</li>
                    <li>Provide personalized recommendations</li>
                    <li>Maintain your analysis history</li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-3">Account Management</h4>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>User authentication and authorization</li>
                    <li>Account security monitoring</li>
                    <li>Usage limit enforcement</li>
                    <li>Customer support</li>
                  </ul>
                </div>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg mt-6">
                <p className="text-blue-800">
                  <strong>Important:</strong> We never sell your personal data. We never share your analysis results with third parties. 
                  All analysis is performed securely within our system and results are automatically deleted after 24 hours.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Data Protection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Lock className="h-5 w-5 text-purple-600" />
                <span>3. Data Protection & Security</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-gray max-w-none">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-lg font-semibold mb-3">Encryption</h4>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>TLS 1.3 encryption for all data transmission</li>
                    <li>AES-256 encryption for data at rest</li>
                    <li>End-to-end encrypted analysis pipeline</li>
                    <li>Secure Firebase authentication</li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-3">Access Control</h4>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Multi-factor authentication for admin access</li>
                    <li>Role-based access control (RBAC)</li>
                    <li>Regular security audits and penetration testing</li>
                    <li>Automated threat detection and response</li>
                  </ul>
                </div>
              </div>

              <h4 className="text-lg font-semibold mb-3 mt-6">Data Retention</h4>
              <div className="bg-red-50 p-4 rounded-lg">
                <p className="text-red-800">
                  <strong>Automatic Deletion Policy:</strong> All analysis results and temporary data are automatically 
                  deleted after 24 hours. Account information is retained only as long as your account is active.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Your Rights */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <UserCheck className="h-5 w-5 text-indigo-600" />
                <span>4. Your Rights (GDPR Compliance)</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-gray max-w-none">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-lg font-semibold mb-3">Data Access Rights</h4>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Right to access your personal data</li>
                    <li>Right to data portability</li>
                    <li>Right to rectification (correct inaccurate data)</li>
                    <li>Right to erasure ("right to be forgotten")</li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-3">Control Rights</h4>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Right to restrict processing</li>
                    <li>Right to object to processing</li>
                    <li>Right to withdraw consent</li>
                    <li>Right to lodge a complaint with supervisory authority</li>
                  </ul>
                </div>
              </div>

              <div className="mt-6 p-4 bg-green-50 rounded-lg">
                <h4 className="text-lg font-semibold mb-2 text-green-800">Exercise Your Rights</h4>
                <p className="text-green-700">
                  To exercise any of these rights, contact us at <a href="mailto:privacy@tracelens.ai" className="underline">privacy@tracelens.ai</a>. 
                  We will respond within 30 days as required by GDPR.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Contact Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-blue-600" />
                <span>5. Contact Us</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <h4 className="font-semibold mb-2">Privacy Officer</h4>
                  <p className="text-sm text-gray-600">privacy@tracelens.ai</p>
                </div>
                <div className="text-center">
                  <h4 className="font-semibold mb-2">Legal Team</h4>
                  <p className="text-sm text-gray-600">legal@tracelens.ai</p>
                </div>
                <div className="text-center">
                  <h4 className="font-semibold mb-2">General Support</h4>
                  <p className="text-sm text-gray-600">support@tracelens.ai</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicyPage;
