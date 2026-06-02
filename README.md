# SAM3 - Macau Street View Perception Research

>> Segment Anything Model 3 applied to Macau Historic Centre analysis

## Project Structure

### 1. sam3-main/ - SAM3 Facade Segmentation and Analysis
Main project for street-view facade segmentation and K-means color extraction.

### 2. tools/meeting_summary/ - Teams Meeting AI Summary Tool

---

## Quick Start: Meeting Summary Tool

### Install

```bash
cd tools/meeting_summary
pip install -r requirements.txt
```

### Configure

```bash
cp config.template.py config.py
```

Edit config.py with your API key, then run:

```bash
python run.py --paste
```

Or use --file for a single transcript, --watch for batch processing.

### Windows Automation
Run as Admin PowerShell:
```powershell
cd tools/meeting_summary
.\schedule_automation.ps1 -Setup
```

---

## Tech Stack
- Python 3.8+
- httpx
- OpenAI / DeepSeek compatible API
- SAM3

## Output
After processing, output/ contains:
- meeting_minutes.md (structured summary)
- meeting_data.json (raw analysis)