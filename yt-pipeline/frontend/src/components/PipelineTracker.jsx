const STAGES = ['queued', 'extracting', 'analyzing', 'complete']

function stageIndex(status) {
  const idx = STAGES.indexOf(status)
  return idx === -1 ? 0 : idx
}

export function PipelineTracker({ status }) {
  const isFailed = status === 'failed'
  // When failed, treat the furthest reached stage as current — derive from polling
  // The backend marks status as 'failed' after potentially advancing; default to index 0
  // We use the last known non-terminal status; since we only receive 'failed' here,
  // show the tracker stalled at 'queued' position (index 0) for safety — but the
  // job detail page should pass the last real status when available. For the component
  // itself, if status === 'failed' we highlight stage 0 in red.
  const currentIdx = isFailed ? 0 : stageIndex(status)

  return (
    <div className="flex items-center w-full py-2">
      {STAGES.map((stage, idx) => {
        const isDone = idx < currentIdx
        const isCurrent = idx === currentIdx
        const isAfter = idx > currentIdx

        // Connector line before each stage except the first
        const lineGreen = idx > 0 && idx <= currentIdx

        return (
          <div key={stage} className="flex items-center flex-1 last:flex-none">
            {/* Connector line */}
            {idx > 0 && (
              <div
                className={`flex-1 h-0.5 ${lineGreen ? 'bg-green-500' : 'bg-gray-700'}`}
              />
            )}

            {/* Circle + label */}
            <div className="flex flex-col items-center gap-1">
              <div
                className={[
                  'w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold transition-all',
                  isDone
                    ? 'bg-green-500 text-white'
                    : isCurrent && isFailed
                    ? 'bg-red-500 text-white ring-2 ring-red-400 ring-offset-2 ring-offset-gray-900'
                    : isCurrent
                    ? 'bg-blue-500 text-white ring-2 ring-blue-400 ring-offset-2 ring-offset-gray-900 animate-pulse'
                    : 'bg-gray-800 border-2 border-gray-600 text-gray-500',
                ].join(' ')}
              >
                {isDone ? '✓' : isCurrent && isFailed ? '✗' : idx + 1}
              </div>
              <span
                className={[
                  'text-xs whitespace-nowrap',
                  isDone
                    ? 'text-green-400'
                    : isCurrent && isFailed
                    ? 'text-red-400 font-bold'
                    : isCurrent
                    ? 'text-blue-400 font-bold'
                    : 'text-gray-600',
                ].join(' ')}
              >
                {stage.charAt(0).toUpperCase() + stage.slice(1)}
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )
}
