'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import AnalysisDashboard from '@/components/dashboard/AnalysisDashboard';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ROUTES } from '@/lib/routes';
import { LogOut, User, Settings } from 'lucide-react';
import toast from 'react-hot-toast';

const DashboardPage = () => {
  const { user, traceLensUser, loading, logout } = useAuth();
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Navigation */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-blue-600">TraceLens</h1>
            <span className="text-gray-500">Dashboard</span>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* User Info */}
            <div className="flex items-center space-x-2 text-sm">
              <User className="h-4 w-4 text-gray-500" />
              <span className="text-gray-700">{user.displayName || user.email}</span>
            </div>
            
            {/* Sign Out Button */}
            <Button
              variant="outline"
              onClick={handleSignOut}
              className="flex items-center space-x-2 hover:bg-red-50 hover:border-red-200 hover:text-red-600"
            >
              <LogOut className="h-4 w-4" />
              <span>Sign Out</span>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto py-6 space-y-6 px-4">
        {/* User Welcome Section */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Welcome back, {user.displayName || 'User'}! 👋</CardTitle>
              <Button variant="ghost" size="sm" className="flex items-center space-x-2">
                <Settings className="h-4 w-4" />
                <span>Settings</span>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-semibold">{user.email}</p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-gray-600">Account Status</p>
                <p className="font-semibold">
                  {user.emailVerified ? '✅ Verified' : '⚠️ Unverified'}
                </p>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <p className="text-sm text-gray-600">Subscription</p>
                <p className="font-semibold">
                  {traceLensUser?.subscriptionTier || 'Loading...'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Usage Statistics Section */}
        {traceLensUser && (
          <Card>
            <CardHeader>
              <CardTitle>Usage Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <p className="text-sm text-gray-600">Daily Usage</p>
                  <p className="text-2xl font-bold text-yellow-600">
                    {traceLensUser.dailyUsage}
                  </p>
                  <p className="text-xs text-gray-500">
                    of {traceLensUser.subscriptionTier === 'free' ? '3' : '∞'} allowed
                  </p>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <p className="text-sm text-gray-600">Total Analyses</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {traceLensUser.lifetimeAnalysisCount || 0}
                  </p>
                  <p className="text-xs text-gray-500">all time</p>
                </div>
                <div className="text-center p-4 bg-indigo-50 rounded-lg">
                  <p className="text-sm text-gray-600">Privacy Level</p>
                  <p className="text-2xl font-bold text-indigo-600">
                    {traceLensUser.privacyLevel || 'Standard'}
                  </p>
                  <p className="text-xs text-gray-500">protection</p>
                </div>
                <div className="text-center p-4 bg-teal-50 rounded-lg">
                  <p className="text-sm text-gray-600">Member Since</p>
                  <p className="text-lg font-semibold text-teal-600">
                    {traceLensUser.createdAt ? 
                      new Date(traceLensUser.createdAt).toLocaleDateString('en-US', { 
                        month: 'short', 
                        year: 'numeric' 
                      }) : 'Recently'
                    }
                  </p>
                  <p className="text-xs text-gray-500">joined</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* System Status Section */}
        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div>
                  <p className="font-medium text-green-800">Firebase Connection</p>
                  <p className="text-sm text-green-600">Connected & Authenticated</p>
                </div>
                <div className="h-3 w-3 bg-green-500 rounded-full"></div>
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
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <h3 className="font-medium text-gray-800 mb-2">🔍 Start Analysis</h3>
                <p className="text-sm text-gray-600">
                  Analyze any social media profile for privacy insights and digital footprint assessment.
                </p>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <h3 className="font-medium text-gray-800 mb-2">📊 View History</h3>
                <p className="text-sm text-gray-600">
                  Access your previous analysis results and track your privacy improvements over time.
                </p>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <h3 className="font-medium text-gray-800 mb-2">🛡️ Privacy Guide</h3>
                <p className="text-sm text-gray-600">
                  Learn practical tips to improve your digital privacy and reduce your online footprint.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Analysis Dashboard */}
        <AnalysisDashboard />

        {/* Footer Information */}
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-sm text-gray-500 space-y-2">
              <p>🔒 Your privacy is our priority. All analysis data is automatically deleted after 24 hours.</p>
              <p>📧 Questions or feedback? Contact us at support@tracelens.ai</p>
              <div className="flex justify-center space-x-4 mt-4">
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                  🔐 GDPR Compliant
                </span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                  🛡️ Privacy First
                </span>
                <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                  🤖 AI Powered
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
