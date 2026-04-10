import { useState } from 'react'

export function ClipCard({ clip, videoId }) {
  const [copied, setCopied] = useState(false)

  function handleCopyTimestamp() {
    navigator.clipboard.writeText(clip.start_time).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  const ytUrl = `https://www.youtube.com/watch?v=${videoId}&t=${clip.start_seconds}`

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex flex-col gap-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Clip {clip.clip_id}
        </span>
        <span className="bg-gray-800 text-gray-300 text-xs font-mono px-2 py-0.5 rounded-full">
          {clip.duration_seconds}s
        </span>
      </div>

      {/* Timestamp range */}
      <div className="font-mono text-sm text-blue-400">
        {clip.start_time} → {clip.end_time}
      </div>

      {/* Hook summary */}
      <p className="text-white text-sm leading-relaxed">{clip.hook_summary}</p>

      {/* Why this works */}
      <p className="text-gray-400 text-sm leading-relaxed">{clip.why_this_works}</p>

      {/* Suggested title */}
      <p className="text-gray-300 text-sm italic">{clip.suggested_title}</p>

      {/* Actions */}
      <div className="flex gap-2 pt-1">
        <a
          href={ytUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 text-center bg-red-900/50 hover:bg-red-800 border border-red-800 text-red-300 text-xs font-medium px-3 py-2 rounded-lg transition-colors"
        >
          Open on YouTube ↗
        </a>
        <button
          onClick={handleCopyTimestamp}
          className="flex-1 bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-medium px-3 py-2 rounded-lg transition-colors"
        >
          {copied ? 'Copied!' : 'Copy Timestamp'}
        </button>
      </div>
    </div>
  )
}
