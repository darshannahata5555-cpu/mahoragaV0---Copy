import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { listJobs, deleteJob } from '../api/jobsApi'
import { StatusBadge } from '../components/StatusBadge'

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: '2-digit',
    year: 'numeric',
  })
}

function truncate(text, max) {
  if (!text) return null
  return text.length > max ? text.slice(0, max) + '...' : text
}

export default function JobListPage() {
  const navigate = useNavigate()
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [deletingId, setDeletingId] = useState(null)

  const fetchJobs = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await listJobs()
      setJobs(data)
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to load jobs.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  async function handleDelete(e, jobId) {
    e.stopPropagation()
    setDeletingId(jobId)
    try {
      await deleteJob(jobId)
      await fetchJobs()
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || 'Delete failed.')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Nav */}
      <nav className="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="font-bold text-lg tracking-tight hover:text-gray-300 transition-colors"
        >
          YT Pipeline
        </button>
        <span className="text-sm text-gray-400">Jobs</span>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">All Jobs</h1>
          <button
            onClick={() => navigate('/')}
            className="bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            + New Analysis
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-lg px-4 py-3 text-red-400 text-sm mb-6">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="text-gray-500 text-sm py-12 text-center">Loading jobs...</div>
        )}

        {/* Empty */}
        {!loading && !error && jobs.length === 0 && (
          <div className="text-gray-500 text-sm py-20 text-center">
            No jobs yet. Submit a YouTube URL to get started.
          </div>
        )}

        {/* Table */}
        {!loading && jobs.length > 0 && (
          <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400 text-xs uppercase tracking-wider">
                  <th className="text-left px-4 py-3 font-medium">Video</th>
                  <th className="text-left px-4 py-3 font-medium">Channel</th>
                  <th className="text-left px-4 py-3 font-medium">Duration</th>
                  <th className="text-left px-4 py-3 font-medium">Status</th>
                  <th className="text-left px-4 py-3 font-medium">Date</th>
                  <th className="text-left px-4 py-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job, idx) => (
                  <tr
                    key={job.id}
                    onClick={() => navigate(`/jobs/${job.id}`)}
                    className={`border-b border-gray-800/50 last:border-0 cursor-pointer hover:bg-gray-800/50 transition-colors ${idx % 2 === 0 ? '' : 'bg-gray-900/50'}`}
                  >
                    <td className="px-4 py-3 font-medium text-white max-w-xs">
                      {truncate(job.video_title, 60) || (
                        <span className="text-gray-500 text-xs font-mono">
                          {truncate(job.youtube_url, 50)}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-gray-400">
                      {job.channel_name || '—'}
                    </td>
                    <td className="px-4 py-3 text-gray-400 font-mono text-xs">
                      {job.video_duration || '—'}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={job.status} />
                    </td>
                    <td className="px-4 py-3 text-gray-400 text-xs whitespace-nowrap">
                      {formatDate(job.created_at)}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => navigate(`/jobs/${job.id}`)}
                          className="bg-gray-700 hover:bg-gray-600 text-white text-xs px-3 py-1.5 rounded-md transition-colors"
                        >
                          View
                        </button>
                        <button
                          onClick={(e) => handleDelete(e, job.id)}
                          disabled={deletingId === job.id}
                          className="bg-red-900/60 hover:bg-red-800 disabled:opacity-50 disabled:cursor-not-allowed text-red-300 text-xs px-3 py-1.5 rounded-md transition-colors"
                        >
                          {deletingId === job.id ? '...' : 'Delete'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
