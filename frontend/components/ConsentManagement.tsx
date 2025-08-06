'use client'
import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { consentAPI } from '@/lib/api'
import toast from 'react-hot-toast'
import { Shield, Info, CheckCircle, AlertTriangle } from 'lucide-react'

interface ConsentStep {
  type: string
  title: string
  description: string
  granted: boolean
  required: boolean
  details: string[]
}

interface ConsentManagementProps {
  userId: string
  sessionId: string
  onConsentComplete: (processId: string) => void
}

const ConsentManagement: React.FC<ConsentManagementProps> = ({
  userId,
  sessionId,
  onConsentComplete
}) => {
  const [consentSteps, setConsentSteps] = useState<ConsentStep[]>([
    {
      type: 'data_collection',
      title: 'Data Collection',
      description: 'Allow collection of publicly available social media data',
      granted: false,
      required: true,
      details: [
        'Public profile information (username, bio, follower count)',
        'Recent public posts and content',
        'Public engagement metrics (likes, shares, comments)',
        'No private messages or personal data'
      ]
    },
    {
      type: 'data_processing',
      title: 'Data Processing',
      description: 'Allow AI analysis of collected data',
      granted: false,
      required: true,
      details: [
        'Sentiment analysis of public content',
        'Topic modeling and interest categorization',
        'Pattern recognition in posting behavior',
        'All processing performed on anonymized data'
      ]
    },
    {
      type: 'analysis_inference',
      title: 'Analysis & Inference',
      description: 'Allow generation of insights and recommendations',
      granted: false,
      required: true,
      details: [
        'Personality and interest profiling',
        'Behavioral pattern analysis',
        'Risk assessment and recommendations',
        'Cross-platform correlation analysis'
      ]
    },
    {
      type: 'data_retention',
      title: 'Temporary Data Retention',
      description: 'Allow temporary data storage (max 24 hours)',
      granted: false,
      required: false,
      details: [
        'Data stored for analysis optimization',
        'Automatic deletion after 24 hours maximum',
        'Encrypted storage with secure deletion',
        'Can be deleted immediately upon request'
      ]
    },
    {
      type: 'result_storage',
      title: 'Result Storage',
      description: 'Allow storage of analysis results for your review',
      granted: false,
      required: false,
      details: [
        'Analysis results stored in your account',
        'Results can be downloaded or deleted anytime',
        'Used for historical comparison and trends',
        'You maintain complete control over your results'
      ]
    }
  ])

  const [processId, setProcessId] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)

  useEffect(() => {
    initializeConsentProcess()
  }, [])

  const initializeConsentProcess = async () => {
    try {
      const response = await consentAPI.initiateConsentProcess(userId, sessionId)
      if (response.data.success) {
        setProcessId(response.data.process_id)
      }
    } catch (error) {
      toast.error('Failed to initialize consent process')
    }
  }

  const handleConsentChange = async (stepIndex: number, granted: boolean) => {
    const step = consentSteps[stepIndex]
    setIsLoading(true)

    try {
      const response = await consentAPI.processConsentStep(
        processId,
        step.type,
        granted
      )

      if (response.data.success) {
        setConsentSteps(prev => prev.map((s, i) =>
          i === stepIndex ? { ...s, granted } : s
        ))

        if (granted && stepIndex === currentStep) {
          setCurrentStep(prev => Math.min(prev + 1, consentSteps.length - 1))
        }

        toast.success(`${step.title} consent ${granted ? 'granted' : 'withdrawn'}`)

        // Check if all required consents are granted
        const updatedSteps = consentSteps.map((s, i) =>
          i === stepIndex ? { ...s, granted } : s
        )

        const allRequiredGranted = updatedSteps
          .filter(s => s.required)
          .every(s => s.granted || s.type === step.type && granted)

        if (allRequiredGranted) {
          onConsentComplete(processId)
        }
      }
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to process consent')
    } finally {
      setIsLoading(false)
    }
  }

  const getProgressPercentage = () => {
    const grantedRequired = consentSteps.filter(s => s.required && s.granted).length
    const totalRequired = consentSteps.filter(s => s.required).length
    return (grantedRequired / totalRequired) * 100
  }

  const canProceed = () => {
    return consentSteps.filter(s => s.required).every(s => s.granted)
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-6 w-6" />
            Consent Management
          </CardTitle>
          <div className="space-y-2">
            <Progress value={getProgressPercentage()} className="w-full" />
            <p className="text-sm text-gray-600">
              {consentSteps.filter(s => s.required && s.granted).length} of{' '}
              {consentSteps.filter(s => s.required).length} required consents granted
            </p>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {consentSteps.map((step, index) => (
              <Card key={step.type} className={`${
                index === currentStep ? 'border-blue-500 shadow-md' : ''
              }`}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                          step.granted ? 'bg-green-500 text-white' : 
                          step.required ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'
                        }`}>
                          {step.granted ? (
                            <CheckCircle className="h-4 w-4" />
                          ) : step.required ? (
                            <AlertTriangle className="h-4 w-4" />
                          ) : (
                            <Info className="h-4 w-4" />
                          )}
                        </div>

                        <div>
                          <h3 className="font-semibold flex items-center gap-2">
                            {step.title}
                            {step.required && (
                              <span className="text-red-500 text-sm">*Required</span>
                            )}
                          </h3>
                          <p className="text-gray-600 text-sm">{step.description}</p>
                        </div>
                      </div>

                      <div className="ml-9 space-y-2">
                        <div className="bg-gray-50 p-3 rounded-lg">
                          <p className="text-sm font-medium mb-2">What this includes:</p>
                          <ul className="text-sm text-gray-600 space-y-1">
                            {step.details.map((detail, detailIndex) => (
                              <li key={detailIndex} className="flex items-start gap-2">
                                <span className="text-blue-500 mt-1">•</span>
                                {detail}
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="flex items-center gap-4">
                          <Button
                            variant={step.granted ? "default" : "outline"}
                            size="sm"
                            onClick={() => handleConsentChange(index, true)}
                            disabled={isLoading}
                            className="min-w-[80px]"
                          >
                            {step.granted ? '✓ Granted' : 'Grant'}
                          </Button>

                          {step.granted && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleConsentChange(index, false)}
                              disabled={isLoading}
                              className="min-w-[80px] text-red-600 border-red-300 hover:bg-red-50"
                            >
                              Withdraw
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-start gap-2">
              <Info className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="text-sm text-blue-700">
                <p className="font-medium mb-1">Your Rights & Controls:</p>
                <ul className="space-y-1">
                  <li>• You can withdraw consent at any time</li>
                  <li>• All data can be deleted immediately upon request</li>
                  <li>• Processing can be stopped at any stage</li>
                  <li>• You maintain complete control over your information</li>
                </ul>
              </div>
            </div>
          </div>

          {canProceed() && (
            <div className="mt-6 text-center">
              <div className="bg-green-50 p-4 rounded-lg">
                <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
                <p className="text-green-700 font-medium">
                  All required consents granted! You can now proceed with the analysis.
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default ConsentManagement
