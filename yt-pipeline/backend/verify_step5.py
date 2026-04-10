import json
import re
import sys
import time

import httpx


BASE_URL = "http://localhost:8000"
TEST_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
POLL_INTERVAL = 3
MAX_WAIT = 300


def print_result(index: int, label: str, status: str) -> None:
    print(f"{index}. {label}: {status}")


def main() -> None:
    passed = 0
    job_id = None
    completed_job = None

    with httpx.Client(timeout=30.0) as client:
        # 1. Health endpoint responds
        try:
            resp = client.get(f"{BASE_URL}/health")
            data = resp.json()
            if resp.status_code == 200 and data.get("status") == "ok":
                print_result(1, "Health endpoint responds", "PASS")
                passed += 1
            else:
                print_result(
                    1,
                    "Health endpoint responds",
                    f"FAIL (status={resp.status_code}, body={data})",
                )
        except Exception as exc:
            print_result(1, "Health endpoint responds", f"FAIL ({exc})")

        # 2. Job creation
        try:
            resp = client.post(f"{BASE_URL}/api/jobs", json={"youtube_url": TEST_URL})
            data = resp.json()
            valid_id = isinstance(data.get("id"), str) and bool(data.get("id").strip())
            is_queued = data.get("status") == "queued"
            if resp.status_code == 202 and valid_id and is_queued:
                job_id = data["id"]
                print_result(2, "Job creation", "PASS")
                passed += 1
            else:
                print_result(
                    2,
                    "Job creation",
                    f"FAIL (status={resp.status_code}, body={data})",
                )
        except Exception as exc:
            print_result(2, "Job creation", f"FAIL ({exc})")

        # 3. Invalid URL rejection
        try:
            resp = client.post(
                f"{BASE_URL}/api/jobs", json={"youtube_url": "https://google.com"}
            )
            data = resp.json()
            data_str = json.dumps(data).lower()
            mentions_url = "youtube" in data_str or "url" in data_str
            if resp.status_code == 422 and mentions_url:
                print_result(3, "Invalid URL rejection", "PASS")
                passed += 1
            else:
                print_result(
                    3,
                    "Invalid URL rejection",
                    f"FAIL (status={resp.status_code}, body={data})",
                )
        except Exception as exc:
            print_result(3, "Invalid URL rejection", f"FAIL ({exc})")

        # 4. Job appears in list
        try:
            if not job_id:
                raise RuntimeError("job_id unavailable from check 2")
            resp = client.get(f"{BASE_URL}/api/jobs")
            data = resp.json()
            found = isinstance(data, list) and any(item.get("id") == job_id for item in data)
            if resp.status_code == 200 and found:
                print_result(4, "Job appears in list", "PASS")
                passed += 1
            else:
                print_result(
                    4,
                    "Job appears in list",
                    f"FAIL (status={resp.status_code}, found={found})",
                )
        except Exception as exc:
            print_result(4, "Job appears in list", f"FAIL ({exc})")

        # 5. Job status polling
        try:
            if not job_id:
                raise RuntimeError("job_id unavailable from check 2")
            started = time.time()
            terminal = None
            terminal_payload = None
            while time.time() - started < MAX_WAIT:
                resp = client.get(f"{BASE_URL}/api/jobs/{job_id}")
                payload = resp.json()
                status = payload.get("status")
                print(f"[poll] status: {status}...")
                if status in {"complete", "failed"}:
                    terminal = status
                    terminal_payload = payload
                    break
                time.sleep(POLL_INTERVAL)

            if terminal is None:
                print_result(
                    5,
                    "Job status polling",
                    "FAIL (Job did not complete within 180 seconds)",
                )
            elif terminal == "failed":
                error_obj = terminal_payload.get("error") or {}
                error_detail = error_obj.get("message") if isinstance(error_obj, dict) else str(error_obj)
                print_result(
                    5,
                    "Job status polling",
                    f"FAIL (error_code={error_obj.get('code') if isinstance(error_obj, dict) else '?'}, message={error_detail})",
                )
            else:
                completed_job = terminal_payload
                print_result(5, "Job status polling", "PASS")
                passed += 1
        except Exception as exc:
            print_result(5, "Job status polling", f"FAIL ({exc})")

        # 6. Output fields present on completed job
        try:
            if not completed_job:
                raise RuntimeError("completed job payload unavailable from check 5")

            duration_ok = bool(re.match(r"^\d{2}:\d{2}:\d{2}$", completed_job.get("video_duration") or ""))
            clips = completed_job.get("output_clips")
            twitter_post = completed_job.get("output_twitter_post") or ""
            thread = completed_job.get("output_twitter_thread")

            field_checks = {
                "video_title": isinstance(completed_job.get("video_title"), str) and bool((completed_job.get("video_title") or "").strip()),
                "video_duration": isinstance(completed_job.get("video_duration"), str) and duration_ok,
                "channel_name": isinstance(completed_job.get("channel_name"), str) and bool((completed_job.get("channel_name") or "").strip()),
                "video_id": isinstance(completed_job.get("video_id"), str) and bool((completed_job.get("video_id") or "").strip()),
                "output_clips (len==3)": isinstance(clips, list) and len(clips) == 3,
                "output_linkedin_short (>50)": isinstance(completed_job.get("output_linkedin_short"), str) and len(completed_job["output_linkedin_short"]) > 50,
                "output_linkedin_long (>200)": isinstance(completed_job.get("output_linkedin_long"), str) and len(completed_job["output_linkedin_long"]) > 200,
                "output_twitter_post (1-280)": isinstance(twitter_post, str) and 0 < len(twitter_post) <= 280,
                "output_twitter_thread (>=1)": isinstance(thread, list) and len(thread) >= 1,
            }
            failed_fields = [k for k, v in field_checks.items() if not v]

            if not failed_fields:
                print_result(6, "Completed job output fields present", "PASS")
                passed += 1
            else:
                print_result(6, "Completed job output fields present", f"FAIL (failed: {', '.join(failed_fields)})")
        except Exception as exc:
            print_result(6, "Completed job output fields present", f"FAIL ({exc})")

        # 7. Clip structure validation
        try:
            if not completed_job:
                raise RuntimeError("completed job payload unavailable from check 5")
            clips = completed_job.get("output_clips") or []
            required_keys = {
                "clip_id",
                "start_time",
                "end_time",
                "start_seconds",
                "end_seconds",
                "duration_seconds",
                "hook_summary",
                "why_this_works",
                "suggested_title",
            }
            clip_errors = []
            for i, clip in enumerate(clips):
                missing = required_keys - set(clip.keys())
                if missing:
                    clip_errors.append(f"clip[{i}] missing keys: {missing}")
                else:
                    duration = clip.get("duration_seconds")
                    if not isinstance(duration, (int, float)) or not (1 <= duration <= 300):
                        clip_errors.append(f"clip[{i}] duration_seconds={duration!r} out of range [1,300]")
            if not clip_errors and len(clips) == 3:
                print_result(7, "Clip structure validation", "PASS")
                passed += 1
            else:
                detail = "; ".join(clip_errors) if clip_errors else f"expected 3 clips, got {len(clips)}"
                print_result(7, "Clip structure validation", f"FAIL ({detail})")
        except Exception as exc:
            print_result(7, "Clip structure validation", f"FAIL ({exc})")

        # 8. Transcript endpoint
        try:
            if not job_id:
                raise RuntimeError("job_id unavailable from check 2")
            resp = client.get(f"{BASE_URL}/api/jobs/{job_id}/transcript")
            data = resp.json()
            first = data[0] if isinstance(data, list) and data else {}
            required_keys = {"index", "start", "end", "start_seconds", "end_seconds", "text"}
            ok = resp.status_code == 200 and isinstance(data, list) and len(data) >= 1 and required_keys.issubset(set(first.keys()))
            if ok:
                print_result(8, "Transcript endpoint", "PASS")
                passed += 1
            else:
                print_result(
                    8,
                    "Transcript endpoint",
                    f"FAIL (status={resp.status_code}, body_type={type(data).__name__})",
                )
        except Exception as exc:
            print_result(8, "Transcript endpoint", f"FAIL ({exc})")

        # 9. Duplicate job URL handling
        try:
            if not job_id:
                raise RuntimeError("job_id unavailable from check 2")
            resp = client.post(f"{BASE_URL}/api/jobs", json={"youtube_url": TEST_URL})
            data = resp.json()
            new_id = data.get("id")
            ok = (
                resp.status_code == 202
                and isinstance(new_id, str)
                and bool(new_id.strip())
                and new_id != job_id
            )
            if ok:
                print_result(9, "Duplicate URL submission handling", "PASS")
                passed += 1
            else:
                print_result(
                    9,
                    "Duplicate URL submission handling",
                    f"FAIL (status={resp.status_code}, body={data})",
                )
        except Exception as exc:
            print_result(9, "Duplicate URL submission handling", f"FAIL ({exc})")

        # 10. Job deletion
        try:
            if not job_id:
                raise RuntimeError("job_id unavailable from check 2")
            del_resp = client.delete(f"{BASE_URL}/api/jobs/{job_id}")
            get_resp = client.get(f"{BASE_URL}/api/jobs/{job_id}")
            if del_resp.status_code == 200 and get_resp.status_code == 404:
                print_result(10, "Job deletion", "PASS")
                passed += 1
            else:
                print_result(
                    10,
                    "Job deletion",
                    f"FAIL (delete={del_resp.status_code}, get={get_resp.status_code})",
                )
        except Exception as exc:
            print_result(10, "Job deletion", f"FAIL ({exc})")

    print(f"{passed}/10 checks passed.")

    if passed == 10 and completed_job:
        linkedin_short = completed_job.get("output_linkedin_short", "")
        linkedin_preview = (
            f"{linkedin_short[:80]}..." if len(linkedin_short) > 80 else linkedin_short
        )
        print("==========================================")
        print("  PIPELINE END-TO-END: ALL CHECKS PASSED")
        print(f"  Job ID: {completed_job.get('id')}")
        print(f"  Video: {completed_job.get('video_title')}")
        print(f"  Duration: {completed_job.get('video_duration')}")
        print(f"  Word count: {completed_job.get('transcript_word_count')}")
        print(f"  LinkedIn Short: {linkedin_preview}")
        print(f"  Twitter Post: {completed_job.get('output_twitter_post')}")
        print("==========================================")


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)
