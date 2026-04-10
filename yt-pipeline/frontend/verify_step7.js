import { readFileSync, existsSync } from 'fs'
import { join } from 'path'

const SRC = join(process.cwd(), 'src')
let passed = 0

function read(rel) {
  const abs = join(SRC, rel)
  if (!existsSync(abs)) return null
  return readFileSync(abs, 'utf8')
}

function check(index, label, condition, detail) {
  if (condition) {
    console.log(`${index}. ${label}: PASS`)
    passed++
  } else {
    console.log(`${index}. ${label}: FAIL${detail ? ` (${detail})` : ''}`)
  }
}

const trackerFile  = read('components/PipelineTracker.jsx')
const clipFile     = read('components/ClipCard.jsx')
const socialFile   = read('components/SocialPostsPanel.jsx')
const transcriptFile = read('components/TranscriptViewer.jsx')
const detailFile   = read('pages/JobDetailPage.jsx')

// 1. PipelineTracker has all 4 stage names
check(
  1,
  'PipelineTracker.jsx exists and contains all 4 stage names: queued, extracting, analyzing, complete',
  trackerFile !== null &&
    trackerFile.includes('queued') &&
    trackerFile.includes('extracting') &&
    trackerFile.includes('analyzing') &&
    trackerFile.includes('complete'),
  'file missing or stage names absent'
)

// 2. ClipCard has YouTube link + start_seconds + Copy Timestamp + Copied!
check(
  2,
  'ClipCard.jsx contains: youtube.com/watch, start_seconds, Copy Timestamp, Copied!',
  clipFile !== null &&
    clipFile.includes('youtube.com/watch') &&
    clipFile.includes('start_seconds') &&
    clipFile.includes('Copy Timestamp') &&
    clipFile.includes('Copied!'),
  'missing one or more required strings'
)

// 3. SocialPostsPanel has all 4 tab labels
check(
  3,
  'SocialPostsPanel.jsx contains all 4 tab labels: LinkedIn Short, LinkedIn Long, Twitter Post, Twitter Thread',
  socialFile !== null &&
    socialFile.includes('LinkedIn Short') &&
    socialFile.includes('LinkedIn Long') &&
    socialFile.includes('Twitter Post') &&
    socialFile.includes('Twitter Thread'),
  'missing one or more tab labels'
)

// 4. SocialPostsPanel has copy logic
check(
  4,
  'SocialPostsPanel.jsx contains Copy to Clipboard and Copied!',
  socialFile !== null &&
    socialFile.includes('Copy to Clipboard') &&
    socialFile.includes('Copied!'),
  'copy functionality missing'
)

// 5. TranscriptViewer has required elements
check(
  5,
  'TranscriptViewer.jsx contains: getTranscript, Search transcript, isOpen or collapsed or showTranscript',
  transcriptFile !== null &&
    transcriptFile.includes('getTranscript') &&
    transcriptFile.includes('Search transcript') &&
    (transcriptFile.includes('isOpen') ||
      transcriptFile.includes('collapsed') ||
      transcriptFile.includes('showTranscript')),
  'file missing or required strings absent'
)

// 6. JobDetailPage imports all sub-components
check(
  6,
  'JobDetailPage.jsx contains: useParams, useJobPolling, PipelineTracker, ClipCard, SocialPostsPanel, TranscriptViewer',
  detailFile !== null &&
    detailFile.includes('useParams') &&
    detailFile.includes('useJobPolling') &&
    detailFile.includes('PipelineTracker') &&
    detailFile.includes('ClipCard') &&
    detailFile.includes('SocialPostsPanel') &&
    detailFile.includes('TranscriptViewer'),
  'missing one or more imports/usages'
)

// 7. JobDetailPage handles all 3 terminal states
check(
  7,
  'JobDetailPage.jsx handles all 3 states: "failed", "complete", "Loading"',
  detailFile !== null &&
    detailFile.includes('failed') &&
    detailFile.includes('complete') &&
    detailFile.includes('Loading'),
  'missing one or more state handlers'
)

// 8. ClipCard uses navigator.clipboard.writeText
check(
  8,
  'ClipCard.jsx contains navigator.clipboard.writeText',
  clipFile !== null && clipFile.includes('navigator.clipboard.writeText'),
  'clipboard API not found'
)

// 9. SocialPostsPanel uses navigator.clipboard.writeText
check(
  9,
  'SocialPostsPanel.jsx contains navigator.clipboard.writeText',
  socialFile !== null && socialFile.includes('navigator.clipboard.writeText'),
  'clipboard API not found'
)

// 10. JobDetailPage has back navigation
check(
  10,
  'JobDetailPage.jsx contains "← Back" or "Back to Jobs"',
  detailFile !== null &&
    (detailFile.includes('← Back') || detailFile.includes('Back to Jobs')),
  'back navigation not found'
)

console.log(`\n${passed}/10 checks passed.`)

if (passed === 10) {
  console.log(`
==========================================
  STEP 7 FRONTEND: ALL CHECKS PASSED
==========================================`)
}
