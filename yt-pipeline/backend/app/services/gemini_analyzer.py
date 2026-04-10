import json
import os
import time


SYSTEM_PROMPT = (
    "You are an expert content strategist and social media copywriter.\n"
    "You will receive a YouTube video transcript with inline timestamps.\n"
    "Your job is to analyze it and return a single JSON object — no markdown, no explanation, just raw JSON."
)

RETRY_SUFFIX = (
    "IMPORTANT: Your previous response was not valid JSON. Return ONLY the raw JSON object. "
    "No backticks, no markdown, no explanation. Start your response with { and end with }."
)

REQUIRED_RESPONSE_KEYS = {
    "clips",
    "linkedin_short",
    "linkedin_long",
    "twitter_post",
    "twitter_thread",
}


class GeminiAnalysisError(Exception):
    def __init__(self, code: str, message: str, retryable: bool):
        self.code = code
        self.message = message
        self.retryable = retryable
        super().__init__(message)


def _build_user_prompt(
    transcript_string: str,
    video_title: str,
    video_duration: str,
    channel_name: str,
) -> str:
    return f"""Video Title: {video_title}
Channel: {channel_name}
Duration: {video_duration}

TRANSCRIPT:
{transcript_string}

---

Analyze the transcript above and return ONLY a valid JSON object with this exact structure:

{{
  "clips": [
    {{
      "clip_id": 1,
      "start_time": "HH:MM:SS",
      "end_time": "HH:MM:SS",
      "start_seconds": 0,
      "end_seconds": 0,
      "duration_seconds": 0,
      "hook_summary": "one sentence describing the hook",
      "why_this_works": "one sentence explanation",
      "suggested_title": "short punchy title under 60 chars"
    }}
  ],
  "linkedin_short": "150-300 word professional post with 3-5 hashtags",
  "linkedin_long": "600-1200 word post with narrative arc and 5-8 hashtags",
  "twitter_post": "under 280 characters, punchy and opinion-forward",
  "twitter_thread": ["tweet 1", "tweet 2", "tweet 3"]
}}

Rules:
- clips array must contain exactly 3 items
- Each clip must have a duration_seconds between 30 and 90
- twitter_post must be under 280 characters
- linkedin_long must use line breaks for readability (no markdown headers)
- Return only the JSON object. No other text before or after it."""


def _validate_response(parsed: dict) -> dict:
    missing_keys = sorted(list(REQUIRED_RESPONSE_KEYS - set(parsed.keys())))
    if missing_keys:
        raise GeminiAnalysisError(
            code="INCOMPLETE_RESPONSE",
            message=f"Missing keys: {missing_keys}",
            retryable=True,
        )

    clips = parsed.get("clips", [])
    if not isinstance(clips, list):
        raise GeminiAnalysisError(
            code="WRONG_CLIP_COUNT",
            message="Expected 3 clips, got 0",
            retryable=True,
        )
    if len(clips) != 3:
        raise GeminiAnalysisError(
            code="WRONG_CLIP_COUNT",
            message=f"Expected 3 clips, got {len(clips)}",
            retryable=True,
        )

    twitter_post = str(parsed.get("twitter_post", ""))
    if len(twitter_post) > 280:
        original_len = len(twitter_post)
        parsed["twitter_post"] = twitter_post[:277] + "..."
        print(f"[WARN] twitter_post truncated from {original_len} to 280 chars")

    return parsed


def _extract_response_text(response: object) -> str:
    text = getattr(response, "text", "")
    if text:
        return text.strip()

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) or []
        for part in parts:
            part_text = getattr(part, "text", "")
            if part_text:
                return part_text.strip()
    return ""


def analyze_transcript(
    transcript_string: str,
    video_title: str,
    video_duration: str,
    channel_name: str,
) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")

    if not api_key:
        raise GeminiAnalysisError(
            code="MISSING_API_KEY",
            message="GEMINI_API_KEY is not set",
            retryable=False,
        )

    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_PROMPT,
    )

    user_prompt = _build_user_prompt(
        transcript_string=transcript_string,
        video_title=video_title,
        video_duration=video_duration,
        channel_name=channel_name,
    )

    generation_config = {
        "temperature": 0.7,
        "max_output_tokens": 4096,
    }

    def _call_with_rate_limit_retry(prompt: str, max_attempts: int = 4) -> str:
        """Call Gemini, retrying up to max_attempts times on 429 ResourceExhausted."""
        import re as _re
        for attempt in range(1, max_attempts + 1):
            try:
                resp = model.generate_content(prompt, generation_config=generation_config)
                return _extract_response_text(resp)
            except Exception as exc:
                exc_str = str(exc)
                is_rate_limit = "429" in exc_str or "ResourceExhausted" in type(exc).__name__
                if is_rate_limit and attempt < max_attempts:
                    # Parse "retry in Xs" hint from the error message if present
                    match = _re.search(r"retry[^\d]*(\d+(?:\.\d+)?)", exc_str, _re.IGNORECASE)
                    wait = float(match.group(1)) + 2 if match else 30 * attempt
                    print(f"[gemini] 429 rate limit on attempt {attempt}/{max_attempts}, waiting {wait:.0f}s...")
                    time.sleep(wait)
                else:
                    raise

    first_text = _call_with_rate_limit_retry(user_prompt)
    try:
        parsed = json.loads(first_text)
    except json.JSONDecodeError:
        retry_prompt = f"{user_prompt}\n\n{RETRY_SUFFIX}"
        second_text = _call_with_rate_limit_retry(retry_prompt)
        try:
            parsed = json.loads(second_text)
        except json.JSONDecodeError as exc:
            raise GeminiAnalysisError(
                code="INVALID_JSON_RESPONSE",
                message="Gemini returned malformed JSON after retry",
                retryable=True,
            ) from exc

    return _validate_response(parsed)
