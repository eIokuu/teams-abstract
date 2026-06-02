# Teams Meeting AI Summary Tool

Automatically analyze Microsoft Teams meeting transcripts with AI.
Extract speaker-attributed summaries, teacher suggestions, and action items.

## Features
- Parse Teams transcript formats (timestamped, VTT, plain text)
- Speaker attribution (who said what)
- Teacher/advisor suggestion extraction
- Structured meeting minutes (Markdown + JSON)
- Windows Task Scheduler integration
- Docker support

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp config.template.py config.py
# Edit config.py - set your API key

# 3. Run
python run.py --paste
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| LLM_API_KEY | (required) | OpenAI / DeepSeek / compatible API key |
| LLM_BASE_URL | https://api.openai.com/v1 | API endpoint |
| LLM_MODEL | gpt-4o | Model name |
| WATCH_FOLDER | transcripts/inbox | Input folder for --watch |
| OUTPUT_FOLDER | output | Output folder |

## Usage Modes

### 1. Interactive Paste
```bash
python run.py --paste
```
Paste transcript text, type END on a new line to finish.

### 2. Single File
```bash
python run.py --file path/to/transcript.txt
```

### 3. Watch Folder
```bash
python run.py --watch
```
Processes all .txt/.vtt/.srt/.md files in the watch folder.

### 4. Windows Scheduled Task
```powershell
# Run as Administrator
.\schedule_automation.ps1 -Setup
```
Checks for new transcripts every 30 minutes (9AM-10PM).

## Docker

```bash
docker build -t meeting-summary .
docker run -it --rm -v "$(pwd)/config.py:/app/config.py" meeting-summary --paste
```

## Output

All output goes to the configured OUTPUT_FOLDER (default: output/):
- `filename_minutes.md` - Structured meeting minutes
- `filename_data.json` - Raw analysis data

## API Compatibility

Works with any OpenAI-compatible API:
- OpenAI GPT-4o / GPT-4 / GPT-3.5
- DeepSeek
- Moonshot / Kimi
- Local LLMs (vLLM, Ollama with OpenAI proxy)

## License
MIT