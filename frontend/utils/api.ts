import axios, { AxiosResponse, AxiosError } from 'axios'
import toast from 'react-hot-toast'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/auth'
    }
    return Promise.reject(error)
  }
)

// Get client IP address
export const getClientIP = async (): Promise<string> => {
  try {
    const response = await fetch('https://api.ipify.org?format=json')
    const data = await response.json()
    return data.ip
  } catch (error) {
    return '0.0.0.0'
  }
}

// API interfaces
export interface UserRegistrationData {
  email: string
  password: string
  confirmPassword?: string
  recaptcha_token: string
}

export interface EmailVerificationData {
  verification_id: string
  verification_code: string
  user_id: string
}

export interface AnalysisRequestData {
  social_data: any
  user_id: string
  user_email: string
  analysis_type: string
  target_data_description: string
  use_case_description: string
  age_verification_data: any
  consent_process_id: string
  session_id?: string
  privacy_level?: string
  recaptcha_response?: string
  verification_code?: string
  verification_id?: string
}

export interface AnalysisResults {
  analysis_approved: boolean
  sentiment_analysis: any
  hashtag_patterns: any
  engagement_analysis: any
  topic_modeling: any
  schedule_patterns: any
  economic_indicators: any
  mental_state_assessment: any
  interest_profile: any
  abuse_prevention_status: any
  legal_ethical_compliance: any
  privacy_metrics: any
  usage_statistics: any
  analysis_metadata: any
}

// API functions
export const authAPI = {
  register: async (data: UserRegistrationData) => {
    const clientIP = await getClientIP()
    return api.post('/api/register', {
      ...data,
      ip_address: clientIP,
      user_agent: navigator.userAgent
    })
  },

  verifyEmail: async (data: EmailVerificationData) => {
    const clientIP = await getClientIP()
    return api.post('/api/verify-email', {
      ...data,
      ip_address: clientIP
    })
  },

  login: async (email: string, password: string) => {
    const clientIP = await getClientIP()
    return api.post('/api/login', {
      email,
      password,
      ip_address: clientIP,
      user_agent: navigator.userAgent
    })
  },

  initiateEmailVerification: async (userId: string, email: string) => {
    const clientIP = await getClientIP()
    return api.post('/api/initiate-email-verification', {
      user_id: userId,
      email: email,
      ip_address: clientIP,
      user_agent: navigator.userAgent
    })
  }
}

export const analysisAPI = {
  performAnalysis: async (data: AnalysisRequestData) => {
    const clientIP = await getClientIP()
    return api.post('/api/analyze', {
      ...data,
      ip_address: clientIP,
      user_agent: navigator.userAgent
    })
  },

  getAnalysisStatus: async (sessionId: string) => {
    return api.get(`/api/analysis-status/${sessionId}`)
  },

  requestImmediateDeletion: async (userId: string, deletionScope: string = 'complete') => {
    return api.post('/api/request-immediate-deletion', {
      user_id: userId,
      deletion_scope: deletionScope
    })
  },

  executeDeletion: async (requestId: string, verificationCode: string) => {
    return api.post('/api/execute-deletion', {
      request_id: requestId,
      verification_code: verificationCode
    })
  },

  requestOptOut: async (userId: string, sessionId: string, currentStage: string, reason?: string) => {
    return api.post('/api/request-opt-out', {
      user_id: userId,
      session_id: sessionId,
      current_stage: currentStage,
      reason: reason
    })
  },

  withdrawConsent: async (userId: string, consentType: string, reason?: string) => {
    return api.post('/api/withdraw-consent', {
      user_id: userId,
      consent_type: consentType,
      reason: reason
    })
  }
}

export const consentAPI = {
  initiateConsentProcess: async (userId: string, sessionId: string) => {
    const clientIP = await getClientIP()
    return api.post('/api/initiate-consent-process', {
      user_id: userId,
      session_id: sessionId,
      ip_address: clientIP,
      user_agent: navigator.userAgent
    })
  },

  processConsentStep: async (processId: string, consentType: string, granted: boolean) => {
    const clientIP = await getClientIP()
    return api.post('/api/process-consent-step', {
      process_id: processId,
      consent_type: consentType,
      granted: granted,
      ip_address: clientIP,
      user_agent: navigator.userAgent
    })
  }
}

export const reportingAPI = {
  submitAbuseReport: async (reportData: any) => {
    return api.post('/api/submit-abuse-report', reportData)
  },

  getReportStatus: async (reportId: string) => {
    return api.get(`/api/report-status/${reportId}`)
  }
}

export const statusAPI = {
    getComprehensiveStatus: async () => {
        return api.get('/api/comprehensive-status')
    },

    getPrivacyStatus: async () => {
        return api.get('/api/privacy-status')
    },

    getTransparencyReport: async () => {
        return api.get('/api/transparency-report')
    }
}

export default api

