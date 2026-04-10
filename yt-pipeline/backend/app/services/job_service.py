import hashlib
import os

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.job import Job


def create_job(db: Session, youtube_url: str) -> Job:
    url_hash = hashlib.sha256(youtube_url.encode()).hexdigest()
    job = Job(youtube_url=youtube_url, url_hash=url_hash, status="queued")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: str) -> Job:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


def list_jobs(db: Session) -> list[Job]:
    return db.query(Job).order_by(Job.created_at.desc()).all()


def delete_job(db: Session, job_id: str) -> None:
    job = get_job(db, job_id)

    if job.raw_subtitle_path and os.path.exists(job.raw_subtitle_path):
        os.remove(job.raw_subtitle_path)

    if job.transcript_file_path and os.path.exists(job.transcript_file_path):
        os.remove(job.transcript_file_path)

    db.delete(job)
    db.commit()


def set_job_error(
    db: Session, job: Job, code: str, message: str, retryable: bool
) -> Job:
    job.error_code = code
    job.error_message = message
    job.error_retryable = retryable
    job.status = "failed"
    db.commit()
    db.refresh(job)
    return job


def update_job_extraction_results(
    db: Session,
    job: Job,
    video_title: str,
    video_duration: str,
    channel_name: str,
    video_id: str,
    raw_subtitle_path: str,
    transcript_file_path: str,
    transcript_word_count: int,
) -> Job:
    job.video_title = video_title
    job.video_duration = video_duration
    job.channel_name = channel_name
    job.video_id = video_id
    job.raw_subtitle_path = raw_subtitle_path
    job.transcript_file_path = transcript_file_path
    job.transcript_word_count = transcript_word_count
    job.status = "extracting"

    db.commit()
    db.refresh(job)
    return job


def update_job_analysis_results(
    db: Session,
    job: Job,
    output_clips: list,
    output_linkedin_short: str,
    output_linkedin_long: str,
    output_twitter_post: str,
    output_twitter_thread: list,
) -> Job:
    job.output_clips = output_clips
    job.output_linkedin_short = output_linkedin_short
    job.output_linkedin_long = output_linkedin_long
    job.output_twitter_post = output_twitter_post
    job.output_twitter_thread = output_twitter_thread
    job.status = "complete"

    db.commit()
    db.refresh(job)
    return job
