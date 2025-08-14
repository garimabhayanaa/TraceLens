import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { auth } from './firebase';
import toast from 'react-hot-toast';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds timeout for analysis requests
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor to add Firebase token to all requests
apiClient.interceptors.request.use(
  async (config) => {
    try {
      const user = auth.currentUser;
      if (user) {
        const token = await user.getIdToken();
        config.headers.Authorization = `Bearer ${token}`;
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
      } else {
        console.warn('No authenticated user found for API request');
      }
    } catch (error) {
      console.error('Error getting Firebase token:', error);
      toast.error('Authentication error. Please sign in again.');
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    if (error.response?.status === 401) {
      // Token expired or invalid - redirect to login
      toast.error('Session expired. Please sign in again.');
      window.location.href = '/login';
    } else if (error.response?.status === 429) {
      // Rate limit exceeded
      toast.error('Rate limit exceeded. Please wait before trying again.');
    } else if (error.response?.status >= 500) {
      // Server error
      toast.error('Server error. Please try again later.');
    } else if (error.code === 'ECONNABORTED') {
      // Timeout error
      toast.error('Request timeout. Please check your connection and try again.');
    } else if (error.code === 'ERR_NETWORK') {
      // Network error
      toast.error('Network error. Please check your internet connection.');
    }
    
    return Promise.reject(error);
  }
);

// API Service Functions
export const apiService = {
  // Health check
  healthCheck: async () => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },

  // User profile endpoints
  user: {
    // Get user profile
    getProfile: async () => {
      try {
        const response = await apiClient.get('/api/user/profile');
        return response.data;
      } catch (error) {
        console.error('Failed to get user profile:', error);
        throw error;
      }
    },

    // Update user profile
    updateProfile: async (profileData: any) => {
      try {
        const response = await apiClient.put('/api/user/profile', profileData);
        return response.data;
      } catch (error) {
        console.error('Failed to update user profile:', error);
        throw error;
      }
    },
  },

  // Analysis endpoints
  analysis: {
    // Start new analysis
    start: async (url: string, analysisType: string) => {
      try {
        console.log('Starting analysis request:', { url, analysisType });
        
        // Validate inputs before sending
        if (!url || !url.trim()) {
          throw new Error('URL is required');
        }
        
        if (!analysisType || !analysisType.trim()) {
          throw new Error('Analysis type is required');
        }
        
        const requestData = {
          url: url.trim(),
          analysis_type: analysisType.trim(),
        };
        
        console.log('Sending analysis request with data:', requestData);
        
        const response = await apiClient.post('/api/analysis/start', requestData);
        
        console.log('Analysis start response:', response.data);
        return response.data;
      } catch (error: any) {
        console.error('Analysis start error:', error);
        const errorMessage = error.response?.data?.error || error.message || 'Failed to start analysis';
        throw new Error(errorMessage);
      }
    },

    // Get analysis status
    getStatus: async (sessionId: string) => {
      try {
        if (!sessionId) {
          throw new Error('Session ID is required');
        }
        
        const response = await apiClient.get(`/api/analysis/status/${sessionId}`);
        return response.data;
      } catch (error: any) {
        console.error('Failed to get analysis status:', error);
        const errorMessage = error.response?.data?.error || error.message || 'Failed to get analysis status';
        throw new Error(errorMessage);
      }
    },

    // Get analysis results
    getResults: async (sessionId: string) => {
      try {
        if (!sessionId) {
          throw new Error('Session ID is required');
        }
        
        const response = await apiClient.get(`/api/analysis/results/${sessionId}`);
        return response.data;
      } catch (error: any) {
        console.error('Failed to get analysis results:', error);
        const errorMessage = error.response?.data?.error || error.message || 'Failed to get analysis results';
        throw new Error(errorMessage);
      }
    },

    // Get analysis history
    getHistory: async (limit: number = 10) => {
      try {
        const response = await apiClient.get(`/api/analysis/history?limit=${limit}`);
        return response.data;
      } catch (error: any) {
        console.error('Failed to get analysis history:', error);
        const errorMessage = error.response?.data?.error || error.message || 'Failed to get analysis history';
        throw new Error(errorMessage);
      }
    },

    // Delete analysis
    delete: async (sessionId: string) => {
      try {
        if (!sessionId) {
          throw new Error('Session ID is required');
        }
        
        const response = await apiClient.delete(`/api/analysis/delete/${sessionId}`);
        return response.data;
      } catch (error: any) {
        console.error('Failed to delete analysis:', error);
        const errorMessage = error.response?.data?.error || error.message || 'Failed to delete analysis';
        throw new Error(errorMessage);
      }
    },

    // Debug endpoint for testing
    debug: async (testData: any) => {
      try {
        const response = await apiClient.post('/api/analysis/debug', testData);
        return response.data;
      } catch (error: any) {
        console.error('Debug request failed:', error);
        throw error;
      }
    },
  },
};

// Export individual functions for convenience
export const {
  healthCheck,
  user: userService,
  analysis: analysisService,
} = apiService;

export default apiService;
