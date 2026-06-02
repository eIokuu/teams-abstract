FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.template.py meeting_analyzer.py transcript_parser.py run.py ./

VOLUME ["/app/config.py", "/app/transcripts", "/app/output"]

ENTRYPOINT ["python", "run.py"]
CMD ["--help"]