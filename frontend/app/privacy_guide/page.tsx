'use client'
import Link from 'next/link'
import { 
  ShieldCheckIcon, 
  EyeSlashIcon, 
  LockClosedIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'

export default function PrivacyGuide() {
  const privacyTips = [
    {
      title: "Review Privacy Settings Regularly",
      description: "Check and update privacy settings on all social media platforms at least every 3 months.",
      icon: <ShieldCheckIcon className="w-6 h-6" />,
      difficulty: "Easy",
      impact: "High"
    },
    {
      title: "Limit Personal Information Sharing",
      description: "Avoid sharing specific details like full birth dates, addresses, phone numbers, or location data.",
      icon: <EyeSlashIcon className="w-6 h-6" />,
      difficulty: "Easy",
      impact: "High"
    },
    {
      title: "Use Different Usernames Across Platforms",
      description: "Prevent easy correlation by using unique usernames and profile pictures on different platforms.",
      icon: <LockClosedIcon className="w-6 h-6" />,
      difficulty: "Medium",
      impact: "Medium"
    },
    {
      title: "Be Mindful of Pattern Recognition",
      description: "Vary your posting times, topics, and online behavior to avoid predictable patterns.",
      icon: <ExclamationTriangleIcon className="w-6 h-6" />,
      difficulty: "Medium",
      impact: "Medium"
    },
    {
      title: "Enable Two-Factor Authentication",
      description: "Add an extra layer of security to all your online accounts.",
      icon: <CheckCircleIcon className="w-6 h-6" />,
      difficulty: "Easy",
      impact: "High"
    },
    {
      title: "Regular Digital Footprint Audits",
      description: "Search for your name and email online regularly to see what information is publicly available.",
      icon: <InformationCircleIcon className="w-6 h-6" />,
      difficulty: "Easy",
      impact: "Medium"
    }
  ]

  const privacyTools = [
    {
      name: "ProtonMail",
      description: "Privacy-focused email service with end-to-end encryption",
      category: "Email",
      free: true
    },
    {
      name: "Signal",
      description: "Secure messaging app with disappearing messages",
      category: "Messaging",
      free: true
    },
    {
      name: "DuckDuckGo",
      description: "Search engine that doesn't track users",
      category: "Search",
      free: true
    },
    {
      name: "Tor Browser",
      description: "Anonymous web browsing",
      category: "Browsing",
      free: true
    },
    {
      name: "1Password",
      description: "Secure password manager",
      category: "Password Management",
      free: false
    },
    {
      name: "ExpressVPN",
      description: "Virtual Private Network for secure browsing",
      category: "VPN",
      free: false
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md shadow-sm p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold text-blue-600">
            TraceLens
          </Link>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            Privacy Education Hub
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Learn how to protect your digital privacy and reduce your online footprint with these practical tips and tools.
          </p>
        </div>

        {/* Privacy Tips Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-800 mb-8 text-center">
            Essential Privacy Tips
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {privacyTips.map((tip, index) => (
              <div key={index} className="bg-white rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-shadow">
                <div className="flex items-center mb-4">
                  <div className="text-blue-600 mr-3">
                    {tip.icon}
                  </div>
                  <h3 className="text-lg font-bold text-gray-800">{tip.title}</h3>
                </div>
                <p className="text-gray-600 mb-4">{tip.description}</p>
                <div className="flex justify-between text-sm">
                  <span className={`px-3 py-1 rounded-full ${
                    tip.difficulty === 'Easy' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {tip.difficulty}
                  </span>
                  <span className={`px-3 py-1 rounded-full ${
                    tip.impact === 'High' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'
                  }`}>
                    {tip.impact} Impact
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Privacy Tools Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-800 mb-8 text-center">
            Recommended Privacy Tools
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {privacyTools.map((tool, index) => (
              <div key={index} className="bg-white rounded-2xl shadow-xl p-6">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-bold text-gray-800">{tool.name}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    tool.free ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'
                  }`}>
                    {tool.free ? 'Free' : 'Paid'}
                  </span>
                </div>
                <p className="text-sm text-blue-600 font-medium mb-2">{tool.category}</p>
                <p className="text-gray-600">{tool.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Social Media Privacy Guide */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-800 mb-8 text-center">
            Social Media Privacy Checklist
          </h2>
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-bold text-gray-800 mb-4">Facebook/Meta</h3>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Set profile to private</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Limit post visibility to friends only</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Turn off location tracking</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Disable facial recognition</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Review tagged photos before posting</li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-800 mb-4">Twitter/X</h3>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Make tweets private</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Disable location information</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Turn off photo tagging</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Limit who can find you by email/phone</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Disable ad personalization</li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-800 mb-4">LinkedIn</h3>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Control profile visibility</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Limit activity broadcasts</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Turn off active status</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Control who can see your connections</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Disable data sharing with third parties</li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-800 mb-4">Instagram</h3>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Switch to private account</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Turn off location services</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Disable activity status</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Control story visibility</li>
                  <li className="flex items-center"><CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />Limit data sharing with partners</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Digital Footprint Reduction Guide */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-800 mb-8 text-center">
            Reduce Your Digital Footprint
          </h2>
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="space-y-6">
              <div className="border-l-4 border-blue-500 pl-6">
                <h3 className="text-lg font-bold text-gray-800 mb-2">1. Audit Your Online Presence</h3>
                <p className="text-gray-600">Search for your name, email, and phone number on Google and other search engines. Use tools like Google Alerts to monitor mentions of your name.</p>
              </div>
              <div className="border-l-4 border-green-500 pl-6">
                <h3 className="text-lg font-bold text-gray-800 mb-2">2. Delete Unused Accounts</h3>
                <p className="text-gray-600">Close social media accounts and online services you no longer use. Use services like AccountKiller.com to find deletion instructions.</p>
              </div>
              <div className="border-l-4 border-yellow-500 pl-6">
                <h3 className="text-lg font-bold text-gray-800 mb-2">3. Use Privacy-Focused Alternatives</h3>
                <p className="text-gray-600">Replace mainstream services with privacy-focused alternatives like ProtonMail for email, Signal for messaging, and DuckDuckGo for search.</p>
              </div>
              <div className="border-l-4 border-red-500 pl-6">
                <h3 className="text-lg font-bold text-gray-800 mb-2">4. Be Selective with Personal Information</h3>
                <p className="text-gray-600">Think twice before sharing personal details online. Avoid posting photos with location data, full birth dates, or other identifying information.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
          <h2 className="text-3xl font-bold mb-4">Ready to Test Your Privacy?</h2>
          <p className="text-xl mb-6">Use TraceLens to see what information can be inferred about you from public data.</p>
          <Link 
            href="/dashboard"
            className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition inline-block"
          >
            Start Your Analysis
          </Link>
        </div>
      </div>
    </div>
  )
}
