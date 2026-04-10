from __future__ import annotations

import inspect
import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def print_result(index: int, label: str, status: str) -> None:
    print(f"{index}. {label}: {status}")


def _base_valid_response() -> dict:
    return {
        "clips": [
            {
                "clip_id": 1,
                "start_time": "00:00:10",
                "end_time": "00:00:50",
                "start_seconds": 10,
                "end_seconds": 50,
                "duration_seconds": 40,
                "hook_summary": "Hook 1",
                "why_this_works": "Reason 1",
                "suggested_title": "Title 1",
            },
            {
                "clip_id": 2,
                "start_time": "00:01:10",
                "end_time": "00:01:55",
                "start_seconds": 70,
                "end_seconds": 115,
                "duration_seconds": 45,
                "hook_summary": "Hook 2",
                "why_this_works": "Reason 2",
                "suggested_title": "Title 2",
            },
            {
                "clip_id": 3,
                "start_time": "00:02:10",
                "end_time": "00:03:00",
                "start_seconds": 130,
                "end_seconds": 180,
                "duration_seconds": 50,
                "hook_summary": "Hook 3",
                "why_this_works": "Reason 3",
                "suggested_title": "Title 3",
            },
        ],
        "linkedin_short": "Short post",
        "linkedin_long": "Long post",
        "twitter_post": "Normal tweet",
        "twitter_thread": ["tweet 1", "tweet 2", "tweet 3"],
    }


def main() -> None:
    passed = 0

    # 1. gemini_analyzer imports without errors
    try:
        from app.services import gemini_analyzer  # noqa: F401

        print_result(1, "gemini_analyzer imports without errors", "PASS")
        passed += 1
    except Exception as exc:
        print_result(1, "gemini_analyzer imports without errors", f"FAIL ({exc})")
        print("0/10 checks passed.")
        return

    from app.services import gemini_analyzer

    # 2. GeminiAnalysisError instantiation/attributes
    try:
        err = gemini_analyzer.GeminiAnalysisError("X", "msg", True)
        ok = err.code == "X" and err.message == "msg" and err.retryable is True
        if ok:
            print_result(2, "GeminiAnalysisError instantiation/attributes", "PASS")
            passed += 1
        else:
            print_result(2, "GeminiAnalysisError instantiation/attributes", "FAIL")
    except Exception as exc:
        print_result(2, "GeminiAnalysisError instantiation/attributes", f"FAIL ({exc})")

    # 3. analyze_transcript raises MISSING_API_KEY when env var unset
    try:
        original_value = os.environ.pop("GEMINI_API_KEY", None)
        try:
            gemini_analyzer.analyze_transcript(
                transcript_string="[00:00:01] hello",
                video_title="Title",
                video_duration="00:10:00",
                channel_name="Channel",
            )
            print_result(3, "MISSING_API_KEY behavior", "FAIL (no exception)")
        except gemini_analyzer.GeminiAnalysisError as exc:
            if exc.code == "MISSING_API_KEY":
                print_result(3, "MISSING_API_KEY behavior", "PASS")
                passed += 1
            else:
                print_result(3, "MISSING_API_KEY behavior", f"FAIL ({exc.code})")
        finally:
            if original_value is not None:
                os.environ["GEMINI_API_KEY"] = original_value
    except Exception as exc:
        print_result(3, "MISSING_API_KEY behavior", f"FAIL ({exc})")

    # 4. SYSTEM_PROMPT exists and non-empty
    try:
        prompt = getattr(gemini_analyzer, "SYSTEM_PROMPT", "")
        if isinstance(prompt, str) and prompt.strip():
            print_result(4, "SYSTEM_PROMPT exists and non-empty", "PASS")
            passed += 1
        else:
            print_result(4, "SYSTEM_PROMPT exists and non-empty", "FAIL")
    except Exception as exc:
        print_result(4, "SYSTEM_PROMPT exists and non-empty", f"FAIL ({exc})")

    # 5. User prompt contains all interpolated variables
    try:
        built = gemini_analyzer._build_user_prompt(  # noqa: SLF001
            transcript_string="[00:00:01] transcript text",
            video_title="Video A",
            video_duration="00:12:34",
            channel_name="Channel B",
        )
        ok = all(
            token in built
            for token in (
                "Video A",
                "00:12:34",
                "Channel B",
                "[00:00:01] transcript text",
            )
        )
        if ok:
            print_result(5, "User prompt builds with filled variables", "PASS")
            passed += 1
        else:
            source = inspect.getsource(gemini_analyzer._build_user_prompt)  # noqa: SLF001
            print_result(5, "User prompt builds with filled variables", f"FAIL ({source[:80]})")
    except Exception as exc:
        print_result(5, "User prompt builds with filled variables", f"FAIL ({exc})")

    # 6. JSON validation missing clips -> INCOMPLETE_RESPONSE
    try:
        payload = _base_valid_response()
        payload.pop("clips")
        try:
            gemini_analyzer._validate_response(payload)  # noqa: SLF001
            print_result(6, "Missing keys validation", "FAIL (no exception)")
        except gemini_analyzer.GeminiAnalysisError as exc:
            if exc.code == "INCOMPLETE_RESPONSE":
                print_result(6, "Missing keys validation", "PASS")
                passed += 1
            else:
                print_result(6, "Missing keys validation", f"FAIL ({exc.code})")
    except Exception as exc:
        print_result(6, "Missing keys validation", f"FAIL ({exc})")

    # 7. clips count validation -> WRONG_CLIP_COUNT
    try:
        payload = _base_valid_response()
        payload["clips"] = payload["clips"][:2]
        try:
            gemini_analyzer._validate_response(payload)  # noqa: SLF001
            print_result(7, "Clips count validation", "FAIL (no exception)")
        except gemini_analyzer.GeminiAnalysisError as exc:
            if exc.code == "WRONG_CLIP_COUNT":
                print_result(7, "Clips count validation", "PASS")
                passed += 1
            else:
                print_result(7, "Clips count validation", f"FAIL ({exc.code})")
    except Exception as exc:
        print_result(7, "Clips count validation", f"FAIL ({exc})")

    # 8. Twitter truncation behavior
    try:
        payload = _base_valid_response()
        payload["twitter_post"] = "x" * 300
        validated = gemini_analyzer._validate_response(payload)  # noqa: SLF001
        tweet = validated.get("twitter_post", "")
        if len(tweet) == 280 and tweet.endswith("..."):
            print_result(8, "Twitter truncation to 280 chars", "PASS")
            passed += 1
        else:
            print_result(8, "Twitter truncation to 280 chars", f"FAIL (len={len(tweet)})")
    except Exception as exc:
        print_result(8, "Twitter truncation to 280 chars", f"FAIL ({exc})")

    # 9. update_job_analysis_results exists and callable
    try:
        from app.services import job_service

        fn = getattr(job_service, "update_job_analysis_results", None)
        if callable(fn):
            inspect.signature(fn)
            print_result(9, "update_job_analysis_results exists/callable", "PASS")
            passed += 1
        else:
            print_result(9, "update_job_analysis_results exists/callable", "FAIL")
    except Exception as exc:
        print_result(9, "update_job_analysis_results exists/callable", f"FAIL ({exc})")

    # 10. Required key set matches exactly
    try:
        expected = {
            "clips",
            "linkedin_short",
            "linkedin_long",
            "twitter_post",
            "twitter_thread",
        }
        actual = set(getattr(gemini_analyzer, "REQUIRED_RESPONSE_KEYS", set()))
        if actual == expected:
            print_result(10, "All required keys validated", "PASS")
            passed += 1
        else:
            print_result(10, "All required keys validated", f"FAIL (actual={sorted(actual)})")
    except Exception as exc:
        print_result(10, "All required keys validated", f"FAIL ({exc})")

    print(f"{passed}/10 checks passed.")


if __name__ == "__main__":
    main()
