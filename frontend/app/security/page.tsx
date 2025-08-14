'use client';

import React from 'react';
import { Shield, Lock, Key, Server, Eye, AlertTriangle, CheckCircle2, Globe } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

const SecurityPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50">
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
      <div className="container mx-auto px-4 py-12 max-w-5xl">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-indigo-100 rounded-full">
              <Lock className="h-12 w-12 text-indigo-600" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Security & Data Protection</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Your security is our top priority. Learn about the comprehensive measures we take to protect your data and privacy.
          </p>
          <div className="flex items-center justify-center space-x-4 mt-6">
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
              🔐 Enterprise-Grade Security
            </span>
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              🛡️ SOC 2 Compliant
            </span>
            <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
              🌐 Global Infrastructure
            </span>
          </div>
        </div>

        {/* Security Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
          <Card className="text-center">
            <CardContent className="p-6">
              <div className="text-3xl font-bold text-green-600 mb-2">99.9%</div>
              <div className="text-sm text-gray-600">Uptime SLA</div>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardContent className="p-6">
              <div className="text-3xl font-bold text-blue-600 mb-2">256-bit</div>
              <div className="text-sm text-gray-600">AES Encryption</div>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardContent className="p-6">
              <div className="text-3xl font-bold text-purple-600 mb-2">24hrs</div>
              <div className="text-sm text-gray-600">Data Retention</div>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardContent className="p-6">
              <div className="text-3xl font-bold text-indigo-600 mb-2">24/7</div>
              <div className="text-sm text-gray-600">Monitoring</div>
            </CardContent>
          </Card>
        </div>

        {/* Security Sections */}
        <div className="space-y-8">
          {/* Data Encryption */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Key className="h-5 w-5 text-blue-600" />
                <span>Data Encryption & Protection</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg font-semibold mb-4">Encryption in Transit</h4>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">TLS 1.3 for all communications</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Perfect Forward Secrecy (PFS)</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">HSTS (HTTP Strict Transport Security)</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Certificate pinning for mobile apps</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-lg font-semibold mb-4">Encryption at Rest</h4>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">AES-256 encryption for all stored data</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Hardware Security Modules (HSMs)</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Encrypted database backups</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Key rotation every 90 days</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-8 p-4 bg-blue-50 rounded-lg">
                <h4 className="text-lg font-semibold mb-2 text-blue-800">End-to-End Encryption</h4>
                <p className="text-blue-700 text-sm">
                  From the moment you submit a URL for analysis until you receive results, your data is protected 
                  with multiple layers of encryption. We use industry-standard cryptographic protocols to ensure 
                  your information remains secure throughout the entire analysis pipeline.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Infrastructure Security */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Server className="h-5 w-5 text-green-600" />
                <span>Infrastructure & Network Security</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold">Cloud Infrastructure</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center space-x-2">
                      <CheckCircle2 className="h-3 w-3 text-green-600" />
                      <span>Google Cloud Platform (GCP)</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircle2 className="h-3 w-3 text-green-600" />
                      <span>Multi-region deployment</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircle2 className="h-3 w-3 text-green-600" />
                      <span>Auto-scaling and load balancing</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircle2 className="h-3 w-3 text-green-600" />
                      <span>DDoS protection</span>
                    </li>
                  </ul>
                </div>
                
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold">Network Security</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center space-x-2">
                      <CheckCircle2 className="h-3 w-3 text-green-600" />
                      <span>Web Application Firewall (WAF)</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircle2 className="h-3 w-3 text-green-600" />
                      <span>Intrusion Detection System (IDS)</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircle2 className="h-3 w-3 text-green-600" />
                      <span>VPC with private subnets</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircle2 className="h-3 w-3 text-green-600" />
                      <span>Rate limiting and throttling</span>
                    </li>
                  </ul>
                </div>
                
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold">Monitoring</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center space-x-2">
                      <CheckCircle2 className="h-3 w-3 text-green-600" />
                      <span>24/7 security monitoring</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircle2 className="h-3 w-3 text-green-600" />
                      <span>Real-time alerting</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircle2 className="h-3 w-3 text-green-600" />
                      <span>Automated threat response</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircle2 className="h-3 w-3 text-green-600" />
                      <span>Comprehensive audit logging</span>
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Authentication & Access Control */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Eye className="h-5 w-5 text-purple-600" />
                <span>Authentication & Access Control</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg font-semibold mb-4">User Authentication</h4>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Firebase Authentication (Google-backed)</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Multi-Factor Authentication (MFA) support</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">OAuth 2.0 and OpenID Connect</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Session management with automatic expiry</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-lg font-semibold mb-4">Access Control</h4>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Role-Based Access Control (RBAC)</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Principle of least privilege</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">API rate limiting per user</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Regular access reviews</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-purple-50 rounded-lg">
                <h4 className="text-lg font-semibold mb-2 text-purple-800">Zero-Trust Architecture</h4>
                <p className="text-purple-700 text-sm">
                  We implement a zero-trust security model where every request is authenticated and authorized, 
                  regardless of the source. No implicit trust is granted based on network location.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Data Privacy */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-indigo-600" />
                <span>Data Privacy & Retention</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg font-semibold mb-4">Automatic Data Deletion</h4>
                  <div className="bg-red-50 p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                      <span className="font-semibold text-red-800">24-Hour Policy</span>
                    </div>
                    <p className="text-red-700 text-sm">
                      All analysis results and temporary data are automatically purged after 24 hours. 
                      No analysis data is retained beyond this period, ensuring maximum privacy protection.
                    </p>
                  </div>
                  
                  <h5 className="font-semibold mt-4 mb-2">What Gets Deleted</h5>
                  <ul className="space-y-1 text-sm">
                    <li>• Social media URLs analyzed</li>
                    <li>• Generated analysis results</li>
                    <li>• Temporary processing data</li>
                    <li>• AI model outputs</li>
                  </ul>
                </div>
                
                <div>
                  <h4 className="text-lg font-semibold mb-4">Data Minimization</h4>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Only collect necessary data</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">No tracking of personal browsing</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Anonymous usage analytics only</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Data pseudonymization</span>
                    </div>
                  </div>

                  <h5 className="font-semibold mt-4 mb-2">What We Keep</h5>
                  <ul className="space-y-1 text-sm">
                    <li>• Account authentication data</li>
                    <li>• Usage statistics (anonymized)</li>
                    <li>• System performance metrics</li>
                    <li>• Security audit logs</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Compliance */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Globe className="h-5 w-5 text-green-600" />
                <span>Compliance & Certifications</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <h4 className="font-semibold text-green-800 mb-2">GDPR</h4>
                  <p className="text-sm text-green-700">
                    Full compliance with European General Data Protection Regulation
                  </p>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-semibold text-blue-800 mb-2">SOC 2 Type II</h4>
                  <p className="text-sm text-blue-700">
                    Security, availability, and confidentiality controls audited
                  </p>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <h4 className="font-semibold text-purple-800 mb-2">ISO 27001</h4>
                  <p className="text-sm text-purple-700">
                    Information security management system certified
                  </p>
                </div>
              </div>

              <h4 className="text-lg font-semibold mb-4">Security Practices</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h5 className="font-semibold mb-2">Regular Audits</h5>
                  <ul className="space-y-1 text-sm">
                    <li>• Quarterly security assessments</li>
                    <li>• Annual penetration testing</li>
                    <li>• Continuous vulnerability scanning</li>
                    <li>• Third-party security reviews</li>
                  </ul>
                </div>
                <div>
                  <h5 className="font-semibold mb-2">Incident Response</h5>
                  <ul className="space-y-1 text-sm">
                    <li>• 24/7 security operations center</li>
                    <li>• Automated threat detection</li>
                    <li>• Incident response playbooks</li>
                    <li>• Post-incident analysis and improvement</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Contact Security Team */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-orange-600" />
                <span>Security Concerns & Reporting</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg font-semibold mb-3">Report a Security Issue</h4>
                  <p className="text-sm text-gray-600 mb-4">
                    If you discover a security vulnerability, please report it responsibly to our security team.
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium">Security Email:</span>
                      <a href="mailto:security@tracelens.ai" className="text-blue-600 underline text-sm">
                        security@tracelens.ai
                      </a>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium">Response Time:</span>
                      <span className="text-sm">Within 24 hours</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-lg font-semibold mb-3">Bug Bounty Program</h4>
                  <p className="text-sm text-gray-600 mb-4">
                    We reward security researchers who help us improve our security posture.
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium">Rewards:</span>
                      <span className="text-sm">Up to $5,000</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium">Scope:</span>
                      <span className="text-sm">tracelens.ai domain</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default SecurityPage;
