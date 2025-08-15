'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAnalysis } from '@/lib/useAnalysis';
import { useAuth } from '@/lib/auth-context';
import toast from 'react-hot-toast';
import { 
  Play, 
  Trash2, 
  Clock, 
  Shield, 
  Heart, 
  DollarSign, 
  Calendar,
  Globe,
  Lock,
  CheckCircle,
  XCircle,
  AlertTriangle
} from 'lucide-react';

const AnalysisDashboard: React.FC = () => {
  const { user, traceLensUser } = useAuth();
  const {
    currentSession,
    analysisHistory,
    isLoading,
    error,
    startAnalysis,
    loadHistory,
    deleteAnalysis,
    clearSession
  } = useAnalysis();

  const [url, setUrl] = useState('');
  const [analysisType, setAnalysisType] = useState('comprehensive');
  const [urlError, setUrlError] = useState('');

  // Load history on component mount
  useEffect(() => {
    if (user) {
      loadHistory();
    }
  }, [user, loadHistory]);

  // Validate URL
  const validateUrl = (inputUrl: string) => {
    const urlPattern = /^https?:\/\/.+/;
    if (!urlPattern.test(inputUrl)) {
      return 'Please enter a valid URL starting with http:// or https://';
    }
    return '';
  };

  // Handle analysis start
  const handleStartAnalysis = async () => {
    const error = validateUrl(url);
    if (error) {
      setUrlError(error);
      return;
    }

    if (!traceLensUser) {
      toast.error('User profile not loaded. Please refresh the page.');
      return;
    }

    // Check daily usage limit
    if (traceLensUser.subscriptionTier === 'free' && traceLensUser.dailyUsage >= 3) {
      toast.error('Daily analysis limit reached. Upgrade to continue.');
      return;
    }

    setUrlError('');
    try {
      await startAnalysis(url, analysisType);
      setUrl(''); // Clear input after successful start
    } catch (error) {
      // Error handling is done in the hook
    }
  };

  // Handle analysis deletion
  const handleDeleteAnalysis = async (sessionId: string) => {
    if (window.confirm('Are you sure you want to delete this analysis? This action cannot be undone.')) {
      await deleteAnalysis(sessionId);
    }
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'processing':
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-500" />;
    }
  };

  // Render analysis results
  const renderResults = (results: any) => {
    if (!results) return null;

    return (
      <Tabs defaultValue="privacy" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="privacy">Privacy</TabsTrigger>
        </TabsList>
        <TabsContent value="privacy" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Privacy Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium">Privacy Score</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {results.privacy_analysis?.privacy_score || 'N/A'}/100
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium">Data Exposure</p>
                  <p className="text-lg font-semibold">
                    {results.privacy_analysis?.data_exposure_level || 'Unknown'}
                  </p>
                </div>
              </div>
              {results.privacy_analysis?.recommendations && (
                <div className="mt-4">
                  <p className="text-sm font-medium mb-2">Recommendations:</p>
                  <ul className="text-sm space-y-1">
                    {results.privacy_analysis.recommendations.map((rec: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-blue-500">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    );
  };

  return (
    <div className="space-y-6">
      {/* Analysis Input Section */}
      <Card>
        <CardHeader>
          <CardTitle>Start New Analysis</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Input
              placeholder="Enter a social media profile URL, Medium article, news site, public blog, or any public webpage URL"
              value={url}
              onChange={(e) => {
                setUrl(e.target.value);
                if (urlError) setUrlError('');
              }}
              className={urlError ? 'border-red-500' : ''}
            />
            {urlError && (
              <p className="text-red-500 text-sm mt-1">{urlError}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Analysis Type</label>
            <select
              value="privacy_only"
              disabled
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="privacy_only">Privacy Only</option>
            </select>
          </div>

          <div className="flex items-center justify-between">
            <Button 
              onClick={handleStartAnalysis}
              disabled={isLoading || !url.trim()}
              className="flex items-center gap-2"
            >
              <Play className="h-4 w-4" />
              {isLoading ? 'Starting...' : 'Start Analysis'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Current Analysis Progress */}
      {currentSession && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Current Analysis</span>
              <div className="flex items-center gap-2">
                {getStatusIcon(currentSession.status)}
                <span className="text-sm capitalize">{currentSession.status}</span>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-gray-600">URL: {currentSession.url}</p>
              <p className="text-sm text-gray-600">Type: {currentSession.analysis_type}</p>
            </div>

            {currentSession.status === 'processing' && (
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Progress</span>
                  <span className="text-sm">{currentSession.progress}%</span>
                </div>
                <Progress value={currentSession.progress} className="h-2" />
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-3">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}

            {currentSession.status === 'completed' && currentSession.results && (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Analysis Results</h3>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDeleteAnalysis(currentSession.session_id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
                {renderResults(currentSession.results)}
              </div>
            )}

            <div className="flex gap-2">
              <Button variant="outline" onClick={clearSession}>
                Clear Session
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analysis History */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis History</CardTitle>
        </CardHeader>
        <CardContent>
          {analysisHistory.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No analysis history found.</p>
          ) : (
            <div className="space-y-3">
              {analysisHistory.map((session) => (
                <div
                  key={session.session_id}
                  className="flex items-center justify-between p-3 border border-gray-200 rounded-md"
                >
                  <div className="flex-1">
                    <p className="font-medium truncate">{session.url}</p>
                    <p className="text-sm text-gray-600">
                      {session.analysis_type} • {new Date(session.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    {getStatusIcon(session.status)}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteAnalysis(session.session_id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AnalysisDashboard;
