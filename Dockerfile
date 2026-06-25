# Atomic Search - Production Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential libxml2-dev libxslt-dev zlib1g-dev \
    libffi-dev libssl-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clone SearXNG (this creates /app/searx/ as the package)
ARG SEARXNG_COMMIT=e3126b89e69d1a56488f54f27928581a897cb058
RUN git clone --depth 1 https://github.com/searxng/searxng.git . && \
    git fetch --depth 1 origin ${SEARXNG_COMMIT} && \
    git reset --hard ${SEARXNG_COMMIT}

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy our custom source files INTO SearXNG structure
COPY ./src/templates/ ./searx/templates/
COPY ./src/static/ ./searx/static/
COPY ./src/settings.yml ./searx/settings.yml
COPY ./src/js/ ./searx/js/
COPY ./src/less/ ./searx/less/

# Copy compiled themes/CSS to SearXNG static folder
COPY ./out/ ./searx/static/themes/simple/

# Copy search plugins (individual files to avoid glob issues)
RUN if [ -d ./src/search ]; then \
      for f in ./src/search/*.py; do \
        [ -f "$f" ] && cp "$f" ./searx/search/; \
      done \
    fi || true

# Branding replacement in settings
RUN sed -i 's/"SearXNG"/"Atomic Search"/g' ./searx/settings.yml && \
    sed -i 's/SearXNG/Atomic Search/g' ./searx/settings.yml

# Environment - generate secret at runtime
ENV PYTHONUNBUFFERED=1
ENV SEARXNG_DATA_DIR=/app/searxng-data
ENV SEARXNG_SETTINGS=/app/searx/settings.yml

# Generate random secret for runtime (overridden by Railway's PORT env)
RUN SECRET=$(openssl rand -hex 32) && \
    sed -i "s/atomic-search-secret-change-me-in-production/$SECRET/" /app/searx/settings.yml

RUN mkdir -p /app/searxng-data

EXPOSE 8888

# Run SearXNG on port 8888
CMD ["python", "-m", "searx.webapp", "--bind", "0.0.0.0", "--port", "8888"]
