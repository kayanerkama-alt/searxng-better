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

# Copy source files (templates, static, settings)
COPY --chown=root:root ./src/ /app/searx/

# Copy themes from out folder to static/themes
COPY --chown=root:root ./out/themes/simple/* /app/searx/static/themes/simple/

# Copy additional features
COPY --chown=root:root ./src/search/privacy_features.py /app/searx/search/privacy_features.py
COPY --chown=root:root ./src/search/ranking_control.py /app/searx/search/ranking_control.py

# Patch branding - replace ALL SearXNG with Atomic Search in settings
RUN sed -i 's/"SearXNG"/"Atomic Search"/g' /app/searx/settings.yml && \
    sed -i 's/instance_name: "Atomic Search"/instance_name: "Atomic Search"/g' /app/searx/settings.yml

# Set environment
ENV PYTHONUNBUFFERED=1
ENV SEARXNG_DATA_DIR=/app/searxng-data
ENV SEARXNG_SETTINGS=/app/searx/settings.yml

# Create data directory
RUN mkdir -p /app/searxng-data

EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -sf http://localhost:8080/ || exit 1

CMD ["python", "-m", "searx.webapp"]
