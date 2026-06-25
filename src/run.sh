#!/bin/bash
# Atomic Search - Simple Startup Script
# Based on SearXNG | Rebranded by UCXP Project

set -e

echo "🔮 Starting Atomic Search..."

# Change to app directory
cd /app

# Set environment
export PYTHONUNBUFFERED=1
export SEARXNG_DATA_DIR="${SEARXNG_DATA_DIR:-/app/searx/data}"
export SEARXNG_SETTINGS="${SEARXNG_SETTINGS:-/app/searx/settings.yml}"

# Create data directory if needed
mkdir -p "$SEARXNG_DATA_DIR"

# Add healthcheck endpoint if not present
if ! grep -q "def healthz" searx/webapp.py 2>/dev/null; then
    # Add after imports
    sed -i "/from flask import/a\\
\\
@app.route('/healthz', methods=['GET'])\\
def healthz():\\
    return 'OK', 200" searx/webapp.py 2>/dev/null || true
fi

# Set instance name
if [ -n "$NAME" ]; then
    sed -i "s/instance_name:.*/instance_name: $NAME/" searx/settings.yml 2>/dev/null || true
fi

# Enable image proxy
if [ "$IMAGE_PROXY" = "true" ]; then
    sed -i 's/^image_proxy:.*/image_proxy: true/' searx/settings.yml 2>/dev/null || true
fi

# Set secret key if not set
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY="$(head -c 32 /dev/urandom | base64)"
fi

# Set listen address
HOST="${GRANIAN_HOST:-0.0.0.0}"
PORT="${GRANIAN_PORT:-8080}"

echo "📍 Listening on $HOST:$PORT"

# Run granian
exec /opt/venv/bin/granian \
    --host "$HOST" \
    --port "$PORT" \
    --workers 2 \
    --threads 4 \
    --name "atomic-search" \
    searx.privau_wsgi:app
