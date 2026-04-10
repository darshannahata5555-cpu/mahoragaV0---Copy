import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { submitJob } from '../api/jobsApi'

export default function SubmitPage() {
  const navigate = useNavigate()
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [submitted, setSubmitted] = useState(null) // { id }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!url.trim()) {
      setError('Please enter a YouTube URL.')
      return
    }
    setError(null)
    setLoading(true)
    try {
      const job = await submitJob(url.trim())
      setSubmitted(job)
    } catch (err) {
      const msg =
        err?.response?.data?.detail?.[0]?.msg ||
        err?.response?.data?.detail ||
        err?.message ||
        'Submission failed.'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Nav */}
      <nav className="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between">
        <span className="font-bold text-lg tracking-tight">YT Pipeline</span>
        <Link to="/jobs" className="text-sm text-gray-400 hover:text-white transition-colors">
          View All Jobs →
        </Link>
      </nav>

      {/* Main */}
      <div className="flex items-center justify-center px-4 py-20">
        <div className="w-full max-w-xl bg-gray-900 rounded-2xl border border-gray-800 p-8 shadow-2xl">
          <h1 className="text-2xl font-bold mb-2">YouTube Content Intelligence</h1>
          <p className="text-gray-400 text-sm mb-8">
            Paste a YouTube URL to generate clips, LinkedIn posts, and tweets
          </p>

          {!submitted ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
              />

              {error && (
                <p className="text-red-400 text-sm">{error}</p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-blue-900 disabled:cursor-not-allowed text-white font-medium py-3 rounded-lg transition-colors text-sm"
              >
                {loading ? 'Analyzing...' : 'Analyze Video'}
              </button>
            </form>
          ) : (
            <div className="space-y-4">
              <div className="bg-green-900/30 border border-green-700 rounded-lg px-4 py-3">
                <p className="text-green-400 text-sm font-medium">Job submitted successfully</p>
                <p className="text-gray-400 text-xs mt-1 font-mono break-all">ID: {submitted.id}</p>
              </div>
              <Link
                to={`/jobs/${submitted.id}`}
                className="block text-center bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg px-4 py-3 text-sm font-medium transition-colors"
              >
                View Job →
              </Link>
              <button
                onClick={() => { setSubmitted(null); setUrl(''); setError(null) }}
                className="w-full text-gray-500 hover:text-gray-300 text-sm py-2 transition-colors"
              >
                Submit another URL
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
