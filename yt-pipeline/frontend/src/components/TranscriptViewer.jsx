import { useState, useEffect } from 'react'
import { getTranscript } from '../api/jobsApi'

export function TranscriptViewer({ jobId }) {
  const [isOpen, setIsOpen] = useState(false)
  const [transcript, setTranscript] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')

  // Fetch on first expand
  useEffect(() => {
    if (!isOpen || transcript !== null || loading) return
    setLoading(true)
    setError(null)
    getTranscript(jobId)
      .then((data) => setTranscript(data))
      .catch(() => setError('Transcript not available'))
      .finally(() => setLoading(false))
  }, [isOpen, jobId, transcript, loading])

  const filtered = transcript
    ? transcript.filter((cue) =>
        cue.text.toLowerCase().includes(search.toLowerCase())
      )
    : []

  function formatTime(seconds) {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = Math.floor(seconds % 60)
    return [h, m, s].map((n) => String(n).padStart(2, '0')).join(':')
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
      {/* Toggle */}
      <button
        onClick={() => setIsOpen((o) => !o)}
        className="w-full flex items-center justify-between px-5 py-4 text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-800/50 transition-colors"
      >
        <span>{isOpen ? 'Hide Transcript ▲' : 'Show Transcript ▼'}</span>
        {transcript && (
          <span className="text-xs text-gray-500 font-normal">
            {transcript.length} cues
          </span>
        )}
      </button>

      {isOpen && (
        <div className="border-t border-gray-800">
          {/* Search */}
          <div className="px-5 py-3 border-b border-gray-800">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search transcript..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Body */}
          <div className="max-h-96 overflow-y-auto px-5 py-3 space-y-1">
            {loading && (
              <p className="text-gray-500 text-sm py-4 text-center">Loading transcript...</p>
            )}
            {error && (
              <p className="text-red-400 text-sm py-4 text-center">{error}</p>
            )}
            {!loading && !error && filtered.length === 0 && (
              <p className="text-gray-500 text-sm py-4 text-center">
                {search ? 'No cues match your search.' : 'No transcript data.'}
              </p>
            )}
            {!loading &&
              !error &&
              filtered.map((cue) => (
                <div key={cue.index} className="flex gap-3 py-1">
                  <span className="font-mono text-xs text-gray-500 shrink-0 pt-0.5">
                    [{formatTime(cue.start_seconds)}]
                  </span>
                  <span className="text-sm text-white leading-relaxed">{cue.text}</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}
