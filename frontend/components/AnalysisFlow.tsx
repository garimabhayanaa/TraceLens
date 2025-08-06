'use client'
import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Progress } from '@/components/ui/progress'
import { analysisAPI, AnalysisRequestData, AnalysisResults } from '@/lib/api'
import ConsentManagement from '@/components/consent/ConsentManagement'
import AnalysisDashboard from '@/components/dashboard/AnalysisDashboard'
import toast from 'react-hot-toast'
import { Loader2, Brain, Shield, CheckCircle, AlertCircle } from 'lucide-react'

type AnalysisStage = 'input' | 'consent' | 'processing' | 'complete'

interface AnalysisFlowProps {
  userId: string
  userEmail: string
}

const AnalysisFlow: React.FC<AnalysisFlowProps> = ({ userId, userEmail }) => {
  const [currentStage, setCurrentStage] = useState<AnalysisStage>('input')
  const [analysisData, setAnalysisData] = useState({
    targetDescription: '',
    useCaseDescription: '',
    analysisType: 'self_analysis',
    privacyLevel: 'standard',
    socialData: {}
  })
  const [sessionId, setSessionId] = useState('')
  const [consentProcessId, setConsentProcessId] = useState('')
  const [progress, setProgress] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<AnalysisResults | null>(null)
  const [processingSteps, setProcessingSteps] = useState<string[]>([])

  useEffect(() => {
    // Generate session ID
    setSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
  }, [])

  const handleInputSubmit = () => {
    if (!analysisData.targetDescription.trim() || !analysisData.useCaseDescription.trim()) {
      toast.error('Please fill in all required fields')
      return
    }

    if (analysisData.targetDescription.length < 10) {
      toast.error('Please provide a more detailed description (minimum 10 characters)')
      return
    }

    setCurrentStage('consent')
  }

  const handleConsentComplete = (processId: string) => {
    setConsentProcessId(processId)
    setCurrentStage('processing')
    performAnalysis(processId)
  }

  const performAnalysis = async (consentId: string) => {
    setIsLoading(true)
    setProgress(10)

    try {
      // Prepare analysis request data
      const requestData: AnalysisRequestData = {
        social_data: analysisData.socialData,
        user_id: userId,
        user_email: userEmail,
        analysis_type: analysisData.analysisType,
        target_data_description: analysisData.targetDescription,
        use_case_description: analysisData.useCaseDescription,
        age_verification_data: {
          verified: true,
          method: 'self_declaration',
          age_confirmed: true
        },
        consent_process_id: consentId,
        session_id: sessionId,
        privacy_level: analysisData.privacyLevel
      }

      setProgress(25)
      setProcessingSteps(prev => [...prev, '🔍 Initiating comprehensive analysis...'])

      // Perform analysis
      const response = await analysisAPI.performAnalysis(requestData)

      if (response.data.analysis_approved) {
        setProgress(50)
        setProcessingSteps(prev => [...prev, '✅ All security checks passed'])

        setProgress(75)
        setProcessingSteps(prev => [...prev, '🧠 AI analysis in progress...'])

        setProgress(90)
        setProcessingSteps(prev => [...prev, '📊 Generating insights and recommendations...'])

        setProgress(100)
        setProcessingSteps(prev => [...prev, '✅ Analysis complete!'])

        setResults(response.data)
        setCurrentStage('complete')

        toast.success('Analysis completed successfully!')
      } else {
        // Handle rejection
        const rejectionReason = response.data.rejection_reason
        const errorMessage = response.data.error_message || 'Analysis was rejected'

        toast.error(errorMessage)

        if (rejectionReason === 'abuse_prevention') {
          setProcessingSteps(prev => [...prev, '🚫 Analysis blocked by abuse prevention system'])
          setProcessingSteps(prev => [...prev, `⚠️ ${errorMessage}`])
        } else if (rejectionReason === 'content_moderation_block') {
          setProcessingSteps(prev => [...prev, '🚫 Content flagged by moderation system'])
          setProcessingSteps(prev => [...prev, `⚠️ ${errorMessage}`])
        } else {
          setProcessingSteps(prev => [...prev, `🚫 ${errorMessage}`])
        }
      }
    } catch (error: any) {
      console.error('Analysis error:', error)

      const errorMessage = error.response?.data?.error_message ||
                          error.response?.data?.error ||
                          'Analysis failed. Please try again.'

      toast.error(errorMessage)
      setProcessingSteps(prev => [...prev, `❌ Error: ${errorMessage}`])
    } finally {
      setIsLoading(false)
    }
  }

  const renderInputStage = () => (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-6 w-6" />
          Start AI Analysis
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <label className="block text-sm font-medium mb-2">
            Analysis Type
          </label>
          <select
            className="w-full p-3 border border-gray-300 rounded-lg"
            value={analysisData.analysisType}
            onChange={(e) => setAnalysisData(prev => ({ ...prev, analysisType: e.target.value }))}
          >
            <option value="self_analysis">Self Analysis (Your own profiles)</option>
            <option value="third_party_analysis">Third Party Analysis (With consent)</option>
            <option value="research_analysis">Research Analysis (Academic/Professional)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Target Data Description *
          </label>
          <Textarea
            placeholder="Describe what you want to analyze (e.g., 'My Twitter and LinkedIn profiles to understand my professional online presence')"
            value={analysisData.targetDescription}
            onChange={(e) => setAnalysisData(prev => ({ ...prev, targetDescription: e.target.value }))}
            className="min-h-[100px]"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Use Case Description *
          </label>
          <Textarea
            placeholder="Explain why you want this analysis (e.g., 'Personal development and career advancement insights')"
            value={analysisData.useCaseDescription}
            onChange={(e) => setAnalysisData(prev => ({ ...prev, useCaseDescription: e.target.value }))}
            className="min-h-[100px]"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Privacy Level
          </label>
          <select
            className="w-full p-3 border border-gray-300 rounded-lg"
            value={analysisData.privacyLevel}
            onChange={(e) => setAnalysisData(prev => ({ ...prev, privacyLevel: e.target.value }))}
          >
            <option value="minimal">Minimal (Research/Academic use)</option>
            <option value="standard">Standard (Recommended)</option>
            <option value="strict">Strict (Maximum privacy protection)</option>
          </select>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-start gap-2">
            <Shield className="h-5 w-5 text-blue-600 mt-0.5" />
            <div className="text-sm text-blue-700">
              <p className="font-medium mb-1">Your analysis will include:</p>
              <ul className="space-y-1">
                <li>• Comprehensive sentiment and emotional analysis</li>
                <li>• Behavioral pattern recognition across platforms</li>
                <li>• Professional and economic indicator analysis</li>
                <li>• Mental well-being assessment and recommendations</li>
                <li>• Complete privacy protection with zero data retention</li>
              </ul>
            </div>
          </div>
        </div>

        <Button
          onClick={handleInputSubmit}
          className="w-full"
          size="lg"
        >
          Continue to Consent Management
        </Button>
      </CardContent>
    </Card>
  )

  const renderProcessingStage = () => (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          Processing Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Analysis Progress</span>
              <span className="text-sm text-gray-600">{progress}%</span>
            </div>
            <Progress value={progress} className="w-full" />
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium mb-3">Processing Steps:</h4>
            <div className="space-y-2">
              {processingSteps.map((step, index) => (
                <div key={index} className="flex items-start gap-2 text-sm">
                  <span className="text-gray-500 min-w-[20px]">{index + 1}.</span>
                  <span>{step}</span>
                </div>
              ))}
              {isLoading && (
                <div className="flex items-center gap-2 text-sm text-blue-600">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Processing...</span>
                </div>
              )}
            </div>
          </div>

          <div className="text-center text-gray-600">
            <p>This may take a few moments. Please don't close this page.</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-8">
            {['Input', 'Consent', 'Processing', 'Complete'].map((stage, index) => {
              const stageValues: AnalysisStage[] = ['input', 'consent', 'processing', 'complete']
              const isActive = stageValues.indexOf(currentStage) >= index
              const isCurrent = stageValues[index] === currentStage

              return (
                <div key={stage} className="flex items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    isActive ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
                  } ${isCurrent ? 'ring-4 ring-blue-200' : ''}`}>
                    {index + 1}
                  </div>
                  <span className={`ml-2 font-medium ${
                    isActive ? 'text-blue-600' : 'text-gray-600'
                  }`}>
                    {stage}
                  </span>
                  {index < 3 && <div className="w-8 h-px bg-gray-300 mx-4" />}
                </div>
              )
            })}
          </div>
        </div>

        {/* Stage Content */}
        {currentStage === 'input' && renderInputStage()}

        {currentStage === 'consent' && (
          <ConsentManagement
            userId={userId}
            sessionId={sessionId}
            onConsentComplete={handleConsentComplete}
          />
        )}

        {currentStage === 'processing' && renderProcessingStage()}

        {currentStage === 'complete' && results && (
          <AnalysisDashboard
            results={results}
            sessionId={sessionId}
            userId={userId}
          />
        )}
      </div>
    </div>
  )
}

export default AnalysisFlow
