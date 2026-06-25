# Atomic Search - Production Dockerfile
# Rebranded by UCXP Project
# Fixed for Railway/Render deployment

# Stage 1: Builder
FROM python:3.13-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    git \
    libxml2-dev \
    libxslt-dev \
    zlib-dev \
    openssl-dev \
    cargo \
    rust

WORKDIR /app

# Clone SearXNG
ARG SEARXNG_COMMIT=e3126b89e69d1a56488f54f27928581a897cb058
RUN git clone --depth 1 https://github.com/searxng/searxng.git . && \
    git fetch --depth 1 origin ${SEARXNG_COMMIT} && \
    git reset --hard ${SEARXNG_COMMIT}

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install granian

# Stage 2: Runtime
FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random

# Install runtime dependencies
RUN apk add --no-cache libxslt dumb-init curl

# Create user
RUN addgroup -S atomic && adduser -S atomic -G atomic

WORKDIR /app

# Copy from builder
COPY --from=builder /opt /opt
COPY --from=builder /app /app

# Copy custom settings
COPY --chown=atomic:atomic ./src/settings.yml /app/searx/settings.yml

# Copy themes
COPY --chown=atomic:atomic ./out/themes/ /app/searx/static/themes/simple/

# Copy JS enhancements
COPY --chown=atomic:atomic ./out/js/ /app/searx/static/themes/simple/js/

# Healthcheck endpoint patch
RUN sed -i "/from flask import/a\\
@app.route('/healthz')\\
def healthz():\\
    return 'OK', 200\\
" /app/searx/webapp.py 2>/dev/null || true

# Branding patch - change instance name
RUN sed -i 's/instance_name: "SearXNG"/instance_name: "Atomic Search"/' /app/searx/settings.yml || true

# Set permissions
RUN chown -R atomic:atomic /app

USER atomic

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -sf http://localhost:8080/healthz || curl -sf http://localhost:8080/ || exit 1

ENV SEARXNG_DATA_DIR=/app/searxng-data
ENV SEARXNG_SETTINGS=/app/searx/settings.yml

CMD ["python", "-m", "searx.webapp"]
