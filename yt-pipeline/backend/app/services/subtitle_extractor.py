import json
import subprocess
from pathlib import Path


class ExtractionError(Exception):
    def __init__(self, code: str, message: str, retryable: bool):
        self.code = code
        self.message = message
        self.retryable = retryable
        super().__init__(message)


def _format_duration(duration_seconds: int | float | None) -> str:
    total = int(duration_seconds or 0)
    hours = total // 3600
    minutes = (total % 3600) // 60
    seconds = total % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def _parse_print_json_output(stdout: str) -> dict:
    for line in reversed(stdout.splitlines()):
        candidate = line.strip()
        if not candidate:
            continue
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return {}


def _pick_subtitle_file(job_dir: Path) -> Path | None:
    candidates = sorted(
        list(job_dir.glob("*.vtt")) + list(job_dir.glob("*.srt")),
        key=lambda path: path.name.lower(),
    )
    if not candidates:
        return None

    preferred = [
        path
        for path in candidates
        if ".auto" not in path.name.lower() and ".live_chat" not in path.name.lower()
    ]
    return (preferred or candidates)[0]


def extract_subtitles(job_id: str, youtube_url: str, output_dir: str) -> dict:
    job_dir = Path(output_dir) / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(job_dir / "subtitles")
    cmd = [
        "yt-dlp",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs",
        "en",
        "--sub-format",
        "srt/vtt",
        "--skip-download",
        "--output",
        output_template,
        "--print-json",
        youtube_url,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ExtractionError(
            code="EXTRACTION_FAILED",
            message=f"yt-dlp timed out after 120 seconds: {str(exc)[:500]}",
            retryable=False,
        ) from exc

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()[:500]
        raise ExtractionError(
            code="EXTRACTION_FAILED",
            message=stderr or "yt-dlp extraction failed",
            retryable=False,
        )

    metadata = _parse_print_json_output(result.stdout or "")
    subtitle_file = _pick_subtitle_file(job_dir)
    if subtitle_file is None:
        raise ExtractionError(
            code="NO_SUBTITLES",
            message="No subtitles available for this video",
            retryable=False,
        )

    return {
        "video_title": metadata.get("title", ""),
        "video_duration": _format_duration(metadata.get("duration")),
        "channel_name": metadata.get("channel") or metadata.get("uploader") or "",
        "video_id": metadata.get("id", ""),
        "subtitle_file_path": str(subtitle_file.resolve()),
        "subtitle_format": subtitle_file.suffix.lstrip(".").lower(),
    }
