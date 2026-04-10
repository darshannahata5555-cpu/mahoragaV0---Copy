import re
from pathlib import Path


_TAG_RE = re.compile(r"<[^>]+>")
_VTT_TS_RE = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(?P<end>\d{2}:\d{2}:\d{2}\.\d{3})"
)
_SRT_TS_RE = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(?P<end>\d{2}:\d{2}:\d{2},\d{3})"
)
_TIMESTAMP_MARKER_RE = re.compile(r"\[\d{2}:\d{2}:\d{2}\]")
_SENTENCE_END_RE = re.compile(r"[.?!][\"')\]]*$")


def _clean_text(text: str) -> str:
    cleaned = _TAG_RE.sub("", text)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _timestamp_to_seconds(timestamp: str) -> float:
    hh, mm, ss_mmm = timestamp.split(":")
    if "," in ss_mmm:
        ss, mmm = ss_mmm.split(",")
    else:
        ss, mmm = ss_mmm.split(".")
    return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(mmm) / 1000.0


def _parse_vtt(content: str) -> list[dict]:
    cues: list[dict] = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line == "WEBVTT":
            i += 1
            continue

        if line.startswith("NOTE"):
            i += 1
            while i < len(lines) and lines[i].strip():
                i += 1
            i += 1
            continue

        ts_match = _VTT_TS_RE.search(line)
        if ts_match:
            start = ts_match.group("start")
            end = ts_match.group("end")
            i += 1
            text_lines: list[str] = []
            while i < len(lines) and lines[i].strip():
                text_lines.append(lines[i].strip())
                i += 1
            text = _clean_text(" ".join(text_lines))
            if text:
                cues.append(
                    {
                        "index": len(cues) + 1,
                        "start": start,
                        "end": end,
                        "start_seconds": float(_timestamp_to_seconds(start)),
                        "end_seconds": float(_timestamp_to_seconds(end)),
                        "text": text,
                    }
                )
            continue

        i += 1
    return cues


def _parse_srt(content: str) -> list[dict]:
    cues: list[dict] = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if line.isdigit():
            i += 1
            continue

        ts_match = _SRT_TS_RE.search(line)
        if ts_match:
            start = ts_match.group("start").replace(",", ".")
            end = ts_match.group("end").replace(",", ".")
            i += 1
            text_lines: list[str] = []
            while i < len(lines) and lines[i].strip():
                if not lines[i].strip().isdigit():
                    text_lines.append(lines[i].strip())
                i += 1
            text = _clean_text(" ".join(text_lines))
            if text:
                cues.append(
                    {
                        "index": len(cues) + 1,
                        "start": start,
                        "end": end,
                        "start_seconds": float(_timestamp_to_seconds(start)),
                        "end_seconds": float(_timestamp_to_seconds(end)),
                        "text": text,
                    }
                )
            continue

        i += 1
    return cues


def _remove_consecutive_duplicates(cues: list[dict]) -> list[dict]:
    if not cues:
        return cues
    deduped = [cues[0].copy()]
    for cue in cues[1:]:
        if cue["text"] != deduped[-1]["text"]:
            deduped.append(cue.copy())
    return deduped


def _merge_overlapping_cues(cues: list[dict]) -> list[dict]:
    if not cues:
        return cues
    merged: list[dict] = [cues[0].copy()]
    for cue in cues[1:]:
        current = merged[-1]
        if current["end_seconds"] > cue["start_seconds"]:
            if cue["text"] and cue["text"] not in current["text"]:
                current["text"] = f"{current['text']} {cue['text']}".strip()
            if cue["end_seconds"] > current["end_seconds"]:
                current["end_seconds"] = cue["end_seconds"]
                current["end"] = cue["end"]
        else:
            merged.append(cue.copy())
    return merged


def _ends_sentence(text: str) -> bool:
    return bool(_SENTENCE_END_RE.search(text.strip()))


def _merge_sentence_fragments(cues: list[dict]) -> list[dict]:
    if not cues:
        return cues
    rebuilt = [cue.copy() for cue in cues]
    i = 0
    while i < len(rebuilt) - 1:
        if not _ends_sentence(rebuilt[i]["text"]):
            next_cue = rebuilt.pop(i + 1)
            rebuilt[i]["text"] = f"{rebuilt[i]['text']} {next_cue['text']}".strip()
            rebuilt[i]["end"] = next_cue["end"]
            rebuilt[i]["end_seconds"] = next_cue["end_seconds"]
            continue
        i += 1
    return rebuilt


def _reindex(cues: list[dict]) -> list[dict]:
    for idx, cue in enumerate(cues, start=1):
        cue["index"] = idx
    return cues


def parse_subtitles(subtitle_file_path: str, subtitle_format: str) -> list[dict]:
    path = Path(subtitle_file_path)
    content = path.read_text(encoding="utf-8")
    fmt = subtitle_format.lower().lstrip(".")

    if fmt == "vtt":
        cues = _parse_vtt(content)
    elif fmt == "srt":
        cues = _parse_srt(content)
    else:
        raise ValueError(f"Unsupported subtitle format: {subtitle_format}")

    cues = _remove_consecutive_duplicates(cues)
    cues = _merge_overlapping_cues(cues)
    cues = _merge_sentence_fragments(cues)
    cues = _reindex(cues)
    return cues


def build_transcript_string(cues: list[dict]) -> str:
    lines: list[str] = []
    for cue in cues:
        start_hms = str(cue["start"]).split(".")[0]
        lines.append(f"[{start_hms}] {cue['text']}")
    return "\n".join(lines)


def count_words(transcript_string: str) -> int:
    without_markers = _TIMESTAMP_MARKER_RE.sub("", transcript_string)
    tokens = [token for token in without_markers.split() if token]
    return len(tokens)
