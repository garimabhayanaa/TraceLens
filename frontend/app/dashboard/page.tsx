'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import AnalysisDashboard from '@/components/dashboard/AnalysisDashboard';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ROUTES } from '@/lib/routes';
import { LogOut, User, Settings, Shield, Home } from 'lucide-react';
import toast from 'react-hot-toast';

const DashboardPage = () => {
  const { user, traceLensUser, loading, logout, retryConnection, firestoreError } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push(ROUTES.LOGIN);
    }
  }, [user, loading, router]);

  const handleSignOut = async () => {
    try {
      await logout();
      toast.success('Signed out successfully!');
      router.push(ROUTES.HOME);
    } catch (error) {
      toast.error('Error signing out. Please try again.');
      console.error('Sign out error:', error);
    }
  };

  const handleRetryConnection = async () => {
    try {
      await retryConnection();
    } catch (error) {
      console.error('Retry connection error:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Navigation */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-blue-600">TraceLens</h1>
            </div>
            <div className="hidden md:flex items-center space-x-2 text-gray-500">
              <span>/</span>
              <span>Dashboard</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* User Info */}
            <div className="hidden md:flex items-center space-x-2 text-sm">
              <User className="h-4 w-4 text-gray-500" />
              <span className="text-gray-700 max-w-32 truncate">
                {user.displayName || user.email}
              </span>
            </div>
            
            {/* Connection Status */}
            {firestoreError && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleRetryConnection}
                className="text-orange-600 border-orange-200 hover:bg-orange-50"
              >
                Retry Connection
              </Button>
            )}
            
            {/* Navigation Buttons */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push(ROUTES.HOME)}
              className="hidden md:flex items-center space-x-2"
            >
              <Home className="h-4 w-4" />
              <span>Home</span>
            </Button>
            
            {/* Sign Out Button */}
            <Button
              variant="outline"
              onClick={handleSignOut}
              className="flex items-center space-x-2 hover:bg-red-50 hover:border-red-200 hover:text-red-600 transition-colors"
            >
              <LogOut className="h-4 w-4" />
              <span>Sign Out</span>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto py-6 space-y-6 px-4">
        {/* Connection Error Banner */}
        {firestoreError && (
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="h-2 w-2 bg-orange-500 rounded-full"></div>
                <span className="text-orange-800 font-medium">Connection Issue</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRetryConnection}
                className="text-orange-600 border-orange-300"
              >
                Retry
              </Button>
            </div>
            <p className="text-orange-700 text-sm mt-1">{firestoreError}</p>
          </div>
        )}

        {/* User Welcome Section */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="flex items-center space-x-2">
                <span>Welcome back, {user.displayName || 'User'}!</span>
              </CardTitle>
              <Button variant="ghost" size="sm" className="flex items-center space-x-2">
                <Settings className="h-4 w-4" />
                <span className="hidden md:inline">Settings</span>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-semibold truncate">{user.email}</p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-gray-600">Account Status</p>
                <p className="font-semibold">
                  {user.emailVerified ? '✅ Verified' : '⚠️ Unverified'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* System Status Section */}
        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`flex items-center justify-between p-3 rounded-lg ${
                firestoreError ? 'bg-orange-50' : 'bg-green-50'
              }`}>
                <div>
                  <p className={`font-medium ${
                    firestoreError ? 'text-orange-800' : 'text-green-800'
                  }`}>
                    Firebase Connection
                  </p>
                  <p className={`text-sm ${
                    firestoreError ? 'text-orange-600' : 'text-green-600'
                  }`}>
                    {firestoreError ? 'Connection Issue' : 'Connected & Authenticated'}
                  </p>
                </div>
                <div className={`h-3 w-3 rounded-full ${
                  firestoreError ? 'bg-orange-500' : 'bg-green-500'
                }`}></div>
              </div>
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <div>
                  <p className="font-medium text-blue-800">Analysis Engine</p>
                  <p className="text-sm text-blue-600">Ready for Analysis</p>
                </div>
                <div className="h-3 w-3 bg-blue-500 rounded-full"></div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions Section */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Quick Actions</CardTitle>
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push(ROUTES.HOME)}
                className="text-blue-600 hover:bg-blue-50"
              >
                Back to Home
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <a href="#start_analysis">
                    <div className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                        <h3 className="font-medium text-gray-800 mb-2">🔍 Start Analysis</h3>
                        <p className="text-sm text-gray-600">
                            Analyze any social media profile for privacy insights and digital footprint assessment.
                        </p>
                    </div>
                </a>
              <a href='/privacy_guide'>
                 <div className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                    <h3 className="font-medium text-gray-800 mb-2">🛡️ Privacy Guide</h3>
                    <p className="text-sm text-gray-600">
                        Learn practical tips to improve your digital privacy and reduce your online footprint.
                    </p>
                </div>
              </a>
            </div>
          </CardContent>
        </Card>

        {/* Main Analysis Dashboard */}
        <div id="start_analysis">
            <AnalysisDashboard />
        </div>

        {/* Footer Information */}
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-sm text-gray-500 space-y-2">
              <p>Your privacy is our priority. All analysis data is automatically deleted after 24 hours.</p>
              <div className="flex justify-center space-x-4 mt-4">
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                  GDPR Compliant
                </span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                  Privacy First
                </span>
                <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                  AI Powered
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default DashboardPage;
