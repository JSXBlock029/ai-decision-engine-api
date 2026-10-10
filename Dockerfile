FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PYTHONPATH=/app

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api ./api
COPY ai_decision_engine.py ai_memory_system.py autonomy_tracker.py ./

# State files are written relative to the working directory, so keep that on a volume.
RUN useradd --system --uid 10001 app && mkdir /data && chown app /data
USER app
WORKDIR /data
VOLUME /data

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)"

# SQLite key store: safe with several workers. (The JSON store would need --workers 1.)
ENV KEY_STORE=sqlite KEY_DB_PATH=/data/api_keys.sqlite3
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
