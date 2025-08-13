import { useState, useCallback, useEffect } from 'react';
import { apiService } from './api';
import toast from 'react-hot-toast';

export interface AnalysisSession {
  session_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  results?: any;
  error?: string;
  created_at: string;
  analysis_type: string;
  url: string;
}

export const useAnalysis = () => {
  const [currentSession, setCurrentSession] = useState<AnalysisSession | null>(null);
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Start new analysis
  const startAnalysis = useCallback(async (url: string, analysisType: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.analysis.start(url, analysisType);
      
      if (response.success) {
        const session: AnalysisSession = {
          session_id: response.session_id,
          status: 'pending',
          progress: 0,
          analysis_type: analysisType,
          url: url,
          created_at: new Date().toISOString(),
        };
        
        setCurrentSession(session);
        toast.success('Analysis started successfully!');
        
        // Start polling for status updates
        pollStatus(response.session_id);
        
        return response.session_id;
      } else {
        throw new Error(response.error || 'Failed to start analysis');
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || error.message || 'Failed to start analysis';
      setError(errorMessage);
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Poll analysis status
  const pollStatus = useCallback(async (sessionId: string) => {
    let pollCount = 0;
    const maxPolls = 120; // 10 minutes max (5 second intervals)

    const poll = async () => {
      try {
        const response = await apiService.analysis.getStatus(sessionId);
        
        if (response.success) {
          const updatedSession: AnalysisSession = {
            session_id: sessionId,
            status: response.status,
            progress: response.progress || 0,
            analysis_type: response.analysis_type || '',
            url: response.url || '',
            created_at: response.created_at || new Date().toISOString(),
          };

          setCurrentSession(updatedSession);

          if (response.status === 'completed') {
            // Fetch results
            const resultsResponse = await apiService.analysis.getResults(sessionId);
            if (resultsResponse.success) {
              updatedSession.results = resultsResponse.results;
              setCurrentSession(updatedSession);
              toast.success('Analysis completed successfully!');
            }
            return; // Stop polling
          } else if (response.status === 'failed') {
            setError(response.error || 'Analysis failed');
            toast.error('Analysis failed. Please try again.');
            return; // Stop polling
          } else {
            // Continue polling if still processing
            pollCount++;
            if (pollCount < maxPolls) {
              setTimeout(poll, 5000); // Poll every 5 seconds
            } else {
              setError('Analysis timeout. Please try again.');
              toast.error('Analysis took too long. Please try again.');
            }
          }
        }
      } catch (error: any) {
        console.error('Polling error:', error);
        pollCount++;
        if (pollCount < maxPolls) {
          setTimeout(poll, 5000); // Continue polling despite errors
        } else {
          setError('Connection error during analysis');
          toast.error('Connection error. Please check your internet connection.');
        }
      }
    };

    // Start polling with initial delay
    setTimeout(poll, 2000);
  }, []);

  // Get analysis history
  const loadHistory = useCallback(async () => {
    try {
      const response = await apiService.analysis.getHistory();
      if (response.success) {
        setAnalysisHistory(response.sessions || []);
      }
    } catch (error: any) {
      console.error('Error loading history:', error);
      toast.error('Failed to load analysis history');
    }
  }, []);

  // Delete analysis
  const deleteAnalysis = useCallback(async (sessionId: string) => {
    try {
      const response = await apiService.analysis.delete(sessionId);
      if (response.success) {
        setAnalysisHistory(prev => prev.filter(session => session.session_id !== sessionId));
        if (currentSession?.session_id === sessionId) {
          setCurrentSession(null);
        }
        toast.success('Analysis deleted successfully');
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Failed to delete analysis';
      toast.error(errorMessage);
    }
  }, [currentSession]);

  // Clear current session
  const clearSession = useCallback(() => {
    setCurrentSession(null);
    setError(null);
  }, []);

  return {
    currentSession,
    analysisHistory,
    isLoading,
    error,
    startAnalysis,
    loadHistory,
    deleteAnalysis,
    clearSession,
  };
};
