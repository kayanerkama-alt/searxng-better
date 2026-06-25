# Atomic Search - Production Dockerfile
# Based on SearXNG | Rebranded by UCXP Project

FROM python:3.12-slim

LABEL maintainer="UCXP Project"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git build-essential libxml2-dev libxslt-dev zlib1g-dev libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

ARG UPSTREAM_COMMIT=e3126b89e69d1a56488f54f27928581a897cb058
RUN git clone --depth 1 https://github.com/searxng/searxng.git . && \
    git fetch --depth 1 origin ${UPSTREAM_COMMIT} && git reset --hard ${UPSTREAM_COMMIT}

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -U pip wheel && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt && \
    /opt/venv/bin/pip install --no-cache-dir granian==1.0.0

COPY --chown=root:root ./out/ /app/searx/static/themes/simple/
COPY --chown=root:root ./src/limiter.toml /etc/searxng/limiter.toml
COPY --chown=root:root ./src/favicons.toml /etc/searxng/favicons.toml

RUN useradd -m -u 1000 -s /bin/bash appuser && \
    mkdir -p /app/searx/data && chown -R appuser:appuser /app

ENV SEARXNG_DATA_DIR=/app/searx/data SEARXNG_SETTINGS=/app/searx/settings.yml \
    GRANIAN_HOST=0.0.0.0 GRANIAN_PORT=8080 IMAGE_PROXY=true NAME="Atomic Search"

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:8080/healthz 2>/dev/null || exit 1

USER appuser
EXPOSE 8080
CMD ["sh", "-c", "python -c \"import searx.webapp; f=open('searx/webapp.py','a'); f.write('\\n@app.route(\\\"/healthz\\\")\\ndef healthz(): return \\\"OK\\\", 200\\n'); f.close()\" && /opt/venv/bin/granian --host 0.0.0.0 --port 8080 --workers 2 searx.webapp:app"]
