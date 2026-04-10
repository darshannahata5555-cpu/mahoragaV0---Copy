import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.job import JobCreate, JobListItem, JobResponse
from app.services import job_service
from app.workers.pipeline_worker import run_pipeline

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
def create_job(payload: JobCreate, db: Session = Depends(get_db)) -> JobResponse:
    job = job_service.create_job(db, payload.youtube_url)
    run_pipeline.delay(job.id)
    return JobResponse.model_validate(job)


@router.get("", response_model=list[JobListItem])
def list_jobs(db: Session = Depends(get_db)) -> list[JobListItem]:
    jobs = job_service.list_jobs(db)
    return [JobListItem.model_validate(job) for job in jobs]


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)) -> JobResponse:
    job = job_service.get_job(db, job_id)
    return JobResponse.model_validate(job)


@router.delete("/{job_id}")
def delete_job(job_id: str, db: Session = Depends(get_db)) -> dict:
    job_service.delete_job(db, job_id)
    return {"message": "Job deleted"}


@router.get("/{job_id}/transcript")
def get_transcript(job_id: str, db: Session = Depends(get_db)) -> JSONResponse:
    job = job_service.get_job(db, job_id)
    if not job.transcript_file_path:
        raise HTTPException(status_code=404, detail="Transcript not available")

    transcript_path = Path(job.transcript_file_path)
    if not transcript_path.exists():
        raise HTTPException(status_code=404, detail="Transcript not available")

    transcript_data = json.loads(transcript_path.read_text(encoding="utf-8"))
    return JSONResponse(content=transcript_data)
