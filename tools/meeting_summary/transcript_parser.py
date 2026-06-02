"""
Teams meeting transcript parser
Supports: Teams native format, VTT captions, and plain text
"""

import re
from pathlib import Path
from typing import List, Dict, Optional


class TranscriptSegment:
    """A single segment of dialogue with speaker attribution"""
    def __init__(self, speaker: str, text: str, timestamp: str = None):
        self.speaker = speaker.strip() if speaker else "Unknown"
        self.text = text.strip()
        self.timestamp = timestamp

    def __repr__(self):
        ts = f"[{self.timestamp}] " if self.timestamp else ""
        return f"{ts}{self.speaker}: {self.text[:50]}..."


def parse_teams_transcript(text: str) -> List[TranscriptSegment]:
    """Parse Teams standard format: [HH:MM:SS] Speaker: text"""
    segments = []
    pattern = re.compile(chr(94)+r"\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?\s+(.+?):\s(.+)$", re.MULTILINE)
    current_speaker = None
    current_text = ""
    current_ts = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = pattern.match(line)
        if m:
            if current_speaker and current_text:
                segments.append(TranscriptSegment(current_speaker, current_text, current_ts))
            ts = m.group(1)
            speaker = m.group(2).strip()
            content = m.group(3).strip()
            current_speaker = speaker
            current_text = content
            current_ts = ts
        else:
            if current_speaker:
                current_text += " " + line
    if current_speaker and current_text:
        segments.append(TranscriptSegment(current_speaker, current_text, current_ts))
    return segments


def parse_vtt_captions(text: str) -> List[TranscriptSegment]:
    """Parse VTT caption format"""
    segments = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        ts_match = re.match(chr(94)+r"(\d{2}:\d{2}:\d{2}\.\d{3})\s*--"+chr(62), line)
        if not ts_match:
            i += 1
            continue
        timestamp = ts_match.group(1)
        i += 1
        content_lines = []
        while i < len(lines) and lines[i].strip() and not re.match(chr(94)+r"\d{2}:\d{2}", lines[i].strip()):
            content_lines.append(lines[i].strip())
            i += 1
        content = " ".join(content_lines)
        sp_match = re.match(chr(94)+r"(.+?):\s(.+)$", content)
        if sp_match:
            segments.append(TranscriptSegment(sp_match.group(1), sp_match.group(2), timestamp))
        else:
            segments.append(TranscriptSegment("Unknown", content, timestamp))
    return segments


def parse_fallback(text: str) -> List[TranscriptSegment]:
    """Fallback: split by blank lines, try to extract Speaker: text"""
    segments = []
    blocks = re.split(chr(92)+chr(92)+chr(110)+chr(92)+chr(92)+chr(115)+chr(42), text.strip())
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        m = re.match(chr(94)+r"(.+?)[:：]\s(.+)$", block, re.DOTALL)
        if m:
            segments.append(TranscriptSegment(m.group(1), m.group(2)))
        else:
            segments.append(TranscriptSegment("Unknown", block))
    return segments


def auto_parse(text: str) -> List[TranscriptSegment]:
    """Auto-detect format and parse"""
    if text.strip().startswith("WEBVTT"):
        result = parse_vtt_captions(text)
        if result:
            return result
    result = parse_teams_transcript(text)
    if result:
        return result
    return parse_fallback(text)


def read_transcript(file_path: str, encoding: str = "utf-8") -> str:
    """Read a transcript file, trying multiple encodings"""
    path = Path(file_path)
    for enc in [encoding, "utf-8-sig", "gbk", "latin-1"]:
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def group_by_speaker(segments: List[TranscriptSegment]) -> Dict[str, str]:
    """Group all text by speaker"""
    groups = {}
    for seg in segments:
        if seg.speaker not in groups:
            groups[seg.speaker] = []
        groups[seg.speaker].append(seg.text)
    return {s: " ".join(t) for s, t in groups.items()}
