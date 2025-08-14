import { useState, useCallback, useEffect, useRef } from 'react';
import { apiService } from './api';
import toast from 'react-hot-toast';

export interface AnalysisSession {
  session_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  results?: any;
  error?: string;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
  analysis_type: string;
  url: string;
  processing_steps?: Array<{
    step: string;
    timestamp: string;
    progress: number;
  }>;
  has_results?: boolean;
  error_message?: string;
}

export interface AnalysisResults {
  privacy_analysis?: {
    privacy_score: number;
    data_exposure_level: string;
    recommendations: string[];
    risk_factors: string[];
  };
  sentiment_analysis?: {
    overall_sentiment: string;
    confidence: number;
    trending_topics: string[];
    emotional_indicators: string[];
  };
  economic_indicators?: {
    income_level: string;
    economic_risk_score: number;
    brand_mentions: string[];
    lifestyle_indicators: string[];
  };
  schedule_patterns?: {
    most_active_time: string;
    activity_pattern: string;
    posting_frequency: string;
    timezone_analysis: string;
  };
  cross_platform_correlation?: {
    linked_platforms: string[];
    consistency_score: number;
    identity_verification: string;
  };
}

export const useAnalysis = () => {
  const [currentSession, setCurrentSession] = useState<AnalysisSession | null>(null);
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  // Refs for cleanup
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const maxPollAttemptsRef = useRef(0);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  // Start new analysis
  const startAnalysis = useCallback(async (url: string, analysisType: string) => {
    setIsLoading(true);
    setError(null);
    
    console.log('Starting analysis with:', { url, analysisType });
    
    try {
      // Validate inputs
      if (!url || !url.trim()) {
        throw new Error('URL is required');
      }
      
      if (!analysisType || !analysisType.trim()) {
        throw new Error('Analysis type is required');
      }
      
      const response = await apiService.analysis.start(url, analysisType);
      console.log('Analysis start response:', response);
      
      if (response.success && response.session_id) {
        const session: AnalysisSession = {
          session_id: response.session_id,
          status: 'pending',
          progress: 0,
          analysis_type: analysisType,
          url: url,
          created_at: new Date().toISOString(),
        };
        
        setCurrentSession(session);
        toast.success('Analysis started successfully! 🚀');
        
        // Start polling for status updates
        startPolling(response.session_id);
        
        return response.session_id;
      } else {
        throw new Error(response.error || 'Failed to start analysis');
      }
    } catch (error: any) {
      console.error('Analysis start error:', error);
      const errorMessage = error.message || 'Failed to start analysis';
      setError(errorMessage);
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Start polling for status updates
  const startPolling = useCallback((sessionId: string) => {
    console.log('Starting polling for session:', sessionId);
    setIsPolling(true);
    maxPollAttemptsRef.current = 0;
    
    // Clear any existing polling
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }
    
    const poll = async () => {
      try {
        maxPollAttemptsRef.current += 1;
        console.log(`Polling attempt ${maxPollAttemptsRef.current} for session:`, sessionId);
        
        const response = await apiService.analysis.getStatus(sessionId);
        
        if (response.success) {
          const updatedSession: AnalysisSession = {
            session_id: sessionId,
            status: response.status,
            progress: response.progress || 0,
            analysis_type: response.analysis_type || '',
            url: response.url || '',
            created_at: response.created_at || new Date().toISOString(),
            updated_at: response.updated_at,
            processing_steps: response.processing_steps || [],
          };

          setCurrentSession(updatedSession);
          console.log('Session status updated:', updatedSession);

          if (response.status === 'completed') {
            console.log('Analysis completed, fetching results...');
            
            try {
              // Fetch results
              const resultsResponse = await apiService.analysis.getResults(sessionId);
              if (resultsResponse.success && resultsResponse.results) {
                updatedSession.results = resultsResponse.results;
                updatedSession.completed_at = resultsResponse.completed_at;
                setCurrentSession(updatedSession);
                toast.success('Analysis completed successfully! ✅');
              } else {
                console.error('Failed to fetch results:', resultsResponse.error);
                toast.error('Analysis completed but failed to fetch results');
              }
            } catch (resultError) {
              console.error('Error fetching results:', resultError);
              toast.error('Analysis completed but failed to fetch results');
            }
            
            // Stop polling
            stopPolling();
            return;
          } else if (response.status === 'failed') {
            console.error('Analysis failed:', response.error);
            setError(response.error || 'Analysis failed');
            updatedSession.error = response.error;
            updatedSession.error_message = response.error;
            setCurrentSession(updatedSession);
            toast.error(`Analysis failed: ${response.error || 'Unknown error'}`);
            stopPolling();
            return;
          }
          
          // Continue polling if still processing
          if (maxPollAttemptsRef.current >= 240) { // 20 minutes max (5 second intervals)
            console.warn('Polling timeout reached for session:', sessionId);
            setError('Analysis timeout. Please try again.');
            toast.error('Analysis took too long. Please try again.');
            stopPolling();
          }
        } else {
          console.error('Status check failed:', response.error);
          if (maxPollAttemptsRef.current >= 5) {
            setError('Failed to check analysis status');
            toast.error('Failed to check analysis status');
            stopPolling();
          }
        }
      } catch (error: any) {
        console.error('Polling error:', error);
        if (maxPollAttemptsRef.current >= 5) {
          setError('Connection error during analysis');
          toast.error('Connection error. Please check your internet connection.');
          stopPolling();
        }
      }
    };

    // Initial status check after 2 seconds
    setTimeout(poll, 2000);
    
    // Set up interval polling every 5 seconds
    pollingIntervalRef.current = setInterval(poll, 5000);
  }, []);

  // Stop polling
  const stopPolling = useCallback(() => {
    console.log('Stopping polling');
    setIsPolling(false);
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  }, []);

  // Get analysis history
  const loadHistory = useCallback(async (limit: number = 10) => {
    try {
      console.log('Loading analysis history...');
      const response = await apiService.analysis.getHistory(limit);
      
      if (response.success && response.sessions) {
        setAnalysisHistory(response.sessions);
        console.log(`Loaded ${response.sessions.length} analysis sessions`);
      } else {
        console.error('Failed to load history:', response.error);
        toast.error('Failed to load analysis history');
      }
    } catch (error: any) {
      console.error('Error loading history:', error);
      const errorMessage = error.message || 'Failed to load analysis history';
      toast.error(errorMessage);
    }
  }, []);

  // Delete analysis
  const deleteAnalysis = useCallback(async (sessionId: string) => {
    try {
      console.log('Deleting analysis session:', sessionId);
      const response = await apiService.analysis.delete(sessionId);
      
      if (response.success) {
        // Remove from history
        setAnalysisHistory(prev => prev.filter(session => session.session_id !== sessionId));
        
        // Clear current session if it's the one being deleted
        if (currentSession?.session_id === sessionId) {
          setCurrentSession(null);
          stopPolling();
        }
        
        toast.success('Analysis deleted successfully 🗑️');
      } else {
        throw new Error(response.error || 'Failed to delete analysis');
      }
    } catch (error: any) {
      console.error('Delete analysis error:', error);
      const errorMessage = error.message || 'Failed to delete analysis';
      toast.error(errorMessage);
    }
  }, [currentSession, stopPolling]);

  // Clear current session
  const clearSession = useCallback(() => {
    console.log('Clearing current session');
    setCurrentSession(null);
    setError(null);
    stopPolling();
  }, [stopPolling]);

  // Retry failed analysis
  const retryAnalysis = useCallback(async (sessionId: string) => {
    try {
      const session = analysisHistory.find(s => s.session_id === sessionId);
      if (session) {
        await startAnalysis(session.url, session.analysis_type);
      } else {
        throw new Error('Session not found in history');
      }
    } catch (error: any) {
      console.error('Retry analysis error:', error);
      toast.error('Failed to retry analysis');
    }
  }, [analysisHistory, startAnalysis]);

  // Get analysis by ID
  const getAnalysisById = useCallback((sessionId: string): AnalysisSession | null => {
    if (currentSession?.session_id === sessionId) {
      return currentSession;
    }
    return analysisHistory.find(session => session.session_id === sessionId) || null;
  }, [currentSession, analysisHistory]);

  // Check if user can start new analysis (rate limiting)
  const canStartAnalysis = useCallback(() => {
    // Simple client-side rate limiting check
    const recentSessions = analysisHistory.filter(session => {
      const sessionTime = new Date(session.created_at).getTime();
      const hourAgo = Date.now() - (60 * 60 * 1000);
      return sessionTime > hourAgo;
    });
    
    return recentSessions.length < 3; // Max 3 per hour for free tier
  }, [analysisHistory]);

  return {
    // State
    currentSession,
    analysisHistory,
    isLoading,
    error,
    isPolling,
    
    // Actions
    startAnalysis,
    loadHistory,
    deleteAnalysis,
    clearSession,
    retryAnalysis,
    stopPolling,
    
    // Utilities
    getAnalysisById,
    canStartAnalysis,
  };
};

export default useAnalysis;
