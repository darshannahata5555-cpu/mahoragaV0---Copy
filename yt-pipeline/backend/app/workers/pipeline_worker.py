import json
import os
from pathlib import Path

from dotenv import load_dotenv

from app.database import SessionLocal
from app.services import gemini_analyzer, job_service, subtitle_extractor, subtitle_parser
from celery_app import celery_app

load_dotenv()


@celery_app.task(name="pipeline_worker.run_pipeline")
def run_pipeline(job_id: str):
    db = SessionLocal()
    try:
        try:
            job = job_service.get_job(db, job_id)
        except Exception as exc:
            print(f"[pipeline] Job {job_id} not found or unavailable: {exc}")
            return

        output_dir = os.environ.get("OUTPUT_DIR", "./outputs")

        # Stage 2: Extraction
        job.status = "extracting"
        db.commit()
        db.refresh(job)
        try:
            extraction_result = subtitle_extractor.extract_subtitles(
                job_id=job_id,
                youtube_url=job.youtube_url,
                output_dir=output_dir,
            )
        except subtitle_extractor.ExtractionError as exc:
            job_service.set_job_error(db, job, exc.code, exc.message, exc.retryable)
            return
        except Exception as exc:
            job_service.set_job_error(db, job, "UNKNOWN_ERROR", str(exc), False)
            return

        # Stage 3: Parsing
        try:
            cues = subtitle_parser.parse_subtitles(
                extraction_result["subtitle_file_path"],
                extraction_result["subtitle_format"],
            )
            transcript_string = subtitle_parser.build_transcript_string(cues)
            transcript_word_count = subtitle_parser.count_words(transcript_string)

            transcript_path = Path(output_dir) / job_id / "transcript.json"
            transcript_path.parent.mkdir(parents=True, exist_ok=True)
            transcript_path.write_text(json.dumps(cues, indent=2), encoding="utf-8")

            job = job_service.update_job_extraction_results(
                db=db,
                job=job,
                video_title=extraction_result["video_title"],
                video_duration=extraction_result["video_duration"],
                channel_name=extraction_result["channel_name"],
                video_id=extraction_result["video_id"],
                raw_subtitle_path=extraction_result["subtitle_file_path"],
                transcript_file_path=str(transcript_path.resolve()),
                transcript_word_count=transcript_word_count,
            )
        except Exception as exc:
            job_service.set_job_error(db, job, "PARSE_ERROR", str(exc), False)
            return

        # Stage 4: Analysis
        job.status = "analyzing"
        db.commit()
        db.refresh(job)
        try:
            analysis_result = gemini_analyzer.analyze_transcript(
                transcript_string=transcript_string,
                video_title=job.video_title or "",
                video_duration=job.video_duration or "",
                channel_name=job.channel_name or "",
            )
        except gemini_analyzer.GeminiAnalysisError as exc:
            job_service.set_job_error(db, job, exc.code, exc.message, exc.retryable)
            return
        except Exception as exc:
            job_service.set_job_error(db, job, "ANALYSIS_ERROR", str(exc), False)
            return

        # Stage 5: Completion
        job_service.update_job_analysis_results(
            db=db,
            job=job,
            output_clips=analysis_result["clips"],
            output_linkedin_short=analysis_result["linkedin_short"],
            output_linkedin_long=analysis_result["linkedin_long"],
            output_twitter_post=analysis_result["twitter_post"],
            output_twitter_thread=analysis_result["twitter_thread"],
        )
        print(f"[pipeline] Job {job_id} complete.")
    finally:
        db.close()
