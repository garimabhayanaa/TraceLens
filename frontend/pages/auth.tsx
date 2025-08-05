import AuthForm from '../components/AuthForm'
import Link from 'next/link'

export default function Auth() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="p-6">
        <Link href="/" className="text-blue-600 hover:text-blue-800 font-semibold">
          ← Back to Home
        </Link>
      </nav>

      <div className="flex items-center justify-center min-h-[80vh]">
        <AuthForm />
      </div>
    </div>
  )
}
