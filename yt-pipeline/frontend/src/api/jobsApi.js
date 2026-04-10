import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

/** Submit a new YouTube URL for processing. Returns { job_id }. */
export const createJob = async (youtubeUrl) => {
  // TODO: implement in Step 1
}

/** Poll a job by ID for status and results. */
export const getJob = async (jobId) => {
  // TODO: implement in Step 1
}

/** List all past jobs. */
export const listJobs = async () => {
  // TODO: implement in Step 1
}

/** Delete a job by ID. */
export const deleteJob = async (jobId) => {
  // TODO: implement in Step 1
}

/** Fetch the raw parsed transcript for a job. */
export const getTranscript = async (jobId) => {
  // TODO: implement in Step 1
}

/** Fetch the generated clip recommendations for a job. */
export const getClips = async (jobId) => {
  // TODO: implement in Step 1
}

export default api
