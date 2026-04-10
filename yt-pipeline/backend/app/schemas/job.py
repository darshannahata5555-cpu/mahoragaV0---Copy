from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class JobCreate(BaseModel):
    youtube_url: str

    @field_validator("youtube_url")
    @classmethod
    def validate_youtube_url(cls, value: str) -> str:
        if "youtube.com/watch" not in value and "youtu.be" not in value:
            raise ValueError(
                "Invalid YouTube URL. Must be a youtube.com/watch or youtu.be link."
            )
        return value

    model_config = ConfigDict(from_attributes=True)


class ErrorDetail(BaseModel):
    code: str | None = None
    message: str | None = None
    retryable: bool | None = None

    model_config = ConfigDict(from_attributes=True)


class ClipOutput(BaseModel):
    clip_id: int
    start_time: str
    end_time: str
    start_seconds: int
    end_seconds: int
    duration_seconds: int
    hook_summary: str
    why_this_works: str
    suggested_title: str

    model_config = ConfigDict(from_attributes=True)


class JobResponse(BaseModel):
    id: str
    status: str
    youtube_url: str
    video_title: str | None = None
    video_duration: str | None = None
    channel_name: str | None = None
    video_id: str | None = None
    transcript_word_count: int | None = None
    output_clips: list[ClipOutput] | None = None
    output_linkedin_short: str | None = None
    output_linkedin_long: str | None = None
    output_twitter_post: str | None = None
    output_twitter_thread: list[str] | None = None
    created_at: datetime
    updated_at: datetime

    error_code: str | None = Field(default=None, exclude=True)
    error_message: str | None = Field(default=None, exclude=True)
    error_retryable: bool | None = Field(default=None, exclude=True)

    @computed_field(return_type=ErrorDetail | None)
    @property
    def error(self) -> ErrorDetail | None:
        if (
            self.error_code is None
            and self.error_message is None
            and self.error_retryable is None
        ):
            return None
        return ErrorDetail(
            code=self.error_code,
            message=self.error_message,
            retryable=self.error_retryable,
        )

    model_config = ConfigDict(from_attributes=True)


class JobListItem(BaseModel):
    id: str
    status: str
    youtube_url: str
    video_title: str | None = None
    channel_name: str | None = None
    video_duration: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
