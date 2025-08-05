import React, { useState } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'
import { useRouter } from 'next/router'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  PointElement,
  LineElement,
} from 'chart.js'
import { Bar, Doughnut, PolarArea, Radar } from 'react-chartjs-2'
import { 
  ShieldCheckIcon, 
  ShieldExclamationIcon,
  EyeIcon,
  ClockIcon,
  BriefcaseIcon,
  ChatBubbleLeftRightIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  PointElement,
  LineElement
)

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

  // Privacy score utilities
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

  const getScoreIcon = (score: number) => {
    if (score >= 6) return <ShieldCheckIcon className="w-8 h-8 text-green-500" />
    return <ShieldExclamationIcon className="w-8 h-8 text-red-500" />
  }

  // Chart configurations
  const createPrivacyScoreChart = (score: number) => ({
    labels: ['Privacy Protected', 'Risk Exposure'],
    datasets: [{
      data: [score, 10 - score],
      backgroundColor: [
        score >= 6 ? '#10B981' : '#EF4444',
        '#E5E7EB'
      ],
      borderWidth: 0,
    }]
  })

  const createInterestsChart = (interests: string[]) => ({
    labels: interests.slice(0, 8), // Show top 8 interests
    datasets: [{
      label: 'Interest Categories',
      data: interests.slice(0, 8).map(() => 1),
      backgroundColor: [
        '#3B82F6', '#10B981', '#F59E0B', '#EF4444',
        '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'
      ],
      borderWidth: 0,
    }]
  })

  const createRadarChart = (results: any) => {
    const categories = ['Interests', 'Schedule', 'Economic', 'Communication', 'Privacy']
    const scores = [
      Math.min(results.interests?.length * 2 || 0, 10),
      Object.keys(results.schedule_patterns).length * 2.5,
      Object.keys(results.economic_indicators).length * 2.5,
      Object.keys(results.mental_state).length * 2.5,
      results.privacy_score
    ]

    return {
      labels: categories,
      datasets: [{
        label: 'Digital Footprint Analysis',
        data: scores,
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(59, 130, 246, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(59, 130, 246, 1)'
      }]
    }
  }

  if (!results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {/* Navigation */}
        <nav className="bg-white/80 backdrop-blur-md shadow-sm p-4 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <h1 className="text-2xl font-bold text-blue-600">LeakPeek Dashboard</h1>
            <button 
              onClick={handleLogout}
              className="text-gray-600 hover:text-gray-900 font-medium transition"
            >
              Logout
            </button>
          </div>
        </nav>

        {/* Main Content */}
        <div className="max-w-3xl mx-auto p-6">
          <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-xl p-8">
            <div className="text-center mb-8">
              <EyeIcon className="w-16 h-16 text-blue-600 mx-auto mb-4" />
              <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Digital Footprint Analysis
              </h2>
              <p className="text-gray-600 text-lg">
                Discover what AI can infer about you from public data
              </p>
            </div>
            
            {/* Privacy Notice */}
            <div className="mb-8 p-6 bg-blue-50 border border-blue-200 rounded-xl">
              <h3 className="font-semibold text-blue-800 mb-3 flex items-center">
                <ShieldCheckIcon className="w-5 h-5 mr-2" />
                Privacy & Security Notice
              </h3>
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
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Full Name *
                </label>
                <input
                  type="text"
                  name="name"
                  placeholder="Enter your full name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Email Address * (must match your login email)
                </label>
                <input
                  type="email"
                  name="email"
                  placeholder="Enter your email address"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Social Media Profiles (Optional)
                </label>
                <textarea
                  name="social_links"
                  placeholder="Paste your social media profile URLs here, one per line:&#10;https://linkedin.com/in/yourprofile&#10;https://github.com/yourusername&#10;https://twitter.com/yourusername&#10;https://instagram.com/yourusername"
                  value={formData.social_links}
                  onChange={handleChange}
                  rows={6}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                />
                <p className="text-sm text-gray-500 mt-2">
                  Leave empty to analyze just your name and email patterns
                </p>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-xl hover:from-blue-700 hover:to-purple-700 transition font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
                    Analyzing Your Digital Footprint...
                  </div>
                ) : (
                  'Start Privacy Analysis'
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    )
  }

  // Results View
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md shadow-sm p-4 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">LeakPeek Results</h1>
          <div className="space-x-4">
            <button 
              onClick={() => setResults(null)}
              className="text-blue-600 hover:text-blue-800 font-medium transition"
            >
              New Analysis
            </button>
            <button 
              onClick={handleLogout}
              className="text-gray-600 hover:text-gray-900 font-medium transition"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            Analysis Complete
          </h1>
          <p className="text-xl text-gray-600">Here's what AI could infer about you from public data</p>
        </div>

        {/* Privacy Score Hero Section */}
        <div className={`mb-8 p-8 rounded-2xl border-2 shadow-xl ${getScoreBackground(results.privacy_score)}`}>
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center mb-4">
                {getScoreIcon(results.privacy_score)}
                <h2 className="text-3xl font-bold ml-3">Your Privacy Score</h2>
              </div>
              <div className={`text-7xl font-extrabold mb-2 ${getScoreColor(results.privacy_score)}`}>
                {results.privacy_score?.toFixed(1)}
              </div>
              <div className="text-xl text-gray-600 mb-4">out of 10.0</div>
              <p className="text-gray-700 max-w-md">
                {results.privacy_score >= 8 ? 'Excellent! Your digital privacy is well protected.' :
                 results.privacy_score >= 6 ? 'Good privacy with some room for improvement.' :
                 results.privacy_score >= 4 ? 'Moderate privacy risks detected. Consider the recommendations below.' :
                 'High privacy risks detected. Immediate action recommended.'}
              </p>
            </div>
            <div className="w-64 h-64 ml-8">
              <Doughnut 
                data={createPrivacyScoreChart(results.privacy_score)}
                options={{
                  responsive: true,
                  maintainAspectRatio: true,
                  plugins: {
                    legend: { display: false },
                    tooltip: {
                      callbacks: {
                        label: (context) => `${context.label}: ${context.parsed.toFixed(1)}/10`
                      }
                    }
                  }
                }}
              />
            </div>
          </div>
        </div>

        {/* Overview Radar Chart */}
        <div className="mb-8 bg-white rounded-2xl shadow-xl p-8">
          <h3 className="text-2xl font-bold mb-6 text-center">Digital Footprint Overview</h3>
          <div className="max-w-lg mx-auto">
            <Radar
              data={createRadarChart(results)}
              options={{
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                  r: {
                    beginAtZero: true,
                    max: 10,
                    ticks: { stepSize: 2 }
                  }
                },
                plugins: {
                  legend: { display: false }
                }
              }}
            />
          </div>
        </div>

        {/* Analysis Results Grid */}
        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {/* Interests */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="flex items-center mb-6">
              <EyeIcon className="w-8 h-8 text-blue-600 mr-3" />
              <h3 className="text-2xl font-bold text-gray-800">Detected Interests</h3>
            </div>
            {results.interests && results.interests.length > 0 ? (
              <div>
                <div className="flex flex-wrap gap-3 mb-6">
                  {results.interests.map((interest: string, idx: number) => (
                    <span 
                      key={idx} 
                      className="inline-block bg-gradient-to-r from-blue-500 to-purple-500 text-white px-4 py-2 rounded-full text-sm font-semibold shadow-md"
                    >
                      {interest}
                    </span>
                  ))}
                </div>
                {results.interests.length > 0 && (
                  <div className="h-64">
                    <PolarArea
                      data={createInterestsChart(results.interests)}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: { display: false }
                        }
                      }}
                    />
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-500 italic text-center py-8">
                No specific interests detected from available data.
              </p>
            )}
          </div>

          {/* Schedule Patterns */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="flex items-center mb-6">
              <ClockIcon className="w-8 h-8 text-green-600 mr-3" />
              <h3 className="text-2xl font-bold text-gray-800">Activity Patterns</h3>
            </div>
            {Object.keys(results.schedule_patterns).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(results.schedule_patterns).map(([key, value], idx) => (
                  <div key={idx} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-gray-700 capitalize">
                        {key.replace('_', ' ')}
                      </span>
                      <span className="text-gray-600 bg-white px-3 py-1 rounded-full text-sm">
                        {value as string}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic text-center py-8">
                No clear activity patterns detected.
              </p>
            )}
          </div>

          {/* Economic Indicators */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="flex items-center mb-6">
              <BriefcaseIcon className="w-8 h-8 text-yellow-600 mr-3" />
              <h3 className="text-2xl font-bold text-gray-800">Professional Indicators</h3>
            </div>
            {Object.keys(results.economic_indicators).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(results.economic_indicators).map(([key, value], idx) => (
                  <div key={idx} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-gray-700 capitalize">
                        {key.replace('_', ' ')}
                      </span>
                      <span className="text-gray-600 bg-white px-3 py-1 rounded-full text-sm">
                        {value as string}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic text-center py-8">
                No professional indicators detected.
              </p>
            )}
          </div>

          {/* Communication Patterns */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="flex items-center mb-6">
              <ChatBubbleLeftRightIcon className="w-8 h-8 text-purple-600 mr-3" />
              <h3 className="text-2xl font-bold text-gray-800">Communication Style</h3>
            </div>
            {Object.keys(results.mental_state).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(results.mental_state).map(([key, value], idx) => (
                  <div key={idx} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-gray-700 capitalize">
                        {key.replace('_', ' ')}
                      </span>
                      <span className="text-gray-600 bg-white px-3 py-1 rounded-full text-sm">
                        {value as string}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic text-center py-8">
                No communication patterns detected.
              </p>
            )}
          </div>
        </div>

        {/* Data Sources */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <h3 className="text-2xl font-bold mb-6 text-gray-800">📊 Data Sources Analyzed</h3>
          {results.data_sources && results.data_sources.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-4">
              {results.data_sources.map((src: string, idx: number) => (
                <div key={idx} className="flex items-center bg-blue-50 rounded-lg p-4">
                  <div className="w-3 h-3 bg-blue-500 rounded-full mr-4"></div>
                  <span className="text-gray-700 font-medium">{src}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 italic text-center py-8">
              Analysis based on provided information only.
            </p>
          )}
        </div>

        {/* Recommendations */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="flex items-center mb-6">
            <ExclamationTriangleIcon className="w-8 h-8 text-red-600 mr-3" />
            <h3 className="text-2xl font-bold text-gray-800">Privacy Recommendations</h3>
          </div>
          <div className="grid gap-4">
            {results.recommendations.map((rec: string, idx: number) => (
              <div key={idx} className="flex items-start bg-gradient-to-r from-red-50 to-orange-50 rounded-lg p-4 border-l-4 border-red-400">
                <span className="text-red-500 mr-4 mt-1 font-bold">•</span>
                <span className="text-gray-700 leading-relaxed">{rec}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}