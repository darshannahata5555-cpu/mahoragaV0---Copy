import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export const POLL_INTERVAL_MS = 3000

export function submitJob(youtubeUrl) {
  return api.post('/jobs', { youtube_url: youtubeUrl }).then((r) => r.data)
}

export function getJob(jobId) {
  return api.get(`/jobs/${jobId}`).then((r) => r.data)
}

export function listJobs() {
  return api.get('/jobs').then((r) => r.data)
}

export function deleteJob(jobId) {
  return api.delete(`/jobs/${jobId}`).then((r) => r.data)
}

export function getTranscript(jobId) {
  return api.get(`/jobs/${jobId}/transcript`).then((r) => r.data)
}
