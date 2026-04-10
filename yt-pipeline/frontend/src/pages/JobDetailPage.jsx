import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getJob } from '../api/jobsApi'
import { useJobPolling } from '../hooks/useJobPolling'
import { StatusBadge } from '../components/StatusBadge'
import { PipelineTracker } from '../components/PipelineTracker'
import { ClipCard } from '../components/ClipCard'
import { SocialPostsPanel } from '../components/SocialPostsPanel'
import { TranscriptViewer } from '../components/TranscriptViewer'

const TERMINAL = new Set(['complete', 'failed'])

function Section({ title, children }) {
  return (
    <section className="space-y-4">
      <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest">
        {title}
      </h2>
      {children}
    </section>
  )
}

export default function JobDetailPage() {
  const { id: jobId } = useParams()
  const navigate = useNavigate()

  const [job, setJob] = useState(null)
  const [initialLoading, setInitialLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)

  // Fetch once on mount for immediate display
  useEffect(() => {
    getJob(jobId)
      .then((data) => {
        setJob(data)
      })
      .catch((err) => {
        if (err?.response?.status === 404) setNotFound(true)
      })
      .finally(() => setInitialLoading(false))
  }, [jobId])

  // Live-poll while not terminal; merge polled data into state
  const pollingActive = job && !TERMINAL.has(job.status)
  const onComplete = useCallback((finalJob) => setJob(finalJob), [])
  const { job: polledJob } = useJobPolling(pollingActive ? jobId : null, onComplete)

  // Keep job state up to date with poll results
  useEffect(() => {
    if (polledJob) setJob(polledJob)
  }, [polledJob])

  // ── Render states ─────────────────────────────────────────────────────────

  if (initialLoading) {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
        <p className="text-gray-500">Loading job...</p>
      </div>
    )
  }

  if (notFound || !job) {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center gap-4">
        <p className="text-gray-400">Job not found.</p>
        <Link to="/jobs" className="text-blue-400 hover:text-blue-300 text-sm">
          ← Back to Jobs
        </Link>
      </div>
    )
  }

  const isComplete = job.status === 'complete'
  const isFailed   = job.status === 'failed'
  const hasTranscript = (job.transcript_word_count ?? 0) > 0

  // For PipelineTracker: when failed, try to infer last real stage from job data
  // (e.g. if video_title exists, extraction ran; treat as 'analyzing' failing)
  function trackerStatus() {
    if (!isFailed) return job.status
    if (job.output_clips) return 'failed' // failed at analysis output
    if (job.video_title)  return 'failed' // failed at or after extracting
    return 'failed'
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Nav */}
      <nav className="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between">
        <button
          onClick={() => navigate('/jobs')}
          className="text-sm text-gray-400 hover:text-white transition-colors"
        >
          ← Back to Jobs
        </button>
        <StatusBadge status={job.status} />
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-10">

        {/* ── Job header ───────────────────────────────────────────────── */}
        <div className="space-y-1">
          <h1 className="text-2xl font-bold leading-snug">
            {job.video_title || 'Processing…'}
          </h1>
          <div className="flex flex-wrap gap-x-3 gap-y-1 text-sm text-gray-400">
            {job.channel_name && <span>{job.channel_name}</span>}
            {job.video_duration && (
              <>
                <span className="text-gray-700">·</span>
                <span className="font-mono">{job.video_duration}</span>
              </>
            )}
            <span className="text-gray-700">·</span>
            <a
              href={job.youtube_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 truncate max-w-xs"
            >
              {job.youtube_url}
            </a>
          </div>
        </div>

        {/* ── Pipeline tracker ─────────────────────────────────────────── */}
        <Section title="Pipeline">
          <PipelineTracker status={trackerStatus()} />
        </Section>

        {/* ── Failed error card ────────────────────────────────────────── */}
        {isFailed && job.error && (
          <div className="bg-red-900/20 border border-red-700 rounded-xl px-5 py-4 space-y-1">
            <p className="text-red-400 font-semibold text-sm">
              {job.error.code || 'Error'}
            </p>
            <p className="text-red-300 text-sm">{job.error.message}</p>
          </div>
        )}

        {/* ── Processing message ───────────────────────────────────────── */}
        {!isComplete && !isFailed && (
          <p className="text-gray-500 text-sm text-center py-4">
            Processing — results will appear when complete
          </p>
        )}

        {/* ── Clips ────────────────────────────────────────────────────── */}
        {isComplete && job.output_clips?.length > 0 && (
          <Section title="Clips">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {job.output_clips.map((clip) => (
                <ClipCard key={clip.clip_id} clip={clip} videoId={job.video_id} />
              ))}
            </div>
          </Section>
        )}

        {/* ── Social posts ─────────────────────────────────────────────── */}
        {isComplete && (
          <Section title="Social Posts">
            <SocialPostsPanel
              linkedinShort={job.output_linkedin_short}
              linkedinLong={job.output_linkedin_long}
              twitterPost={job.output_twitter_post}
              twitterThread={job.output_twitter_thread}
            />
          </Section>
        )}

        {/* ── Transcript ───────────────────────────────────────────────── */}
        {hasTranscript && (
          <Section title="Transcript">
            <TranscriptViewer jobId={jobId} />
          </Section>
        )}

      </div>
    </div>
  )
}
