"""
Meeting content AI analysis engine
Features: dialogue analysis, speaker attribution, teacher suggestion extraction
"""

import json, os, sys, re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from transcript_parser import TranscriptSegment, group_by_speaker


def call_llm(messages: list, config: dict, temperature: float = 0.3) -> str:
    import httpx
    hdrs = {"Authorization": "Bearer "+config["LLM_API_KEY"], "Content-Type": "application/json"}
    pl = {"model": config["LLM_MODEL"], "messages": messages, "temperature": temperature, "max_tokens": 4096}
    r = httpx.post(config["LLM_BASE_URL"].rstrip("/")+"/chat/completions", headers=hdrs, json=pl, timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


SUMMARY_SYSTEM_PROMPT = """You are a professional meeting minutes analyst.
Output analysis as JSON with these fields:
meeting_info (date, duration, participants),
speaker_summary (speaker, main_points, total_speech_ratio),
key_discussions (topic, detail, involved_speakers, conclusion),
teacher_suggestions (teacher, suggestion, context, priority, action_item),
action_items (assignee, task, deadline),
next_steps,
key_risks_or_issues,
overall_summary
"""


def build_analysis_prompt(transcript_text, speaker_groups):
    g = chr(10).join([f"Speaker [{s}]:\n{t[:500]}" for s,t in speaker_groups.items()])
    return f"Transcript:\n{transcript_text[:4000]}\n\nSpeakers:\n{g[:3000]}"


def analyze_transcript(segments, config, title=""):
    lines = []
    for s in segments:
        ts = f"[{s.timestamp}] " if s.timestamp else ""
        lines.append(f"{ts}{s.speaker}: {s.text}")
    text = chr(10).join(lines)
    groups = group_by_speaker(segments)
    prompt = build_analysis_prompt(text, groups)
    msgs = [{"role": "system", "content": SUMMARY_SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
    try:
        raw = call_llm(msgs, config).strip()
        if raw.startswith("```json"): raw = raw[7:]
        elif raw.startswith("```"): raw = raw[3:]
        if raw.endswith("```"): raw = raw[:-3]
        return json.loads(raw.strip())
    except json.JSONDecodeError as e:
        return {"error": str(e), "raw": raw[:300]}
    except Exception as e:
        return {"error": str(e)}

def format_as_markdown(result, title=""):
    t = title or "Meeting"
    lines = [f"# Meeting Minutes: {t}\n", f"Generated: {datetime.now().strftime(chr(37)+chr(89)+chr(45)+chr(37)+chr(109)+chr(45)+chr(37)+chr(100)+chr(32)+chr(37)+chr(72)+chr(58)+chr(37)+chr(77))}\n"]
    info = result.get("meeting_info", {}) or {}
    lines.append("## Meeting Info\n")
    lines.append(f"- Date: {info.get(chr(39)+chr(100)+chr(97)+chr(116)+chr(101)+chr(39), chr(39)+chr(26410)+chr(30693)+chr(39))}")
    lines.append(f"- Duration: {info.get(chr(39)+chr(100)+chr(117)+chr(114)+chr(97)+chr(116)+chr(105)+chr(111)+chr(110)+chr(39), chr(39)+chr(26410)+chr(30693)+chr(39))}")
    parts = info.get("participants", []) or []
    if parts: lines.append(f"- Participants: {chr(44)+chr(12310)+chr(44).join(parts)}")
    lines.append("")
    summary = result.get("overall_summary", "") or ""
    if summary: lines.extend(["## Summary\n", summary, ""])
    sgs = result.get("teacher_suggestions", []) or []
    if sgs:
        lines.append("## Teacher Suggestions\n")
        for i, sg in enumerate(sgs, 1):
            if isinstance(sg, dict):
                lines.append(f"### Suggestion {i} ({sg.get(chr(39)+chr(116)+chr(101)+chr(97)+chr(99)+chr(104)+chr(101)+chr(114)+chr(39), chr(39)+chr(32769)+chr(24072)+chr(39))})\n")
                lines.append(sg.get("suggestion", "") or "")
                ctx = sg.get("context", "") or ""
                if ctx: lines.append(f"\nContext: {ctx}")
                pr = sg.get("priority", "") or ""
                if pr: lines.append(f"\nPriority: {pr}")
                act = sg.get("action_item", "") or ""
                if act: lines.append(f"\nAction: {act}")
                lines.append("")
    dscs = result.get("key_discussions", []) or []
    if dscs:
        lines.append("## Key Discussions\n")
        for d in dscs:
            if isinstance(d, dict):
                lines.append(f"### {d.get(chr(39)+chr(116)+chr(111)+chr(112)+chr(105)+chr(99)+chr(39), chr(39)+chr(35758)+chr(39064)+chr(39))}\n")
                lines.append(d.get("detail", "") or "")
                spks = d.get("involved_speakers", []) or []
                if spks: lines.append(f"\nSpeakers: {chr(44)+chr(12310)+chr(44).join(spks)}")
                conc = d.get("conclusion", "") or ""
                if conc: lines.append(f"\nConclusion: {conc}")
                lines.append("")
    acts = result.get("action_items", []) or []
    if acts:
        lines.append("## Action Items\n")
        for a in acts:
            if isinstance(a, dict):
                lines.append(f"- [ ] {a.get(chr(39)+chr(97)+chr(115)+chr(115)+chr(105)+chr(103)+chr(110)+chr(101)+chr(101)+chr(39), chr(39)+chr(26410)+chr(30693)+chr(39))}: {a.get(chr(39)+chr(116)+chr(97)+chr(115)+chr(107)+chr(39), chr(39)+chr(39))}")
        lines.append("")
    nxt = result.get("next_steps", []) or []
    if nxt:
        lines.append("## Next Steps\n")
        for ns in nxt: lines.append(f"- {ns}")
        lines.append("")
    risks = result.get("key_risks_or_issues", []) or []
    if risks:
        lines.append("## Risks and Issues\n")
        for r in risks: lines.append(f"- {r}")
        lines.append("")
    sp_sum = result.get("speaker_summary", []) or []
    if sp_sum:
        lines.append("## Speaker Summary\n")
        for sp in sp_sum:
            if isinstance(sp, dict):
                lines.append(f"**{sp.get(chr(39)+chr(115)+chr(112)+chr(101)+chr(97)+chr(107)+chr(101)+chr(114)+chr(39), chr(39)+chr(26410)+chr(30693)+chr(39))}**")
                pts = sp.get("main_points", []) or []
                if pts:
                    for p in pts: lines.append(f"- {p}")
                lines.append("")
    return chr(10).join(lines)

def save_output(result, markdown, file_stem, output_dir, fmt="md"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    md = out / f"{file_stem}_minutes.md"
    md.write_text(markdown, encoding="utf-8")
    print(f"  Minutes saved: {md}")
    js = out / f"{file_stem}_data.json"
    js.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Data saved: {js}")
    return md, js
