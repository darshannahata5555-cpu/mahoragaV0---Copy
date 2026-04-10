from celery_app import celery_app


@celery_app.task(name="pipeline_worker.run_pipeline", bind=True)
def run_pipeline(self, job_id: str):
    """
    Main Celery task that orchestrates the full pipeline for a given job_id.

    Steps (implemented in Step 1+):
      1. Update job status → "extracting"
      2. Run yt-dlp to fetch subtitles + metadata
      3. Parse and normalize subtitle file
      4. Update job status → "analyzing"
      5. Build Gemini prompt with full transcript
      6. Call Gemini API
      7. Parse and validate Gemini JSON response
      8. Update job status → "complete", store all outputs
    """
    pass
