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

// 1. jobsApi.js exports
const apiFile = read('api/jobsApi.js')
check(
  1,
  'jobsApi.js exports: submitJob, getJob, listJobs, deleteJob, getTranscript, POLL_INTERVAL_MS',
  apiFile !== null &&
    apiFile.includes('submitJob') &&
    apiFile.includes('getJob') &&
    apiFile.includes('listJobs') &&
    apiFile.includes('deleteJob') &&
    apiFile.includes('getTranscript') &&
    apiFile.includes('POLL_INTERVAL_MS'),
  'missing one or more exports'
)

// 2. useJobPolling.js exists and exports useJobPolling
const hookFile = read('hooks/useJobPolling.js')
check(
  2,
  'useJobPolling.js exists and exports useJobPolling',
  hookFile !== null && hookFile.includes('useJobPolling'),
  'file missing or export not found'
)

// 3. StatusBadge.jsx exists
const badgeFile = read('components/StatusBadge.jsx')
check(
  3,
  'StatusBadge.jsx exists',
  badgeFile !== null,
  'file not found'
)

// 4. SubmitPage.jsx contains required elements
const submitFile = read('pages/SubmitPage.jsx')
check(
  4,
  'SubmitPage.jsx contains: submitJob, "Analyze Video", navigate',
  submitFile !== null &&
    submitFile.includes('submitJob') &&
    submitFile.includes('Analyze Video') &&
    submitFile.includes('navigate'),
  'missing one or more required strings'
)

// 5. JobListPage.jsx contains required elements
const listFile = read('pages/JobListPage.jsx')
check(
  5,
  'JobListPage.jsx contains: listJobs, deleteJob, StatusBadge',
  listFile !== null &&
    listFile.includes('listJobs') &&
    listFile.includes('deleteJob') &&
    listFile.includes('StatusBadge'),
  'missing one or more required strings'
)

// 6. StatusBadge.jsx contains all 5 status color variants
check(
  6,
  'StatusBadge.jsx contains all 5 status variants: queued, extracting, analyzing, complete, failed',
  badgeFile !== null &&
    badgeFile.includes('queued') &&
    badgeFile.includes('extracting') &&
    badgeFile.includes('analyzing') &&
    badgeFile.includes('complete') &&
    badgeFile.includes('failed'),
  'one or more status variants missing'
)

// 7. useJobPolling.js contains interval logic
check(
  7,
  'useJobPolling.js contains: POLL_INTERVAL_MS, setInterval, clearInterval',
  hookFile !== null &&
    hookFile.includes('POLL_INTERVAL_MS') &&
    hookFile.includes('setInterval') &&
    hookFile.includes('clearInterval'),
  'missing polling primitives'
)

// 8. jobsApi.js uses relative paths only (no hardcoded localhost/port)
check(
  8,
  'jobsApi.js uses relative paths only (no localhost or 8000)',
  apiFile !== null &&
    !apiFile.includes('localhost') &&
    !apiFile.includes('8000'),
  'found hardcoded localhost or port'
)

// 9. App.jsx contains all 3 routes
const appFile = read('App.jsx')
check(
  9,
  'App.jsx contains all 3 routes: /, /jobs, /jobs/:id',
  appFile !== null &&
    appFile.includes('path="/"') &&
    appFile.includes('path="/jobs"') &&
    appFile.includes('path="/jobs/:id"'),
  'one or more routes missing'
)

// 10. JobListPage.jsx contains View, Delete, toLocaleDateString
check(
  10,
  'JobListPage.jsx contains: "View", "Delete", toLocaleDateString',
  listFile !== null &&
    listFile.includes('View') &&
    listFile.includes('Delete') &&
    listFile.includes('toLocaleDateString'),
  'missing one or more required strings'
)

console.log(`\n${passed}/10 checks passed.`)

if (passed === 10) {
  console.log(`
==========================================
  STEP 6 FRONTEND: ALL CHECKS PASSED
==========================================`)
}
