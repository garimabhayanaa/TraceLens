import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { auth } from './firebase';
import toast from 'react-hot-toast';
import toast from 'react-hot-toast';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes timeout for analysis requests
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor to add Firebase token to all requests
apiClient.interceptors.request.use(
  async (config) => {
    try {
      const user = auth.currentUser;
      if (user) {
        const token = await user.getIdToken(true); // Force refresh token
        config.headers.Authorization = `Bearer ${token}`;
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
      } else {
        console.warn('No authenticated user found for API request');
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
      } else {
        console.warn('No authenticated user found for API request');
      }
    } catch (error) {
      console.error('Error getting Firebase token:', error);
      toast.error('Authentication error. Please sign in again.');
      toast.error('Authentication error. Please sign in again.');
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
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
  (response: AxiosResponse) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    if (error.response) {
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Token expired or invalid - redirect to login
          toast.error('Session expired. Please sign in again.');
          window.location.href = '/login';
          break;
        case 403:
          // Forbidden - access denied
          toast.error('Access denied. Please check your permissions.');
          break;
        case 404:
          // Not found
          toast.error('Resource not found.');
          break;
        case 429:
          // Rate limit exceeded
          const rateLimitMessage = data?.error || 'Rate limit exceeded. Please wait before trying again.';
          toast.error(rateLimitMessage);
          break;
        case 500:
        case 502:
        case 503:
        case 504:
          // Server errors
          toast.error('Server error. Please try again later.');
          break;
        default:
          // Other HTTP errors
          const errorMessage = data?.error || data?.message || 'An error occurred';
          toast.error(errorMessage);
      }
    } else if (error.code === 'ECONNABORTED') {
      // Timeout error
      toast.error('Request timeout. Please check your connection and try again.');
    } else if (error.code === 'ERR_NETWORK') {
      // Network error
      toast.error('Network error. Please check your internet connection.');
    } else {
      // Unknown error
      toast.error('An unexpected error occurred. Please try again.');
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

        // Clean and validate URL
        const cleanUrl = url.trim();
        if (!cleanUrl.startsWith('http://') && !cleanUrl.startsWith('https://')) {
          throw new Error('URL must start with http:// or https://');
        }
        
        const requestData = {
          url: cleanUrl, // Backend accepts 'url' parameter
          analysis_type: analysisType.trim(),
        };
        
        console.log('Sending analysis request with data:', requestData);
        
        const response = await apiClient.post('/api/analysis/start', requestData);
        
        console.log('Analysis start response:', response.data);
        
        if (response.data.success) {
          return response.data;
        } else {
          throw new Error(response.data.error || 'Failed to start analysis');
        }
      } catch (error: any) {
        console.error('Analysis start error:', error);
        
        if (error.response?.data) {
          const errorData = error.response.data;
          // Handle specific error cases from backend
          if (errorData.supported_platforms) {
            const errorMessage = `${errorData.error}: ${errorData.message}\n\nSupported platforms:\n${errorData.supported_platforms.join(', ')}`;
            throw new Error(errorMessage);
          } else {
            throw new Error(errorData.error || errorData.message || 'Failed to start analysis');
          }
        } else {
          throw new Error(error.message || 'Failed to start analysis');
        }
      }
    },

    // Get analysis status
    getStatus: async (sessionId: string) => {
      try {
        if (!sessionId) {
          throw new Error('Session ID is required');
        }
        
        const response = await apiClient.get(`/api/analysis/status/${sessionId}`);
        
        if (response.data.success) {
          return response.data;
        } else {
          throw new Error(response.data.error || 'Failed to get analysis status');
        }
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
        
        if (response.data.success) {
          return response.data;
        } else {
          throw new Error(response.data.error || 'Failed to get analysis results');
        }
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
        
        if (response.data.success) {
          return response.data;
        } else {
          throw new Error(response.data.error || 'Failed to get analysis history');
        }
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
        
        if (response.data.success) {
          return response.data;
        } else {
          throw new Error(response.data.error || 'Failed to delete analysis');
        }
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

  // Utility functions
  utils: {
    // Test backend connection
    testConnection: async () => {
      try {
        const response = await apiService.healthCheck();
        return {
          success: true,
          status: response.status,
          service: response.service,
          firebase: response.firebase
        };
      } catch (error) {
        return {
          success: false,
          error: 'Failed to connect to backend'
        };
      }
    },

    // Validate URL before sending to backend
    validateUrl: (url: string) => {
      const supportedPlatforms = [
        'twitter.com', 'x.com', 'linkedin.com', 'github.com',
        'instagram.com', 'facebook.com', 'tiktok.com', 'youtube.com'
      ];

      if (!url || !url.trim()) {
        return { isValid: false, error: 'URL is required' };
      }

      const cleanUrl = url.trim();
      
      if (!cleanUrl.startsWith('http://') && !cleanUrl.startsWith('https://')) {
        return { isValid: false, error: 'URL must start with http:// or https://' };
      }

      const containsSupportedPlatform = supportedPlatforms.some(platform => 
        cleanUrl.toLowerCase().includes(platform)
      );

      if (!containsSupportedPlatform) {
        return { 
          isValid: false, 
          error: 'URL must be from a supported social media platform',
          supportedPlatforms 
        };
      }

      return { isValid: true, cleanUrl };
    },

    // Get current authentication status
    getAuthStatus: async () => {
      try {
        const user = auth.currentUser;
        if (!user) {
          return { authenticated: false };
        }

        const token = await user.getIdToken();
        return {
          authenticated: true,
          userId: user.uid,
          email: user.email,
          emailVerified: user.emailVerified,
          tokenExpiry: new Date(Date.now() + 3600000) // 1 hour from now
        };
      } catch (error) {
        console.error('Auth status check failed:', error);
        return { authenticated: false, error: 'Failed to check authentication status' };
      }
    }
  }
};

// Export individual functions for convenience
export const {
  healthCheck,
  user: userService,
  analysis: analysisService,
  utils: utilityService
} = apiService;

export default apiService;
