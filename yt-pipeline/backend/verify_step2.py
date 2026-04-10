from __future__ import annotations

import inspect
import sys
import tempfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


MINI_VTT = """WEBVTT

00:00:01.000 --> 00:00:04.000
<c>Hello</c> and welcome to <b>this</b> video.

00:00:04.000 --> 00:00:04.000
<c>Hello</c> and welcome to <b>this</b> video.

00:00:05.500 --> 00:00:09.000
Today we're going to talk about AI
"""

MINI_SRT = """1
00:00:01,000 --> 00:00:04,000
Hello and welcome to this video.

2
00:00:05,500 --> 00:00:09,000
Today we are talking about AI.
"""


def print_result(index: int, label: str, status: str) -> None:
    print(f"{index}. {label}: {status}")


def has_required_keys(item: dict) -> bool:
    required = {"index", "start", "end", "start_seconds", "end_seconds", "text"}
    return required.issubset(set(item.keys()))


def main() -> None:
    passed = 0

    # 1. subtitle_extractor imports without errors
    try:
        from app.services import subtitle_extractor  # noqa: F401

        print_result(1, "subtitle_extractor imports without errors", "PASS")
        passed += 1
    except Exception as exc:
        print_result(1, "subtitle_extractor imports without errors", f"FAIL ({exc})")

    # 2. ExtractionError can be instantiated and attributes are accessible
    try:
        from app.services.subtitle_extractor import ExtractionError

        err = ExtractionError("EXTRACTION_FAILED", "sample", False)
        ok = (
            err.code == "EXTRACTION_FAILED"
            and err.message == "sample"
            and err.retryable is False
        )
        if ok:
            print_result(2, "ExtractionError instantiation/attributes", "PASS")
            passed += 1
        else:
            print_result(2, "ExtractionError instantiation/attributes", "FAIL")
    except Exception as exc:
        print_result(2, "ExtractionError instantiation/attributes", f"FAIL ({exc})")

    # 3. subtitle_parser imports without errors
    try:
        from app.services import subtitle_parser  # noqa: F401

        print_result(3, "subtitle_parser imports without errors", "PASS")
        passed += 1
    except Exception as exc:
        print_result(3, "subtitle_parser imports without errors", f"FAIL ({exc})")

    # 4. VTT parsing structure and float start_seconds
    try:
        from app.services.subtitle_parser import parse_subtitles

        with tempfile.TemporaryDirectory() as tmp_dir:
            vtt_path = Path(tmp_dir) / "sample.vtt"
            vtt_path.write_text(MINI_VTT, encoding="utf-8")
            cues = parse_subtitles(str(vtt_path), "vtt")

        ok = bool(cues) and has_required_keys(cues[0]) and isinstance(
            cues[0]["start_seconds"], float
        )
        if ok:
            print_result(4, "VTT parsing returns structured cues", "PASS")
            passed += 1
        else:
            print_result(4, "VTT parsing returns structured cues", "FAIL")
    except Exception as exc:
        print_result(4, "VTT parsing returns structured cues", f"FAIL ({exc})")
        cues = []

    # 5. VTT parsing strips HTML tags
    try:
        no_tags = all("<" not in cue["text"] and ">" not in cue["text"] for cue in cues)
        if cues and no_tags:
            print_result(5, "VTT parsing strips HTML tags", "PASS")
            passed += 1
        else:
            print_result(5, "VTT parsing strips HTML tags", "FAIL")
    except Exception as exc:
        print_result(5, "VTT parsing strips HTML tags", f"FAIL ({exc})")

    # 6. SRT parsing structure
    try:
        from app.services.subtitle_parser import parse_subtitles

        with tempfile.TemporaryDirectory() as tmp_dir:
            srt_path = Path(tmp_dir) / "sample.srt"
            srt_path.write_text(MINI_SRT, encoding="utf-8")
            srt_cues = parse_subtitles(str(srt_path), "srt")

        ok = bool(srt_cues) and has_required_keys(srt_cues[0]) and isinstance(
            srt_cues[0]["start_seconds"], float
        )
        if ok:
            print_result(6, "SRT parsing returns structured cues", "PASS")
            passed += 1
        else:
            print_result(6, "SRT parsing returns structured cues", "FAIL")
    except Exception as exc:
        print_result(6, "SRT parsing returns structured cues", f"FAIL ({exc})")

    # 7. Duplicate cue removal
    try:
        from app.services.subtitle_parser import parse_subtitles

        duplicate_vtt = """WEBVTT

00:00:01.000 --> 00:00:02.000
Hello world.

00:00:02.000 --> 00:00:03.000
Hello world.
"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            dup_path = Path(tmp_dir) / "dup.vtt"
            dup_path.write_text(duplicate_vtt, encoding="utf-8")
            dup_cues = parse_subtitles(str(dup_path), "vtt")
        if len(dup_cues) == 1:
            print_result(7, "Duplicate consecutive cue removal", "PASS")
            passed += 1
        else:
            print_result(7, "Duplicate consecutive cue removal", f"FAIL (len={len(dup_cues)})")
    except Exception as exc:
        print_result(7, "Duplicate consecutive cue removal", f"FAIL ({exc})")

    # 8. build_transcript_string format
    try:
        from app.services.subtitle_parser import build_transcript_string

        transcript = build_transcript_string(cues)
        starts_ok = bool(transcript) and all(
            line.startswith("[") for line in transcript.splitlines() if line.strip()
        )
        if starts_ok:
            print_result(8, "build_transcript_string line format", "PASS")
            passed += 1
        else:
            print_result(8, "build_transcript_string line format", "FAIL")
    except Exception as exc:
        print_result(8, "build_transcript_string line format", f"FAIL ({exc})")

    # 9. count_words correctness
    try:
        from app.services.subtitle_parser import count_words

        words = count_words("[00:00:01] hello world")
        if words == 2:
            print_result(9, "count_words returns correct integer", "PASS")
            passed += 1
        else:
            print_result(9, "count_words returns correct integer", f"FAIL ({words})")
    except Exception as exc:
        print_result(9, "count_words returns correct integer", f"FAIL ({exc})")

    # 10. update_job_extraction_results exists/callable
    try:
        from app.services import job_service

        fn = getattr(job_service, "update_job_extraction_results", None)
        if callable(fn):
            inspect.signature(fn)
            print_result(10, "update_job_extraction_results exists and is callable", "PASS")
            passed += 1
        else:
            print_result(
                10,
                "update_job_extraction_results exists and is callable",
                "FAIL",
            )
    except Exception as exc:
        print_result(
            10,
            "update_job_extraction_results exists and is callable",
            f"FAIL ({exc})",
        )

    print(f"{passed}/10 checks passed.")


if __name__ == "__main__":
    main()
