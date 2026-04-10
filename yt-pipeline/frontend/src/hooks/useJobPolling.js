import { useState, useEffect, useRef } from 'react'
import { getJob, POLL_INTERVAL_MS } from '../api/jobsApi'

export function useJobPolling(jobId, onComplete) {
  const [job, setJob] = useState(null)
  const [isPolling, setIsPolling] = useState(false)
  const [error, setError] = useState(null)
  const onCompleteRef = useRef(onComplete)

  useEffect(() => {
    onCompleteRef.current = onComplete
  }, [onComplete])

  useEffect(() => {
    if (!jobId) {
      setJob(null)
      setIsPolling(false)
      setError(null)
      return
    }

    setIsPolling(true)
    setError(null)

    const intervalId = setInterval(async () => {
      try {
        const data = await getJob(jobId)
        setJob(data)
        if (data.status === 'complete' || data.status === 'failed') {
          clearInterval(intervalId)
          setIsPolling(false)
          onCompleteRef.current(data)
        }
      } catch (err) {
        setError(err)
        clearInterval(intervalId)
        setIsPolling(false)
      }
    }, POLL_INTERVAL_MS)

    return () => {
      clearInterval(intervalId)
      setIsPolling(false)
    }
  }, [jobId])

  return { job, isPolling, error }
}
