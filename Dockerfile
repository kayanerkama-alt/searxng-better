# Atomic Search - Uses Official SearXNG Image
# This is the ONLY guaranteed working approach
FROM searxng/searxng:latest

LABEL maintainer="UCXP Project"

# Copy custom themes ON TOP of official image
COPY --chown=searxng:searxng ./out/ /etc/searxng/static/themes/simple/

# Copy limiter config
COPY --chown=searxng:searxng ./src/limiter.toml /etc/searxng/limiter.toml

# Create hello endpoint for healthcheck
RUN echo '
@app.route("/healthz")
def healthz():
    return "OK", 200
' >> /usr/local/searxng/searx/webapp.py

# Set brand name
ENV SEARXNG_BRAND_NAME="Atomic Search"
ENV SEARXNG_INSTANCE_NAME="Atomic Search"

EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/healthz || exit 1

CMD ["searxng"]
