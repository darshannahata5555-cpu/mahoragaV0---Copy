import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer, JSON, String, Text

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('queued', 'extracting', 'analyzing', 'complete', 'failed')",
            name="jobs_status_check",
        ),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, nullable=False, default="queued")
    youtube_url = Column(String, nullable=False)
    url_hash = Column(String, nullable=True, index=True)
    video_title = Column(String, nullable=True)
    video_duration = Column(String, nullable=True)
    channel_name = Column(String, nullable=True)
    video_id = Column(String, nullable=True)

    raw_subtitle_path = Column(String, nullable=True)
    transcript_file_path = Column(String, nullable=True)
    transcript_word_count = Column(Integer, nullable=True)

    output_clips = Column(JSON, nullable=True)
    output_linkedin_short = Column(Text, nullable=True)
    output_linkedin_long = Column(Text, nullable=True)
    output_twitter_post = Column(Text, nullable=True)
    output_twitter_thread = Column(JSON, nullable=True)

    error_code = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    error_retryable = Column(Boolean, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
