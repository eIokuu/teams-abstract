"""
Meeting transcript analysis tool
Usage: run.py --file PATH or --watch or --paste
"""

import argparse, os, sys, json
from pathlib import Path
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from transcript_parser import auto_parse, read_transcript
from meeting_analyzer import analyze_transcript, format_as_markdown, save_output

def load_config():
    cf = Path(__file__).parent / "config.py"
    if not cf.exists():
        print("="*60)
        print("  Missing config.py!")
        print("  Copy config.template.py and set API key")
        print("="*60)
        sys.exit(1)
    import importlib.util
    spec = importlib.util.spec_from_file_location("config", str(cf))
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    return {
        "LLM_API_KEY": cfg.LLM_API_KEY,
        "LLM_BASE_URL": getattr(cfg, "LLM_BASE_URL", "https://api.openai.com/v1"),
        "LLM_MODEL": getattr(cfg, "LLM_MODEL", "gpt-4o"),
        "WATCH_FOLDER": getattr(cfg, "WATCH_FOLDER", ""),
        "ARCHIVE_FOLDER": getattr(cfg, "ARCHIVE_FOLDER", ""),
        "OUTPUT_FOLDER": getattr(cfg, "OUTPUT_FOLDER", ""),
        "TRANSCRIPT_ENCODING": getattr(cfg, "TRANSCRIPT_ENCODING", "utf-8"),
    }

def process_file(file_path, config):
    path = Path(file_path)
    print(f"\nProcessing: {path.name}")
    print("  Reading transcript...")
    text = read_transcript(str(path), config.get("TRANSCRIPT_ENCODING", "utf-8"))
    print("  Parsing...")
    segments = auto_parse(text)
    print(f"  Found {len(segments)} dialogue segments")
    speakers = set(s.speaker for s in segments)
    real = [s for s in speakers if s != "Unknown"]
    if real: print(f"  Participants: {", ".join(real)}")
    print("  AI analysis (may take 10-30s)...")
    title = path.stem.replace("_", " ")
    result = analyze_transcript(segments, config, title=title)
    if "error" in result:
        print(f"  ERROR: {result["error"]}")
        return result
    print("  Analysis complete!")
    md = format_as_markdown(result, title=title)
    od = config.get("OUTPUT_FOLDER", str(path.parent.parent / "output")) or str(path.parent.parent / "output")
    save_output(result, md, path.stem, od)
    return result

def process_watch_folder(config):
    wd = config.get("WATCH_FOLDER", "")
    if not wd or not Path(wd).exists():
        print(f"Watch folder not found: {wd}")
        return
    ad = config.get("ARCHIVE_FOLDER", str(Path(wd).parent / "archive"))
    Path(ad).mkdir(parents=True, exist_ok=True)
    exts = (".txt", ".vtt", ".srt", ".md")
    files = sorted([f for f in Path(wd).iterdir() if f.is_file() and f.suffix.lower() in exts])
    if not files:
        print(f"No files to process in: {wd}")
        return
    print(f"Found {len(files)} file(s)")
    for f in files:
        print("-"*40)
        result = process_file(str(f), config)
        if "error" not in result:
            f.rename(Path(ad) / f.name)
            print(f"  Archived: {f.name}")
    print(f"Done: {len(files)} file(s) processed")


def interactive_mode(config):
    print("Paste transcript text, then type END on a new line and press Enter:")
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "END": break
            lines.append(line)
        except EOFError:
            break
    if not lines:
        print("No input")
        return
    text = chr(10).join(lines)
    print(f"Received {len(text)} chars")
    segments = auto_parse(text)
    print(f"Found {len(segments)} segments")
    result = analyze_transcript(segments, config, "interactive")
    if "error" in result:
        print(f"Error: {result["error"]}")
        return
    md = format_as_markdown(result, "interactive")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    od = config.get("OUTPUT_FOLDER", str(Path(__file__).parent / "output"))
    save_output(result, md, f"interactive_{ts}", od)
    print(md[:500])


def main():
    p = argparse.ArgumentParser(description="Teams meeting transcript analysis tool")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--file", "-f", help="Single transcript file")
    g.add_argument("--watch", "-w", action="store_true", help="Batch process watch folder")
    g.add_argument("--paste", "-p", action="store_true", help="Interactive paste mode")
    args = p.parse_args()
    config = load_config()
    if config["LLM_API_KEY"] == "sk-your-api-key-here" or not config["LLM_API_KEY"]:
        print("Please set LLM_API_KEY in config.py")
        sys.exit(1)
    if args.file:
        if not Path(args.file).exists():
            print(f"File not found: {args.file}")
            sys.exit(1)
        process_file(args.file, config)
    elif args.watch:
        process_watch_folder(config)
    elif args.paste:
        interactive_mode(config)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
