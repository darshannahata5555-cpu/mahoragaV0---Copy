const STATUS_CLASSES = {
  queued:     'bg-gray-700 text-gray-300',
  extracting: 'bg-blue-900 text-blue-300',
  analyzing:  'bg-yellow-900 text-yellow-300',
  complete:   'bg-green-900 text-green-300',
  failed:     'bg-red-900 text-red-300',
}

const PULSING_STATUSES = new Set(['extracting', 'analyzing'])

export function StatusBadge({ status }) {
  const colorClass = STATUS_CLASSES[status] ?? 'bg-gray-700 text-gray-300'
  const pulse = PULSING_STATUSES.has(status)

  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${colorClass}`}>
      {pulse && <span className="animate-pulse mr-1">●</span>}
      {status ? status.charAt(0).toUpperCase() + status.slice(1) : '—'}
    </span>
  )
}
