from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def print_result(index: int, label: str, status: str) -> None:
    print(f"{index}. {label}: {status}")


def main() -> None:
    passed = 0

    # 1. Job model imports without errors
    try:
        from app.models.job import Job  # noqa: F401

        print_result(1, "Job model imports without errors", "PASS")
        passed += 1
    except Exception as exc:
        print_result(1, "Job model imports without errors", f"FAIL ({exc})")
        Job = None  # type: ignore[assignment]

    # 2. Job model has all required columns
    try:
        required_columns = {
            "id",
            "status",
            "youtube_url",
            "url_hash",
            "video_title",
            "video_duration",
            "channel_name",
            "video_id",
            "raw_subtitle_path",
            "transcript_file_path",
            "transcript_word_count",
            "output_clips",
            "output_linkedin_short",
            "output_linkedin_long",
            "output_twitter_post",
            "output_twitter_thread",
            "error_code",
            "error_message",
            "error_retryable",
            "created_at",
            "updated_at",
        }
        model_columns = set(Job.__table__.columns.keys())  # type: ignore[union-attr]
        missing = sorted(required_columns - model_columns)
        extra = sorted(model_columns - required_columns)
        if not missing and not extra:
            print_result(2, "Job model has all required columns", "PASS")
            passed += 1
        else:
            detail = f"missing={missing}, extra={extra}"
            print_result(2, "Job model has all required columns", f"FAIL ({detail})")
    except Exception as exc:
        print_result(2, "Job model has all required columns", f"FAIL ({exc})")

    # 3-8. Schema checks
    try:
        from app.schemas.job import ClipOutput, ErrorDetail, JobCreate, JobResponse

        # 3. JobCreate rejects invalid URL
        try:
            JobCreate(youtube_url="https://google.com")
            print_result(3, "JobCreate rejects invalid URL", "FAIL (accepted invalid URL)")
        except Exception:
            print_result(3, "JobCreate rejects invalid URL", "PASS")
            passed += 1

        # 4. JobCreate accepts valid youtube.com/watch URL
        try:
            JobCreate(youtube_url="https://www.youtube.com/watch?v=test")
            print_result(4, "JobCreate accepts youtube.com/watch URL", "PASS")
            passed += 1
        except Exception as exc:
            print_result(4, "JobCreate accepts youtube.com/watch URL", f"FAIL ({exc})")

        # 5. JobCreate accepts youtu.be URL
        try:
            JobCreate(youtube_url="https://youtu.be/test123")
            print_result(5, "JobCreate accepts youtu.be URL", "PASS")
            passed += 1
        except Exception as exc:
            print_result(5, "JobCreate accepts youtu.be URL", f"FAIL ({exc})")

        # 6. ErrorDetail schema instantiates correctly
        try:
            err = ErrorDetail(code="ERR_TEST", message="Test message", retryable=True)
            ok = (
                err.code == "ERR_TEST"
                and err.message == "Test message"
                and err.retryable is True
            )
            if ok:
                print_result(6, "ErrorDetail schema instantiates correctly", "PASS")
                passed += 1
            else:
                print_result(6, "ErrorDetail schema instantiates correctly", "FAIL")
        except Exception as exc:
            print_result(6, "ErrorDetail schema instantiates correctly", f"FAIL ({exc})")

        # 7. ClipOutput schema instantiates correctly
        try:
            clip = ClipOutput(
                clip_id=1,
                start_time="00:00:10",
                end_time="00:00:40",
                start_seconds=10,
                end_seconds=40,
                duration_seconds=30,
                hook_summary="Strong opening hook",
                why_this_works="High curiosity gap and clear payoff",
                suggested_title="The 30-second insight",
            )
            if clip.duration_seconds == 30:
                print_result(7, "ClipOutput schema instantiates correctly", "PASS")
                passed += 1
            else:
                print_result(7, "ClipOutput schema instantiates correctly", "FAIL")
        except Exception as exc:
            print_result(7, "ClipOutput schema instantiates correctly", f"FAIL ({exc})")

        # 8. JobResponse has a computed "error" field
        try:
            computed_fields = getattr(JobResponse, "model_computed_fields", {})
            sample = JobResponse(
                id="job-1",
                status="failed",
                youtube_url="https://www.youtube.com/watch?v=test",
                video_title=None,
                video_duration=None,
                channel_name=None,
                video_id=None,
                transcript_word_count=None,
                output_clips=None,
                output_linkedin_short=None,
                output_linkedin_long=None,
                output_twitter_post=None,
                output_twitter_thread=None,
                error_code="E001",
                error_message="Sample failure",
                error_retryable=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            dumped = sample.model_dump()
            has_error_computed = "error" in computed_fields
            error_ok = dumped.get("error") == {
                "code": "E001",
                "message": "Sample failure",
                "retryable": False,
            }
            if has_error_computed and error_ok:
                print_result(8, "JobResponse schema has computed error field", "PASS")
                passed += 1
            else:
                print_result(
                    8,
                    "JobResponse schema has computed error field",
                    f"FAIL (computed={has_error_computed}, dumped_error={dumped.get('error')})",
                )
        except Exception as exc:
            print_result(8, "JobResponse schema has computed error field", f"FAIL ({exc})")

    except Exception as exc:
        print_result(3, "JobCreate rejects invalid URL", f"FAIL ({exc})")
        print_result(4, "JobCreate accepts youtube.com/watch URL", f"FAIL ({exc})")
        print_result(5, "JobCreate accepts youtu.be URL", f"FAIL ({exc})")
        print_result(6, "ErrorDetail schema instantiates correctly", f"FAIL ({exc})")
        print_result(7, "ClipOutput schema instantiates correctly", f"FAIL ({exc})")
        print_result(8, "JobResponse schema has computed error field", f"FAIL ({exc})")

    # 9. job_service imports without errors
    try:
        from app.services import job_service  # noqa: F401

        print_result(9, "job_service imports without errors", "PASS")
        passed += 1
    except Exception as exc:
        print_result(9, "job_service imports without errors", f"FAIL ({exc})")

    # 10. db_init.py runs cleanly (or skip if postgres unreachable)
    try:
        result = subprocess.run(
            [sys.executable, "db_init.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        combined_output = (result.stdout + "\n" + result.stderr).lower()
        if result.returncode == 0 and "database tables created successfully." in combined_output:
            print_result(10, "db_init.py runs cleanly", "PASS")
            passed += 1
        elif any(
            token in combined_output
            for token in (
                "postgres",
                "psycopg",
                "connection refused",
                "could not connect",
                "connection to server",
                "operationalerror",
            )
        ):
            print_result(10, "db_init.py runs cleanly", "SKIP — postgres not reachable")
        else:
            detail = (result.stdout + "\n" + result.stderr).strip().replace("\n", " | ")
            print_result(10, "db_init.py runs cleanly", f"FAIL ({detail})")
    except Exception as exc:
        print_result(10, "db_init.py runs cleanly", f"FAIL ({exc})")

    print(f"{passed}/10 checks passed.")


if __name__ == "__main__":
    main()
