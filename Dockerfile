# Atomic Search - PRODUCTION Dockerfile
# Rebranded by UCXP Project
# This WORKS on Railway/Render

FROM python:3.12-slim

LABEL maintainer="UCXP Project"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential libxml2-dev libxslt-dev zlib1g-dev \
    libffi-dev libssl-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clone SearXNG from source
ARG SEARXNG_COMMIT=e3126b89e69d1a56488f54f27928581a897cb058
RUN git clone --depth 1 https://github.com/searxng/searxng.git . && \
    git fetch --depth 1 origin ${SEARXNG_COMMIT} && \
    git reset --hard ${SEARXNG_COMMIT}

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy custom settings with branding
COPY --chown=root:root ./src/settings.yml /app/searx/settings.yml

# Copy privacy features
COPY --chown=root:root ./src/search/privacy_features.py /app/searx/search/privacy_features.py
COPY --chown=root:root ./src/search/ranking_control.py /app/searx/search/ranking_control.py

# Copy themes
COPY --chown=root:root ./out/themes/ /app/searx/static/themes/simple/

# Patch branding - replace ALL SearXNG with Atomic Search
RUN sed -i 's/instance_name:.*SearXNG/instance_name: "Atomic Search"/g' /app/searx/settings.yml && \
    sed -i 's/SearXNG/Atomic Search/g' /app/searx/infopage/*/about.md && \
    sed -i 's/SearXNG/Atomic Search/g' /app/searx/templates/simple/info/en/about.md && \
    sed -i 's/SearXNG/Atomic Search/g' /app/searx/templates/simple/base.html && \
    sed -i 's/SearXNG/Atomic Search/g' /app/searx/templates/simple/info/about.html && \
    sed -i 's/SearXNG/Atomic Search/g' /app/searx/templates/simple/manifest.json && \
    sed -i 's/SearXNG/Atomic Search/g' /app/searx/templates/simple/opensearch.xml && \
    sed -i 's/About SearXNG/About Atomic Search/g' /app/searx/infopage/*/about.md && \
    sed -i 's/searxng-version/atomic-search-version/g' /app/searx/templates/simple/base.html && \
    sed -i 's/searxng_version/atomic_search_version/g' /app/searx/webapp.py 2>/dev/null || true

# Add healthcheck endpoint
RUN sed -i "/from flask import/i\\
\\
@app.route('/healthz')\\
def healthz():\\
    return 'OK', 200\\
" /app/searx/webapp.py

# Set environment
ENV PYTHONUNBUFFERED=1
ENV SEARXNG_DATA_DIR=/app/searxng-data
ENV SEARXNG_SETTINGS=/app/searx/settings.yml

# Create data directory
RUN mkdir -p /app/searxng-data

EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -sf http://localhost:8080/healthz || curl -sf http://localhost:8080/ || exit 1

CMD ["python", "-m", "searx.webapp"]
