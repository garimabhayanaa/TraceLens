import React, { useState } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'
import { useRouter } from 'next/router'

// Configure axios
axios.defaults.baseURL = 'http://localhost:5000'
axios.defaults.withCredentials = true

export default function Dashboard() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    social_links: ''
  })
  const [results, setResults] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const socialLinks = formData.social_links
        .split('\n')
        .map(link => link.trim())
        .filter(link => link.length > 0)

      const response = await axios.post('/api/analyze', {
        ...formData,
        social_links: socialLinks
      })

      setResults(response.data.results)
      toast.success('Analysis complete!')
    } catch (err: any) {
      const errorMsg = err?.response?.data?.error || 'Analysis failed'
      toast.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await axios.post('/api/logout')
      toast.success('Logged out successfully')
      router.push('/')
    } catch (err) {
      toast.error('Logout failed')
    }
  }

  // Privacy score color helper
  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600'
    if (score >= 6) return 'text-yellow-600'
    if (score >= 4) return 'text-orange-600'
    return 'text-red-600'
  }

  const getScoreBackground = (score: number) => {
    if (score >= 8) return 'bg-green-50 border-green-200'
    if (score >= 6) return 'bg-yellow-50 border-yellow-200'
    if (score >= 4) return 'bg-orange-50 border-orange-200'
    return 'bg-red-50 border-red-200'
  }

  if (!results) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-sm p-4">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <h1 className="text-2xl font-bold text-blue-600">LeakPeek Dashboard</h1>
            <button
              onClick={handleLogout}
              className="text-gray-600 hover:text-gray-900 font-medium"
            >
              Logout
            </button>
          </div>
        </nav>

        {/* Main Content */}
        <div className="max-w-2xl mx-auto p-6">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-3xl font-bold mb-6 text-center">Digital Footprint Analysis</h2>

            {/* Privacy Notice */}
            <div className="mb-8 p-6 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-semibold text-blue-800 mb-3">🔒 Privacy & Security Notice</h3>
              <ul className="text-blue-700 text-sm space-y-2">
                <li>• You can only analyze your own digital footprint</li>
                <li>• All data is automatically deleted within 24 hours</li>
                <li>• Only publicly available information is analyzed</li>
                <li>• This tool is for educational purposes only</li>
              </ul>
            </div>

            {/* Analysis Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name *
                </label>
                <input
                  type="text"
                  name="name"
                  placeholder="Enter your full name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address * (must match your login email)
                </label>
                <input
                  type="email"
                  name="email"
                  placeholder="Enter your email address"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Social Media Profiles (Optional)
                </label>
                <textarea
                  name="social_links"
                  placeholder="Paste your social media profile URLs here, one per line:&#10;https://linkedin.com/in/yourprofile&#10;https://github.com/yourusername&#10;https://twitter.com/yourusername&#10;https://instagram.com/yourusername"
                  value={formData.social_links}
                  onChange={handleChange}
                  rows={6}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-sm text-gray-500 mt-2">
                  Leave empty to analyze just your name and email patterns
                </p>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-4 rounded-lg hover:bg-blue-700 transition font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Analyzing Your Digital Footprint...' : 'Start Privacy Analysis'}
              </button>
            </form>
          </div>
        </div>
      </div>
    )
  }

  // Results View
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">LeakPeek Results</h1>
          <div className="space-x-4">
            <button
              onClick={() => setResults(null)}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              New Analysis
            </button>
            <button
              onClick={handleLogout}
              className="text-gray-600 hover:text-gray-900 font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Analysis Complete</h1>
          <p className="text-xl text-gray-600">Here's what AI could infer about you from public data</p>
        </div>

        {/* Privacy Score */}
        <div className={`mb-8 p-8 rounded-lg border-2 ${getScoreBackground(results.privacy_score)}`}>
          <div className="text-center">
            <h2 className="text-2xl font-semibold mb-4">Your Privacy Score</h2>
            <div className={`text-8xl font-extrabold mb-4 ${getScoreColor(results.privacy_score)}`}>
              {results.privacy_score?.toFixed(1)}
            </div>
            <div className="text-lg text-gray-600">out of 10.0</div>
            <p className="text-sm text-gray-600 mt-4 max-w-md mx-auto">
              {results.privacy_score >= 8 ? 'Excellent! Your digital privacy is well protected.' :
               results.privacy_score >= 6 ? 'Good privacy with some room for improvement.' :
               results.privacy_score >= 4 ? 'Moderate privacy risks detected. Consider the recommendations below.' :
               'High privacy risks detected. Immediate action recommended.'}
            </p>
          </div>
        </div>

        {/* Analysis Results Grid */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Interests */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">🎯 Detected Interests</h3>
            {results.interests && results.interests.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {results.interests.map((interest: string, idx: number) => (
                  <span
                    key={idx}
                    className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium"
                  >
                    {interest}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic">No specific interests detected from available data.</p>
            )}
          </div>

          {/* Schedule Patterns */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">⏰ Activity Patterns</h3>
            {Object.keys(results.schedule_patterns).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(results.schedule_patterns).map(([key, value], idx) => (
                  <div key={idx} className="flex justify-between items-center">
                    <span className="font-medium text-gray-700 capitalize">
                      {key.replace('_', ' ')}:
                    </span>
                    <span className="text-gray-600 text-sm">{value as string}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic">No clear activity patterns detected.</p>
            )}
          </div>

          {/* Economic Indicators */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">💼 Professional Indicators</h3>
            {Object.keys(results.economic_indicators).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(results.economic_indicators).map(([key, value], idx) => (
                  <div key={idx} className="flex justify-between items-center">
                    <span className="font-medium text-gray-700 capitalize">
                      {key.replace('_', ' ')}:
                    </span>
                    <span className="text-gray-600 text-sm">{value as string}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic">No professional indicators detected.</p>
            )}
          </div>

          {/* Communication Patterns */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">💬 Communication Style</h3>
            {Object.keys(results.mental_state).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(results.mental_state).map(([key, value], idx) => (
                  <div key={idx} className="flex justify-between items-center">
                    <span className="font-medium text-gray-700 capitalize">
                      {key.replace('_', ' ')}:
                    </span>
                    <span className="text-gray-600 text-sm">{value as string}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic">No communication patterns detected.</p>
            )}
          </div>
        </div>

        {/* Data Sources */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">📊 Data Sources Analyzed</h3>
          {results.data_sources && results.data_sources.length > 0 ? (
            <ul className="space-y-2">
              {results.data_sources.map((src: string, idx: number) => (
                <li key={idx} className="flex items-center text-gray-700">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  {src}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 italic">Analysis based on provided information only.</p>
          )}
        </div>

        {/* Recommendations */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-6 text-gray-800">🛡️ Privacy Recommendations</h3>
          <div className="space-y-4">
            {results.recommendations.map((rec: string, idx: number) => (
              <div key={idx} className="flex items-start">
                <span className="text-blue-500 mr-3 mt-1">•</span>
                <span className="text-gray-700 leading-relaxed">{rec}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
