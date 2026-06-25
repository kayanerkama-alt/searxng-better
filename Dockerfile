# Atomic Search - Uses Official SearXNG Image
FROM searxng/searxng:latest

LABEL maintainer="UCXP Project"

# Copy custom themes (71+ themes)
COPY --chown=searxng:searxng ./out/themes/ /etc/searxng/static/themes/simple/

# Copy limiter config
COPY --chown=searxng:searxng ./src/limiter.toml /etc/searxng/limiter.toml

# Set brand name
ENV SEARXNG_BRAND_NAME="Atomic Search"
ENV SEARXNG_INSTANCE_NAME="Atomic Search"
ENV SEARXNG_UI_DEFAULT_SETTINGS='{"simple_style": "macchiato"}'

EXPOSE 8080

# Healthcheck - use root path
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1

CMD ["searxng"]
