# Atomic Search - PRODUCTION Dockerfile
# Privacy-first search engine with Kagi-style features

FROM python:3.12-slim

LABEL maintainer="Atomic Search"
LABEL description="Privacy-first search engine"

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

# Copy Atomic Search custom features
COPY --chown=root:root ./src/search/*.py /app/searx/search/

# Complete branding replacement
RUN sed -i 's/"SearXNG"/"Atomic Search"/g' /app/searx/settings.yml && \
    sed -i 's/SearXNG/Atomic Search/g' /app/searx/settings.yml && \
    sed -i 's/port: 8888/port: 8000/g' /app/searx/settings.yml

# Set environment
ENV PYTHONUNBUFFERED=1
ENV SEARXNG_DATA_DIR=/app/searxng-data
ENV SEARXNG_SETTINGS=/app/searx/settings.yml
ENV SEARXNG_PORT=8000
ENV SEARXNG_BIND_ADDRESS=0.0.0.0

# Create data directory
RUN mkdir -p /app/searxng-data

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -sf http://localhost:8000/ || exit 1

# Run on port 8000
CMD ["python", "-m", "searx.webapp", "--port", "8000", "--bind", "0.0.0.0"]
