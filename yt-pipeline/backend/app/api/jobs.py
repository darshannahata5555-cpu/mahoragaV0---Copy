from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("")
def create_job(db: Session = Depends(get_db)):
    """Submit a new YouTube URL for processing. Returns a job_id."""
    pass


@router.get("")
def list_jobs(db: Session = Depends(get_db)):
    """List all past jobs."""
    pass


@router.get("/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    """Poll job status and results by job_id."""
    pass


@router.delete("/{job_id}")
def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Remove a job and its associated outputs."""
    pass


@router.get("/{job_id}/transcript")
def get_transcript(job_id: str, db: Session = Depends(get_db)):
    """Download the raw parsed transcript for a job."""
    pass


@router.get("/{job_id}/clips")
def get_clips(job_id: str, db: Session = Depends(get_db)):
    """Get the generated clip recommendations for a job."""
    pass
