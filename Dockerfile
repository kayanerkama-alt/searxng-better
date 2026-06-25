# Atomic Search - Production Dockerfile
# A privacy-first metasearch engine with Kagi-style UI
FROM docker.io/library/python:3.13-alpine AS builder

# Latest upstream SearXNG commit
ENV UPSTREAM_COMMIT=e3126b89e69d1a56488f54f27928581a897cb058

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    brotli \
    git \
    libxml2-dev \
    libxslt-dev \
    zlib-dev \
    openssl-dev \
    cargo \
    rust

WORKDIR /usr/local/searxng/

# Clone SearXNG and install dependencies
RUN git config --global --add safe.directory /usr/local/searxng \
&& git clone https://github.com/searxng/searxng . \
&& git reset --hard ${UPSTREAM_COMMIT}

# Create virtual environment and install dependencies
RUN python -m venv ./venv \
&& . ./venv/bin/activate \
&& pip install --upgrade pip \
&& pip install --no-cache-dir -r requirements.txt \
&& pip install --no-cache-dir "granian~=2.0" \
&& python -m searx.version freeze

# Create searxng user/group
ARG SEARXNG_UID=977
ARG SEARXNG_GID=977

RUN grep -m1 root /etc/group > /tmp/.searxng.group \
&& grep -m1 root /etc/passwd > /tmp/.searxng.passwd \
&& echo "searxng:x:$SEARXNG_GID:" >> /tmp/.searxng.group \
&& echo "searxng:x:$SEARXNG_UID:$SEARXNG_GID:searxng:/usr/local/searxng:/bin/sh" >> /tmp/.searxng.passwd

# Copy custom themes
COPY ./out/ searx/static/themes/simple/

# Precompile static files
RUN . ./venv/bin/activate && python -m compileall -q searx \
&& find searx/static \
    \( -name '*.html' -o -name '*.css' -o -name '*.js' -o -name '*.svg' -o -name '*.ttf' -o -name '*.eot' \) \
    -type f -exec gzip -9 -k {} + -exec brotli --best {} + 2>/dev/null || true

# Runtime stage
FROM docker.io/library/python:3.13-alpine

WORKDIR /usr/local/searxng/

RUN apk add --no-cache libxslt dumb-init wget curl

# Copy from builder
COPY --chown=root:root --from=builder /tmp/.searxng.passwd /etc/passwd
COPY --chown=root:root --from=builder /tmp/.searxng.group /etc/group
COPY --chown=searxng:searxng --from=builder /usr/local/searxng /usr/local/searxng

# Copy custom files
COPY --chown=searxng:searxng ./src/run.sh /usr/local/bin/run.sh
COPY --chown=searxng:searxng ./src/limiter.toml /etc/searxng/limiter.toml
COPY --chown=searxng:searxng ./src/favicons.toml /etc/searxng/favicons.toml

# Theme support patches
RUN sed -i "/'simple_style': EnumStringSetting(/,/center_alignment/ s/choices=\[\"\", \"auto\", \"light\", \"dark\", \"black\"\]/choices=[\"\", \"auto\", \"light\", \"dark\", \"black\", \"paulgo\", \"latte\", \"frappe\", \"macchiato\", \"mocha\", \"kagi\", \"brave\", \"moa\", \"night\", \"dracula\", \"gruvbox\", \"gruvboxmat\", \"everforest\", \"nord\", \"matcha\", \"evergarden\", \"cyberpunk\", \"ocean\", \"forest\", \"sunset\", \"matrix\", \"sakura\", \"pixel\", \"solarized\", \"hacker\", \"arctic\", \"crimson\", \"cobalt\", \"amber\", \"violet\", \"mint\", \"lavender\", \"slate\", \"rose\", \"sky\", \"terminal\", \"cosmic\"]/" searx/preferences.py \
&& sed -i "s/SIMPLE_STYLE = ('auto', 'light', 'dark', 'black')/SIMPLE_STYLE = ('auto', 'light', 'dark', 'black', 'paulgo', 'latte', 'frappe', 'macchiato', 'mocha', 'kagi', 'brave', 'moa', 'night', 'dracula', 'gruvbox', 'gruvboxmat', 'everforest', 'nord', 'matcha', 'evergarden', 'cyberpunk', 'ocean', 'forest', 'sunset', 'matrix', 'sakura', 'pixel', 'solarized', 'hacker', 'arctic', 'crimson', 'cobalt', 'amber', 'violet', 'mint', 'lavender', 'slate', 'rose', 'sky', 'terminal', 'cosmic')/" searx/settings_defaults.py \
&& sed -i "s/{%- for name in \['auto', 'light', 'dark', 'black'\] -%}/{%- for name in \['auto', 'light', 'dark', 'black', 'paulgo', 'latte', 'frappe', 'macchiato', 'mocha', 'kagi', 'brave', 'moa', 'night', 'dracula', 'gruvbox', 'gruvboxmat', 'everforest', 'nord', 'matcha', 'evergarden', 'cyberpunk', 'ocean', 'forest', 'sunset', 'matrix', 'sakura', 'pixel', 'solarized', 'hacker', 'arctic', 'crimson', 'cobalt', 'amber', 'violet', 'mint', 'lavender', 'slate', 'rose', 'sky', 'terminal', 'cosmic'\] -%}/" searx/templates/simple/preferences/theme.html

# Privacy policy page
COPY --chown=searxng:searxng ./src/privacy-policy/privacy-policy.html searx/templates/simple/privacy-policy.html
RUN sed -i "/@app\.route('\/client<token>\.css', methods=\['GET', 'POST'\])/i \\\n@app.route('\/privacy', methods=\['GET'\])\ndef privacy_policy():return render('privacy-policy.html')\n" searx/webapp.py

# Donation page
COPY --chown=searxng:searxng ./src/donation/donation.html searx/templates/simple/donation.html
RUN sed -i "/render('privacy-policy.html')/a @app.route('/donate', methods=['GET'])" searx/webapp.py \
&& sed -i "/@app.route('\/donate', methods=\['GET'\])/a def donate():return render('donation.html')" searx/webapp.py

# Captcha support
COPY --chown=searxng:searxng ./src/captcha/captcha.py searx/captcha.py
COPY --chown=searxng:searxng ./src/captcha/captcha.html searx/templates/simple/captcha.html
RUN sed -i '/search_obj = searx.search.SearchWithPlugins/i\        from searx.captcha import handle_captcha\n        if (captcha_response := handle_captcha(sxng_request, settings["server"]["secret_key"], raw_text_query, search_query, selected_locale)):\n            return captcha_response\n' searx/webapp.py

# Authorized API
COPY --chown=searxng:searxng ./src/auth/auth.py searx/auth.py
RUN sed -i "/if output_format not in settings\['search'\]\['formats'\]:/a\\        from searx.auth import valid_api_key\\n        if (not valid_api_key(sxng_request)):" searx/webapp.py \
&& sed -i "/return Response('', mimetype='text\/css')/a \\\n@app.route('/<key>/search', methods=['GET', 'POST'])\\ndef search_key(key=None):\\n    from searx.auth import auth_search_key\\n    return auth_search_key(sxng_request, key)" searx/webapp.py

# Supplemental engines
COPY --chown=searxng:searxng ./src/search/supplemental_timeout.py searx/search/supplemental_timeout.py
COPY --chown=searxng:searxng ./src/search/google_autocomplete_icons.py searx/search/google_autocomplete_icons.py
COPY --chown=searxng:searxng ./src/search/privau_wsgi.py searx/privau_wsgi.py

# Fix autocompleter
RUN sed -i '/{% if autocomplete %}/,/{% endif %}/s|method="{{ opensearch_method }}"|method="GET"|g' searx/templates/simple/opensearch.xml

# Default settings optimized for privacy and performance
RUN sed -i -e "/safe_search:/s/0/1/g" \
-e "/autocomplete:/s/\"\"/\"google\"/g" \
-e "/autocomplete_min:/s/4/0/g" \
-e "/favicon_resolver:/s/\"\"/\"google\"/g" \
-e "/port:/s/8888/8080/g" \
-e "/simple_style:/s/auto/macchiato/g" \
-e '/searx\.plugins\.infinite_scroll\.SXNGPlugin:/{n;s/active: false/active: true/;}' \
-e "/query_in_title:/s/false/true/g" \
-e '/default_lang:/s/ ""/ en/g' \
-e "/method:/s/\"POST\"/\"GET\"/g" \
-e "/http_protocol_version:/s/1.0/1.1/g" \
-e "s/# max_request_timeout: 10.0/max_request_timeout: 5.0/g" \
-e "/X-Content-Type-Options: nosniff/d" \
-e "/X-XSS-Protection: 1; mode=block/d" \
-e "/X-Robots-Tag: noindex, nofollow/d" \
-e "/Referrer-Policy: no-referrer/d" \
-e "/news:/{n;s/.*//}" \
-e "/files:/d" \
-e "/social media:/d" \
-e "/static_use_hash:/s/false/true/g" \
-e "s/    use_mobile_ui: false/    use_mobile_ui: true/g" \
-e "/disabled: false/d" \
-e "/name: aol/s/$/\n    disabled: true/g" \
-e "/name: currency/s/$/\n    disabled: false/g" \
-e "/name: qwant/s/$/\n    disabled: true/g" \
-e "/name: ddg definitions/,+5{/disabled: true/d;}" \
-e "/shortcut: fd/{n;s/.*/    disabled: false/}" \
searx/settings.yml

# Healthcheck endpoint - add to webapp.py
RUN grep -q "@app.route('/healthz'" searx/webapp.py || \
sed -i "/from flask import/i\\
\\
@app.route('/healthz', methods=['GET'])\\
def healthz():\\
    return 'OK', 200\\
" searx/webapp.py

EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD wget --spider -q http://localhost:8080/healthz 2>/dev/null || \
    curl -f http://localhost:8080/healthz 2>/dev/null || exit 1

# Environment defaults
ENV GRANIAN_PROCESS_NAME="atomic-search" \
    GRANIAN_INTERFACE="wsgi" \
    GRANIAN_HOST="0.0.0.0" \
    GRANIAN_PORT="8080" \
    GRANIAN_WEBSOCKETS="false" \
    GRANIAN_BLOCKING_THREADS="4" \
    GRANIAN_WORKERS_KILL_TIMEOUT="30" \
    IMAGE_PROXY="true" \
    NAME="Atomic Search"

USER searxng

# Direct startup command for Railway/Render
CMD ["/bin/sh", "-c", "exec /usr/local/searxng/venv/bin/granian --host 0.0.0.0 --port 8080 --workers 2 searx.privau_wsgi:app"]
