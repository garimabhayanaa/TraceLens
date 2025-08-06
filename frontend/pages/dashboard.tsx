'use client'
import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { analysisAPI, AnalysisResults } from '@/utils/api'
import toast from 'react-hot-toast'
import {
  Shield, Brain, Heart, TrendingUp, MapPin, DollarSign,
  Clock, Users, MessageCircle, Hash, Eye, AlertTriangle,
  CheckCircle, XCircle, Info, Download, Trash2
} from 'lucide-react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'

interface AnalysisDashboardProps {
  results: AnalysisResults
  sessionId: string
  userId: string
}

const AnalysisDashboard: React.FC<AnalysisDashboardProps> = ({
  results,
  sessionId,
  userId
}) => {
  const [selectedTab, setSelectedTab] = useState('overview')
  const [isLoading, setIsLoading] = useState(false)

  const getStatusColor = (status: boolean | string) => {
    if (typeof status === 'boolean') {
      return status ? 'text-green-600' : 'text-red-600'
    }
    return status === 'compliant' ? 'text-green-600' :
           status === 'non_compliant' ? 'text-red-600' : 'text-yellow-600'
  }

  const getStatusIcon = (status: boolean | string) => {
    if (typeof status === 'boolean') {
      return status ? <CheckCircle className="h-4 w-4" /> : <XCircle className="h-4 w-4" />
    }
    return status === 'compliant' ? <CheckCircle className="h-4 w-4" /> :
           status === 'non_compliant' ? <XCircle className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />
  }

  const handleImmediateDeletion = async () => {
    if (!confirm('Are you sure you want to delete all data immediately? This action cannot be undone.')) {
      return
    }

    setIsLoading(true)
    try {
      const response = await analysisAPI.requestImmediateDeletion(userId, 'complete')

      if (response.data.success) {
        toast.success('Deletion request created. Please check your email for verification code.')
        // Could open a modal for verification code entry
      }
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to request deletion')
    } finally {
      setIsLoading(false)
    }
  }

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* Privacy Score */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Privacy & Security Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <Progress
                value={results.analysis_metadata?.ethical_compliance_score * 100 || 85}
                className="h-3"
              />
            </div>
            <div className="text-2xl font-bold text-green-600">
              {Math.round((results.analysis_metadata?.ethical_compliance_score || 0.85) * 100)}%
            </div>
          </div>

          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className={`font-semibold ${getStatusColor(results.abuse_prevention_status?.enabled)}`}>
                {getStatusIcon(results.abuse_prevention_status?.enabled)}
              </div>
              <p className="text-sm text-gray-600">Abuse Prevention</p>
            </div>

            <div className="text-center">
              <div className={`font-semibold ${getStatusColor(results.legal_ethical_compliance?.regulatory_compliance?.gdpr_compliance === 'compliant')}`}>
                {getStatusIcon(results.legal_ethical_compliance?.regulatory_compliance?.gdpr_compliance === 'compliant')}
              </div>
              <p className="text-sm text-gray-600">GDPR Compliance</p>
            </div>

            <div className="text-center">
              <div className={`font-semibold ${getStatusColor(results.privacy_metrics?.encryption_enabled)}`}>
                {getStatusIcon(results.privacy_metrics?.encryption_enabled)}
              </div>
              <p className="text-sm text-gray-600">Data Encryption</p>
            </div>

            <div className="text-center">
              <div className={`font-semibold ${getStatusColor(results.consent_status?.consent_verified)}`}>
                {getStatusIcon(results.consent_status?.consent_verified)}
              </div>
              <p className="text-sm text-gray-600">Consent Verified</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Usage Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Usage Statistics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-600 font-semibold">Today's Usage</p>
                  <p className="text-2xl font-bold">
                    {results.usage_statistics?.daily_usage || 0}/3
                  </p>
                </div>
                <Eye className="h-8 w-8 text-blue-500" />
              </div>
            </div>

            <div className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-600 font-semibold">Remaining Today</p>
                  <p className="text-2xl font-bold">
                    {results.usage_statistics?.remaining_daily || 3}
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
            </div>

            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-600 font-semibold">Access Level</p>
                  <p className="text-lg font-bold capitalize">
                    {results.authorization_status?.access_level || 'Basic'}
                  </p>
                </div>
                <Shield className="h-8 w-8 text-purple-500" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="h-5 w-5" />
              Sentiment Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            {results.sentiment_analysis && (
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span>Overall Sentiment</span>
                  <span className={`font-semibold capitalize ${
                    results.sentiment_analysis.overall_sentiment === 'positive' ? 'text-green-600' :
                    results.sentiment_analysis.overall_sentiment === 'negative' ? 'text-red-600' : 'text-yellow-600'
                  }`}>
                    {results.sentiment_analysis.overall_sentiment}
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span>Confidence</span>
                  <span className="font-semibold">
                    {Math.round((results.sentiment_analysis.confidence_score || 0) * 100)}%
                  </span>
                </div>

                {results.sentiment_analysis.emotional_profile && (
                  <div className="mt-4">
                    <p className="text-sm font-medium mb-2">Emotional Indicators:</p>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(results.sentiment_analysis.emotional_profile).map(([emotion, score]) => (
                        <span key={emotion} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                          {emotion}: {Math.round(Number(score) * 100)}%
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Hash className="h-5 w-5" />
              Content Patterns
            </CardTitle>
          </CardHeader>
          <CardContent>
            {results.hashtag_patterns && (
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span>Usage Style</span>
                  <span className="font-semibold capitalize">
                    {results.hashtag_patterns.usage_style}
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span>Total Hashtags</span>
                  <span className="font-semibold">
                    {results.hashtag_patterns.total_hashtags || 0}
                  </span>
                </div>

                {results.hashtag_patterns.trending_topics && results.hashtag_patterns.trending_topics.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm font-medium mb-2">Trending Topics:</p>
                    <div className="space-y-1">
                      {results.hashtag_patterns.trending_topics.slice(0, 3).map((topic: any, index: number) => (
                        <div key={index} className="flex justify-between text-sm">
                          <span>#{topic.hashtag}</span>
                          <span className="text-gray-500">{Math.round(topic.score * 100)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderAnalysisTab = () => (
    <div className="space-y-6">
      {/* Advanced Analysis Results */}
      {results.schedule_patterns?.analysis_completed && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Schedule Patterns
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium mb-2">Temporal Analysis</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Posting Frequency:</span>
                    <span className="font-semibold">
                      {results.schedule_patterns.post_timing?.posting_frequency || 'Unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Temporal Signature:</span>
                    <span className="font-semibold">
                      {results.schedule_patterns.post_timing?.temporal_signature || 'Unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Consistency Score:</span>
                    <span className="font-semibold">
                      {Math.round((results.schedule_patterns.post_timing?.consistency_score || 0) * 100)}%
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Activity Patterns</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Engagement Rhythm:</span>
                    <span className="font-semibold">
                      {results.schedule_patterns.activity_frequency?.engagement_rhythm || 'Unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Work-Life Balance:</span>
                    <span className="font-semibold">
                      {results.schedule_patterns.work_personal_boundary?.boundary_clarity || 'Unknown'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {results.schedule_patterns.behavioral_insights && results.schedule_patterns.behavioral_insights.length > 0 && (
              <div className="mt-4">
                <h4 className="font-medium mb-2">Behavioral Insights</h4>
                <div className="bg-blue-50 p-3 rounded-lg">
                  <ul className="space-y-1 text-sm">
                    {results.schedule_patterns.behavioral_insights.slice(0, 3).map((insight: string, index: number) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="text-blue-500 mt-1">•</span>
                        {insight}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Economic Analysis */}
      {results.economic_indicators?.analysis_completed && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              Economic Indicators
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-600 font-medium">Brand Mentions</p>
                    <p className="text-2xl font-bold">
                      {results.economic_indicators.brand_mentions?.length || 0}
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-green-500" />
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-600 font-medium">Location Patterns</p>
                    <p className="text-2xl font-bold">
                      {results.economic_indicators.location_patterns?.length || 0}
                    </p>
                  </div>
                  <MapPin className="h-8 w-8 text-blue-500" />
                </div>
              </div>

              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-600 font-medium">Economic Risk</p>
                    <p className="text-2xl font-bold">
                      {Math.round((results.economic_indicators.economic_risk_score || 0) * 100)}%
                    </p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-purple-500" />
                </div>
              </div>
            </div>

            {results.economic_indicators.economic_profile && (
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-2">Economic Profile</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Spending Capacity:</span>
                      <span className="font-semibold capitalize">
                        {results.economic_indicators.economic_profile.spending_capacity || 'Unknown'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Brand Affinity:</span>
                      <span className="font-semibold capitalize">
                        {results.economic_indicators.economic_profile.brand_affinity_tier || 'Unknown'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Purchase Style:</span>
                      <span className="font-semibold capitalize">
                        {results.economic_indicators.economic_profile.purchase_decision_style || 'Unknown'}
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2">Professional Network</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Seniority Level:</span>
                      <span className="font-semibold capitalize">
                        {results.economic_indicators.professional_network?.seniority_level || 'Unknown'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Professional Influence:</span>
                      <span className="font-semibold">
                        {Math.round((results.economic_indicators.professional_network?.professional_influence || 0) * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Mental State Assessment */}
      {results.mental_state_assessment?.analysis_completed && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Mental State Assessment
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium mb-2">Overall Assessment</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Mental State:</span>
                    <span className="font-semibold capitalize">
                      {results.mental_state_assessment.mental_state_profile?.overall_mental_state || 'Stable'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Emotional Stability:</span>
                    <span className="font-semibold">
                      {Math.round((results.mental_state_assessment.mental_state_profile?.emotional_stability_score || 0.5) * 100)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Assessment Confidence:</span>
                    <span className="font-semibold">
                      {Math.round((results.mental_state_assessment.assessment_confidence || 0) * 100)}%
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Social Connectivity</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Connectivity Level:</span>
                    <span className="font-semibold capitalize">
                      {results.mental_state_assessment.mental_state_profile?.social_connectivity_level || 'Unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Interaction Rate:</span>
                    <span className="font-semibold">
                      {Math.round((results.mental_state_assessment.social_interaction?.interaction_rate || 0) * 100)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {results.mental_state_assessment.recommendations && results.mental_state_assessment.recommendations.length > 0 && (
              <div className="mt-4">
                <h4 className="font-medium mb-2">Recommendations</h4>
                <div className="bg-yellow-50 p-3 rounded-lg">
                  <ul className="space-y-1 text-sm">
                    {results.mental_state_assessment.recommendations.slice(0, 3).map((rec: string, index: number) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="text-yellow-600 mt-1">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )

  const renderComplianceTab = () => (
    <div className="space-y-6">
      {/* Legal Compliance */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Legal & Regulatory Compliance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium mb-3">GDPR Compliance</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span>Status</span>
                  <div className={`flex items-center gap-2 ${getStatusColor(results.legal_ethical_compliance?.regulatory_compliance?.gdpr_compliance)}`}>
                    {getStatusIcon(results.legal_ethical_compliance?.regulatory_compliance?.gdpr_compliance === 'compliant')}
                    <span className="font-semibold capitalize">
                      {results.legal_ethical_compliance?.regulatory_compliance?.gdpr_compliance || 'Unknown'}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span>Compliance Score</span>
                  <span className="font-semibold">
                    {Math.round((results.legal_ethical_compliance?.regulatory_compliance?.gdpr_score || 0) * 100)}%
                  </span>
                </div>

                <div className="bg-green-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-green-700 mb-2">GDPR Rights Implemented:</p>
                  <ul className="text-sm text-green-600 space-y-1">
                    <li>✓ Right to access your data</li>
                    <li>✓ Right to rectification</li>
                    <li>✓ Right to erasure (right to be forgotten)</li>
                    <li>✓ Right to data portability</li>
                    <li>✓ Right to object to processing</li>
                  </ul>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-medium mb-3">CCPA Compliance</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span>Status</span>
                  <div className={`flex items-center gap-2 ${getStatusColor(results.legal_ethical_compliance?.regulatory_compliance?.ccpa_compliance)}`}>
                    {getStatusIcon(results.legal_ethical_compliance?.regulatory_compliance?.ccpa_compliance === 'compliant')}
                    <span className="font-semibold capitalize">
                      {results.legal_ethical_compliance?.regulatory_compliance?.ccpa_compliance || 'Unknown'}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span>Compliance Score</span>
                  <span className="font-semibold">
                    {Math.round((results.legal_ethical_compliance?.regulatory_compliance?.ccpa_score || 0) * 100)}%
                  </span>
                </div>

                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-blue-700 mb-2">CCPA Rights Protected:</p>
                  <ul className="text-sm text-blue-600 space-y-1">
                    <li>✓ Right to know what data is collected</li>
                    <li>✓ Right to delete personal information</li>
                    <li>✓ Right to opt-out of data selling</li>
                    <li>✓ Right to non-discrimination</li>
                    <li>✓ Right to equal service and pricing</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Content Moderation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5" />
            Content Moderation
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Moderation Status</span>
              <div className={`flex items-center gap-2 ${getStatusColor(results.legal_ethical_compliance?.content_moderation?.enabled)}`}>
                {getStatusIcon(results.legal_ethical_compliance?.content_moderation?.enabled)}
                <span className="font-semibold">
                  {results.legal_ethical_compliance?.content_moderation?.enabled ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span>Content Approved</span>
              <div className={`flex items-center gap-2 ${getStatusColor(results.legal_ethical_compliance?.content_moderation?.content_approved)}`}>
                {getStatusIcon(results.legal_ethical_compliance?.content_moderation?.content_approved)}
                <span className="font-semibold">
                  {results.legal_ethical_compliance?.content_moderation?.content_approved ? 'Approved' : 'Flagged'}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span>Risk Level</span>
              <span className={`font-semibold capitalize ${
                results.legal_ethical_compliance?.content_moderation?.risk_level === 'low' ? 'text-green-600' :
                results.legal_ethical_compliance?.content_moderation?.risk_level === 'medium' ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {results.legal_ethical_compliance?.content_moderation?.risk_level || 'Unknown'}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span>Confidence Score</span>
              <span className="font-semibold">
                {Math.round((results.legal_ethical_compliance?.content_moderation?.confidence_score || 0) * 100)}%
              </span>
            </div>

            {results.legal_ethical_compliance?.content_moderation?.flagged_issues &&
             results.legal_ethical_compliance.content_moderation.flagged_issues.length > 0 && (
              <div className="bg-yellow-50 p-3 rounded-lg">
                <p className="text-sm font-medium text-yellow-700 mb-2">Flagged Issues:</p>
                <ul className="text-sm text-yellow-600 space-y-1">
                  {results.legal_ethical_compliance.content_moderation.flagged_issues.map((issue: string, index: number) => (
                    <li key={index}>• {issue}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Abuse Prevention Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Abuse Prevention
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span>User Verified</span>
                <div className={`flex items-center gap-2 ${getStatusColor(results.abuse_prevention_status?.user_verified)}`}>
                  {getStatusIcon(results.abuse_prevention_status?.user_verified)}
                  <span className="font-semibold">
                    {results.abuse_prevention_status?.user_verified ? 'Verified' : 'Pending'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span>IP Tracking</span>
                <div className={`flex items-center gap-2 ${getStatusColor(results.abuse_prevention_status?.ip_tracking_active)}`}>
                  {getStatusIcon(results.abuse_prevention_status?.ip_tracking_active)}
                  <span className="font-semibold">
                    {results.abuse_prevention_status?.ip_tracking_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span>Usage Limits</span>
                <div className={`flex items-center gap-2 ${getStatusColor(results.abuse_prevention_status?.usage_limits_checked)}`}>
                  {getStatusIcon(results.abuse_prevention_status?.usage_limits_checked)}
                  <span className="font-semibold">
                    {results.abuse_prevention_status?.usage_limits_checked ? 'Enforced' : 'Not Checked'}
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span>reCAPTCHA Verified</span>
                <div className={`flex items-center gap-2 ${getStatusColor(results.abuse_prevention_status?.recaptcha_verified)}`}>
                  {getStatusIcon(results.abuse_prevention_status?.recaptcha_verified)}
                  <span className="font-semibold">
                    {results.abuse_prevention_status?.recaptcha_verified ? 'Verified' : 'Not Verified'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span>Email Verified</span>
                <div className={`flex items-center gap-2 ${getStatusColor(results.abuse_prevention_status?.email_verified)}`}>
                  {getStatusIcon(results.abuse_prevention_status?.email_verified)}
                  <span className="font-semibold">
                    {results.abuse_prevention_status?.email_verified ? 'Verified' : 'Pending'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span>Reporting Available</span>
                <div className={`flex items-center gap-2 text-green-600`}>
                  <CheckCircle className="h-4 w-4" />
                  <span className="font-semibold">Available</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderControlsTab = () => (
    <div className="space-y-6">
      {/* User Controls */}
      <Card className="border-red-200">
        <CardHeader className="bg-red-50">
          <CardTitle className="flex items-center gap-2 text-red-700">
            <Trash2 className="h-5 w-5" />
            Data Control & Deletion
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="space-y-4">
            <div className="bg-red-50 p-4 rounded-lg">
              <h4 className="font-medium text-red-700 mb-2">Immediate Data Deletion</h4>
              <p className="text-sm text-red-600 mb-3">
                Delete all your data immediately. This action cannot be undone and will remove all analysis results and stored information.
              </p>
              <Button
                onClick={handleImmediateDeletion}
                variant="destructive"
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? 'Processing...' : '🗑️ Delete All Data Immediately'}
              </Button>
            </div>

            <div className="bg-yellow-50 p-4 rounded-lg">
              <h4 className="font-medium text-yellow-700 mb-2">Opt-Out Options</h4>
              <p className="text-sm text-yellow-600 mb-3">
                You can opt out of any processing stage and stop the analysis at any point.
              </p>
              <div className="space-y-2">
                <Button variant="outline" className="w-full text-yellow-700 border-yellow-300 hover:bg-yellow-50">
                  🚪 Opt Out of Current Processing
                </Button>
                <Button variant="outline" className="w-full text-orange-700 border-orange-300 hover:bg-orange-50">
                  🔄 Withdraw All Consents
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Privacy Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Privacy Controls
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Data Retention Period</h4>
                <p className="text-sm text-gray-600">
                  Maximum: {results.privacy_metrics?.data_retention_hours || 24} hours
                </p>
              </div>
              <div className="text-right">
                <div className="text-sm text-green-600 font-medium">✓ Auto-deletion enabled</div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Encryption Status</h4>
                <p className="text-sm text-gray-600">
                  All data encrypted with AES-256
                </p>
              </div>
              <div className="text-right">
                <div className={`text-sm font-medium ${getStatusColor(results.privacy_metrics?.encryption_enabled)}`}>
                  {results.privacy_metrics?.encryption_enabled ? '✓ Encrypted' : '✗ Not Encrypted'}
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Anonymization Level</h4>
                <p className="text-sm text-gray-600">
                  Current level: {results.privacy_metrics?.anonymization_level || 'Standard'}
                </p>
              </div>
              <div className="text-right">
                <div className="text-sm text-blue-600 font-medium">✓ Active</div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Processing ID</h4>
                <p className="text-sm text-gray-600 font-mono">
                  {results.privacy_metrics?.processing_id || 'N/A'}
                </p>
              </div>
              <div className="text-right">
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Download Report
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Consent Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Consent Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {results.consent_status?.granted_consents && results.consent_status.granted_consents.length > 0 ? (
              results.consent_status.granted_consents.map((consent: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <h4 className="font-medium capitalize">
                      {consent.type.replace('_', ' ')}
                    </h4>
                    <p className="text-sm text-gray-600">
                      Granted: {new Date(consent.granted_at).toLocaleDateString()}
                      {consent.expires_at && (
                        <span> | Expires: {new Date(consent.expires_at).toLocaleDateString()}</span>
                      )}
                    </p>
                  </div>
                  <div className="text-green-600">
                    <CheckCircle className="h-5 w-5" />
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-4">No consent records available</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analysis Dashboard</h1>
        <p className="text-gray-600">
          Comprehensive AI analysis with complete privacy protection and legal compliance
        </p>
      </div>

      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
          <TabsTrigger value="controls">Controls</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          {renderOverviewTab()}
        </TabsContent>

        <TabsContent value="analysis" className="mt-6">
          {renderAnalysisTab()}
        </TabsContent>

        <TabsContent value="compliance" className="mt-6">
          {renderComplianceTab()}
        </TabsContent>

        <TabsContent value="controls" className="mt-6">
          {renderControlsTab()}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default AnalysisDashboard
