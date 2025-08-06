'use client'
import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import ReCAPTCHA from "react-google-recaptcha"
import toast from 'react-hot-toast'
import { authAPI, UserRegistrationData, EmailVerificationData } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { AlertCircle, Mail, Shield, CheckCircle } from 'lucide-react'

interface AuthFormData {
  email: string
  password: string
  confirmPassword: string
}

type AuthStep = 'register' | 'verify-email' | 'complete'

const AuthenticationFlow: React.FC = () => {
  const [currentStep, setCurrentStep] = useState<AuthStep>('register')
  const [recaptchaToken, setRecaptchaToken] = useState<string | null>(null)
  const [verificationData, setVerificationData] = useState({
    verification_id: '',
    user_id: '',
    email: ''
  })
  const [verificationCode, setVerificationCode] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [remainingAttempts, setRemainingAttempts] = useState(3)

  const router = useRouter()
  const { register, handleSubmit, watch, formState: { errors }, reset } = useForm<AuthFormData>()

  const password = watch('password')

  const handleRegistration = async (data: AuthFormData) => {
    if (!recaptchaToken) {
      toast.error('Please complete the reCAPTCHA verification')
      return
    }

    if (data.password !== data.confirmPassword) {
      toast.error('Passwords do not match')
      return
    }

    setIsLoading(true)

    try {
      const registrationData: UserRegistrationData = {
        email: data.email,
        password: data.password,
        recaptcha_token: recaptchaToken
      }

      const response = await authAPI.register(registrationData)

      if (response.data.success) {
        setVerificationData({
          verification_id: response.data.verification_id,
          user_id: response.data.user_id,
          email: data.email
        })
        setCurrentStep('verify-email')
        toast.success('Registration successful! Please check your email for verification code.')
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Registration failed'
      toast.error(errorMessage)

      // Handle specific error types
      if (error.response?.data?.rejection_reason === 'abuse_prevention') {
        const retryAfter = error.response?.data?.verification_result?.retry_after
        if (retryAfter) {
          toast.error(`Please try again in ${Math.ceil(retryAfter / 60)} minutes`)
        }
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleEmailVerification = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      toast.error('Please enter a valid 6-digit verification code')
      return
    }

    setIsLoading(true)

    try {
      const emailVerificationData: EmailVerificationData = {
        verification_id: verificationData.verification_id,
        verification_code: verificationCode,
        user_id: verificationData.user_id
      }

      const response = await authAPI.verifyEmail(emailVerificationData)

      if (response.data.success) {
        setCurrentStep('complete')
        toast.success('Email verified successfully!')

        // Store auth token if provided
        if (response.data.token) {
          localStorage.setItem('auth_token', response.data.token)
          localStorage.setItem('user_data', JSON.stringify(response.data.user))
        }

        // Redirect to dashboard after success
        setTimeout(() => {
          router.push('/dashboard')
        }, 2000)
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Verification failed'
      toast.error(errorMessage)

      setRemainingAttempts(prev => prev - 1)

      if (remainingAttempts <= 1) {
        toast.error('Too many failed attempts. Please request a new verification code.')
        setCurrentStep('register')
        reset()
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleResendVerification = async () => {
    setIsLoading(true)

    try {
      const response = await authAPI.initiateEmailVerification(
        verificationData.user_id,
        verificationData.email
      )

      if (response.data.success) {
        setVerificationData(prev => ({
          ...prev,
          verification_id: response.data.verification_id
        }))
        setRemainingAttempts(3)
        toast.success('New verification code sent to your email!')
      }
    } catch (error: any) {
      toast.error('Failed to resend verification code')
    } finally {
      setIsLoading(false)
    }
  }

  const renderRegistrationStep = () => (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5" />
          Create Secure Account
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(handleRegistration)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Email Address</label>
            <Input
              type="email"
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                  message: 'Invalid email address'
                }
              })}
              className={errors.email ? 'border-red-500' : ''}
            />
            {errors.email && (
              <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Password</label>
            <Input
              type="password"
              {...register('password', {
                required: 'Password is required',
                minLength: {
                  value: 8,
                  message: 'Password must be at least 8 characters'
                }
              })}
              className={errors.password ? 'border-red-500' : ''}
            />
            {errors.password && (
              <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Confirm Password</label>
            <Input
              type="password"
              {...register('confirmPassword', {
                required: 'Please confirm your password',
                validate: value => value === password || 'Passwords do not match'
              })}
              className={errors.confirmPassword ? 'border-red-500' : ''}
            />
            {errors.confirmPassword && (
              <p className="text-red-500 text-sm mt-1">{errors.confirmPassword.message}</p>
            )}
          </div>

          <div className="flex justify-center">
            <ReCAPTCHA
              sitekey={process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY!}
              onChange={setRecaptchaToken}
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading || !recaptchaToken}
          >
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </Button>
        </form>

        <div className="mt-6 space-y-2 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span>✅ Email verification required</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span>✅ Bot protection enabled</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span>✅ 3 free analyses per day</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span>✅ Zero data retention</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const renderEmailVerificationStep = () => (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Mail className="h-5 w-5" />
          Verify Your Email
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center mb-6">
          <p className="text-gray-600 mb-2">
            We've sent a 6-digit verification code to:
          </p>
          <p className="font-semibold text-blue-600">{verificationData.email}</p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Enter Verification Code
            </label>
            <Input
              type="text"
              maxLength={6}
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
              placeholder="000000"
              className="text-center text-2xl tracking-widest font-mono"
            />
          </div>

          <Button
            onClick={handleEmailVerification}
            className="w-full"
            disabled={isLoading || verificationCode.length !== 6}
          >
            {isLoading ? 'Verifying...' : 'Verify Email'}
          </Button>

          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">
              Remaining attempts: {remainingAttempts}
            </p>
            <button
              onClick={handleResendVerification}
              className="text-blue-600 hover:underline text-sm"
              disabled={isLoading}
            >
              Resend verification code
            </button>
          </div>
        </div>

        <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
            <div className="text-sm text-yellow-700">
              <p>The code expires in 15 minutes.</p>
              <p>Check your spam folder if you don't see the email.</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const renderCompleteStep = () => (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-green-600">
          <CheckCircle className="h-5 w-5" />
          Account Created Successfully!
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center space-y-4">
          <div className="bg-green-50 p-6 rounded-lg">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <p className="text-green-700 font-medium">
              Your account has been verified and is ready to use!
            </p>
          </div>

          <div className="text-sm text-gray-600 space-y-2">
            <p>✅ Email verified successfully</p>
            <p>✅ Account security enabled</p>
            <p>✅ Ready for AI analysis</p>
          </div>

          <p className="text-gray-600">
            Redirecting to dashboard...
          </p>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {currentStep === 'register' && renderRegistrationStep()}
        {currentStep === 'verify-email' && renderEmailVerificationStep()}
        {currentStep === 'complete' && renderCompleteStep()}
      </div>
    </div>
  )
}

export default AuthenticationFlow
