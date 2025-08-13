import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { auth } from './firebase';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
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
      }
    } catch (error) {
      console.error('Error getting Firebase token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Service Functions
export const apiService = {
  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // User profile
  getUserProfile: async () => {
    const response = await apiClient.get('/api/user/profile');
    return response.data;
  },

  // Analysis endpoints
  analysis: {
    // Start new analysis
    start: async (url: string, analysisType: string) => {
      const response = await apiClient.post('/api/analysis/start', {
        url,
        analysis_type: analysisType,
      });
      return response.data;
    },

    // Get analysis status
    getStatus: async (sessionId: string) => {
      const response = await apiClient.get(`/api/analysis/status/${sessionId}`);
      return response.data;
    },

    // Get analysis results
    getResults: async (sessionId: string) => {
      const response = await apiClient.get(`/api/analysis/results/${sessionId}`);
      return response.data;
    },

    // Get analysis history
    getHistory: async () => {
      const response = await apiClient.get('/api/analysis/history');
      return response.data;
    },

    // Delete analysis
    delete: async (sessionId: string) => {
      const response = await apiClient.delete(`/api/analysis/delete/${sessionId}`);
      return response.data;
    },
  },
};

export default apiService;
