# equity-scout hosted API (scout serve with SCOUT_HOSTED=1). Ships the latest committed feature snapshot.
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 UV_SYSTEM_PYTHON=1 SCOUT_HOSTED=1
WORKDIR /app
RUN pip install --no-cache-dir uv==0.9.3
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev
COPY data ./data
COPY docs ./docs
COPY llm_cache ./llm_cache
COPY runs ./runs
RUN useradd --create-home scout && chown -R scout /app
USER scout
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s CMD python -c "import os,urllib.request;urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8080')+'/api/health',timeout=4)"
CMD ["sh", "-c", "exec /app/.venv/bin/scout serve --no-browser --port ${PORT:-8080}"]
