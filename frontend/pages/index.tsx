import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen py-24 bg-gradient-to-b from-blue-600 to-indigo-900 text-white">
      <h1 className="text-6xl font-extrabold mb-4">TraceLens</h1>
      <p className="text-xl max-w-xl text-center mb-12">See What an AI Can Infer About You From Public Data</p>
      <div className="space-x-6">
        <Link href="/auth" className="bg-white text-blue-700 px-6 py-3 rounded font-semibold hover:bg-blue-100 transition">
          Get Started
        </Link>
        <Link href="/privacy-guide" className="bg-purple-600 text-white px-6 py-3 rounded font-semibold hover:bg-purple-700 transition">
          Privacy Guide
        </Link>
      </div>
    </main>
  )
}
