# Atomic Search - Production Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential libxml2-dev libxslt-dev zlib1g-dev \
    libffi-dev libssl-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clone SearXNG
ARG SEARXNG_COMMIT=e3126b89e69d1a56488f54f27928581a897cb058
RUN git clone --depth 1 https://github.com/searxng/searxng.git . && \
    git fetch --depth 1 origin ${SEARXNG_COMMIT} && \
    git reset --hard ${SEARXNG_COMMIT}

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY --chown=root:root ./src/ /app/searx/
COPY --chown=root:root ./out/ /app/searx/static/themes/simple/
COPY --chown=root:root ./src/search/*.py /app/searx/search/ 2>/dev/null || true

# Branding
RUN sed -i 's/"SearXNG"/"Atomic Search"/g' /app/searx/settings.yml 2>/dev/null || true && \
    sed -i 's/SearXNG/Atomic Search/g' /app/searx/settings.yml 2>/dev/null || true

# Environment - Railway provides PORT, default to 8888
ENV PYTHONUNBUFFERED=1
ENV SEARXNG_DATA_DIR=/app/searxng-data
ENV SEARXNG_SETTINGS=/app/searx/settings.yml
ENV PORT=8888

RUN mkdir -p /app/searxng-data

EXPOSE 8888

# Run - use Railway's PORT if set, otherwise 8888
CMD ["sh", "-c", "python -m searx.webapp --bind 0.0.0.0 --port ${PORT:-8888}"]
