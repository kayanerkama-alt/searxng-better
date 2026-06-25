# Atomic Search - Production Optimized Dockerfile
# Optimized for Railway, Render, and other cloud platforms
# Multi-stage build for smaller image size

# Stage 1: Builder
FROM docker.io/library/python:3.13-alpine AS builder

# Latest upstream SearXNG commit
ENV UPSTREAM_COMMIT=e3126b89e69d1a56488f54f27928581a897cb058 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    brotli \
    git \
    libxml2-dev \
    libxslt-dev \
    zlib-dev \
    openssl-dev

WORKDIR /usr/local/searxng/

# Clone and setup SearXNG
RUN git config --global --add safe.directory /usr/local/searxng \
&& git clone https://github.com/searxng/searxng.git . \
&& git reset --hard ${UPSTREAM_COMMIT}

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv \
&& . /opt/venv/bin/activate \
&& pip install --upgrade pip \
&& pip install -r requirements.txt \
&& pip install "granian[pname]~=2.0" \
&& python -m searx.version freeze

# Stage 2: Runtime
FROM docker.io/library/python:3.13-alpine AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random

# Install runtime dependencies only
RUN apk add --no-cache \
    libxslt \
    dumb-init

# Create non-root user
RUN addgroup -S atomic && adduser -S atomic -G atomic

WORKDIR /usr/local/searxng/

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /usr/local/searxng /usr/local/searxng

# Copy custom files
COPY --chown=atomic:atomic ./src/run.sh /usr/local/bin/run.sh
COPY --chown=atomic:atomic ./src/limiter.toml /etc/searxng/limiter.toml
COPY --chown=atomic:atomic ./src/favicons.toml /etc/searxng/favicons.toml

# Copy static theme files
COPY --chown=atomic:atomic ./out/ /usr/local/searxng/searx/static/themes/simple/

# Precompile Python files for faster startup
RUN . /opt/venv/bin/activate \
&& python -m compileall -q /usr/local/searxng/searx \
&& find /usr/local/searxng/searx/static \
    \( -name '*.html' -o -name '*.css' -o -name '*.js' -o -name '*.svg' -o -name '*.ttf' -o -name '*.eot' \) \
    -type f -exec gzip -9 -k {} + -exec brotli --best {} + 2>/dev/null || true

# Apply SearXNG patches
RUN sed -i "/'simple_style': EnumStringSetting(/,/center_alignment/ s/choices=\[\"\", \"auto\", \"light\", \"dark\", \"black\"\]/choices=[\"\", \"auto\", \"light\", \"dark\", \"black\", \"paulgo\", \"latte\", \"frappe\", \"macchiato\", \"mocha\", \"kagi\", \"brave\", \"moa\", \"night\", \"dracula\", \"gruvbox\", \"gruvboxmat\", \"everforest\", \"nord\", \"matcha\", \"evergarden\", \"cyberpunk\", \"ocean\", \"forest\", \"sunset\", \"matrix\", \"sakura\", \"pixel\", \"solarized\", \"hacker\", \"arctic\", \"crimson\", \"cobalt\", \"amber\", \"violet\", \"mint\", \"lavender\", \"slate\", \"rose\", \"sky\", \"terminal\", \"cosmic\"]/" searx/preferences.py \
&& sed -i "s/SIMPLE_STYLE = ('auto', 'light', 'dark', 'black')/SIMPLE_STYLE = ('auto', 'light', 'dark', 'black', 'paulgo', 'latte', 'frappe', 'macchiato', 'mocha', 'kagi', 'brave', 'moa', 'night', 'dracula', 'gruvbox', 'gruvboxmat', 'everforest', 'nord', 'matcha', 'evergarden', 'cyberpunk', 'ocean', 'forest', 'sunset', 'matrix', 'sakura', 'pixel', 'solarized', 'hacker', 'arctic', 'crimson', 'cobalt', 'amber', 'violet', 'mint', 'lavender', 'slate', 'rose', 'sky', 'terminal', 'cosmic')/" searx/settings_defaults.py \
&& sed -i "s/{%- for name in \['auto', 'light', 'dark', 'black'\] -%}/{%- for name in \['auto', 'light', 'dark', 'black', 'paulgo', 'latte', 'frappe', 'macchiato', 'mocha', 'kagi', 'brave', 'moa', 'night', 'dracula', 'gruvbox', 'gruvboxmat', 'everforest', 'nord', 'matcha', 'evergarden', 'cyberpunk', 'ocean', 'forest', 'sunset', 'matrix', 'sakura', 'pixel', 'solarized', 'hacker', 'arctic', 'crimson', 'cobalt', 'amber', 'violet', 'mint', 'lavender', 'slate', 'rose', 'sky', 'terminal', 'cosmic'\] -%}/" searx/templates/simple/preferences/theme.html

# Privacy policy page
COPY --chown=atomic:atomic ./src/privacy-policy/privacy-policy.html searx/templates/simple/privacy-policy.html
RUN sed -i "/@app\.route('\/client<token>\.css', methods=\['GET', 'POST'\])/i \ \n@app.route('\/privacy', methods=\['GET'\])\ndef privacy_policy():return render('privacy-policy.html')\n" searx/webapp.py

# Donation page
COPY --chown=atomic:atomic ./src/donation/donation.html searx/templates/simple/donation.html
RUN sed -i "/render('privacy-policy.html')/a @app.route('/donate', methods=\['GET'\])" searx/webapp.py && sed -i "/@app.route('\/donate', methods=\['GET'\])/a def donate():return render('donation.html')" searx/webapp.py

# Captcha support
COPY --chown=atomic:atomic ./src/captcha/captcha.py searx/captcha.py
COPY --chown=atomic:atomic ./src/captcha/captcha.html searx/templates/simple/captcha.html
RUN sed -i '/search_obj = searx.search.SearchWithPlugins(search_query, sxng_request, sxng_request.user_plugins)/i\        from searx.captcha import handle_captcha\n        if (captcha_response := handle_captcha(sxng_request, settings["server"]["secret_key"], raw_text_query, search_query, selected_locale)):\n            return captcha_response\n' searx/webapp.py \
&& sed -i "/return Response('OK', mimetype='text\/plain')/a \\\\n@app.route('/captcha', methods=['GET', 'POST'], endpoint='captcha')\\ndef captcha_view():\\n    from searx.captcha import captcha as captcha_page\\n    return captcha_page(sxng_request, settings['server']['secret_key'])" searx/webapp.py

# Authorized API
COPY --chown=atomic:atomic ./src/auth/auth.py searx/auth.py
RUN sed -i -e "/if output_format not in settings\\['search'\\]\\['formats'\\]:/a\\        from searx.auth import valid_api_key\\n        if (not valid_api_key(sxng_request)):" -e 's|flask.abort(403)|    flask.abort(403)|' searx/webapp.py \
&& sed -i "/return Response('', mimetype='text\/css')/a \\\\n@app.route('/<key>/search', methods=['GET', 'POST'])\\ndef search_key(key=None):\\n    from searx.auth import auth_search_key\\n    return auth_search_key(sxng_request, key)" searx/webapp.py \
&& sed -i "/3\. If the IP is not in either list, the request is not blocked\./a\\    from searx.auth import valid_api_key\\n    if (valid_api_key(sxng_request)):\\n        return None" searx/limiter.py

# Supplemental engines
COPY --chown=atomic:atomic ./src/search/supplemental_timeout.py searx/search/supplemental_timeout.py
COPY --chown=atomic:atomic ./src/search/google_autocomplete_icons.py searx/search/google_autocomplete_icons.py
COPY --chown=atomic:atomic ./src/search/privau_wsgi.py searx/privau_wsgi.py

# Fix autocompleter
RUN sed -i '/{% if autocomplete %}/,/{% endif %}/s|method="{{ opensearch_method }}"|method="GET"|g' searx/templates/simple/opensearch.xml

# Default settings - optimized for production
RUN sed -i -e "/safe_search:/s/0/1/g" \
-e "/autocomplete:/s/\"\"/\"google\"/g" \
-e "/autocomplete_min:/s/4/0/g" \
-e "/favicon_resolver:/s/\"\"/\"google\"/g" \
-e "/port:/s/8888/8080/g" \
-e "/simple_style:/s/auto/macchiato/g" \
-e "/instance_name:/s/SearXNG/Atomic Search/g" \
-e "s/SearXNG/Atomic Search/g" \
-e "s/About SearXNG/About Atomic Search/g" \
-e "s/SearXNG may not/Atomic Search may not/g" \
-e "s/SearXNG is a fork/Atomic Search is a fork/g" \
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
-e "/name: aol images/s/$/\n    disabled: true/g" \
-e "/name: aol videos/s/$/\n    disabled: true/g" \
-e "/name: karmasearch/s/$/\n    disabled: true/g" \
-e "/name: karmasearch images/s/$/\n    disabled: true/g" \
-e "/name: karmasearch videos/s/$/\n    disabled: true/g" \
-e "/name: karmasearch news/s/$/\n    disabled: true/g" \
-e "/name: wikispecies/s/$/\n    disabled: true/g" \
-e "/name: wikinews/s/$/\n    disabled: true/g" \
-e "/name: wikibooks/s/$/\n    disabled: true/g" \
-e "/name: wikivoyage/s/$/\n    disabled: true/g" \
-e "/name: wikiversity/s/$/\n    disabled: true/g" \
-e "/name: wikiquote/s/$/\n    disabled: true/g" \
-e "/name: wikisource/s/$/\n    disabled: true/g" \
-e "/name: wikicommons.images/s/$/\n    disabled: true/g" \
-e "/name: wikicommons.videos/s/$/\n    disabled: true/g" \
-e "/name: pinterest/s/$/\n    disabled: true/g" \
-e "/name: piped/s/$/\n    disabled: true/g" \
-e "/name: public domain image archive/s/$/\n    disabled: true/g" \
-e "/name: piped.music/s/$/\n    disabled: true/g" \
-e "/name: bandcamp/s/$/\n    disabled: true/g" \
-e "/name: radio browser/s/$/\n    disabled: true/g" \
-e "/name: mixcloud/s/$/\n    disabled: true/g" \
-e "/name: hoogle/s/$/\n    disabled: true/g" \
-e "/name: currency/s/$/\n    disabled: false/g" \
-e "/name: qwant/s/$/\n    disabled: true/g" \
-e "/name: btdigg/s/$/\n    disabled: true/g" \
-e "/name: lucide/s/$/\n    disabled: true/g" \
-e "/name: devicons/s/$/\n    disabled: true/g" \
-e "/name: pexels/s/$/\n    disabled: true/g" \
-e "/name: docker hub/s/$/\n    disabled: true/g" \
-e "/name: github/s/$/\n    disabled: true/g" \
-e "/name: semantic scholar/s/$/\n    disabled: true/g" \
-e "/name: openairedatasets/s/$/\n    disabled: true/g" \
-e "/name: sepiasearch/s/$/\n    disabled: true/g" \
-e "/name: dailymotion/s/$/\n    disabled: true/g" \
-e "/name: deviantart/s/$/\n    disabled: true/g" \
-e "/name: vimeo/s/$/\n    disabled: true/g" \
-e "/name: openairepublications/s/$/\n    disabled: true/g" \
-e "/name: library of congress/s/$/\n    disabled: true/g" \
-e "/name: dictzone/s/$/\n    disabled: true/g" \
-e "/name: baidu/s/$/\n    disabled: true/g" \
-e "/name: lingva/s/$/\n    disabled: fasle/g" \
-e "/name: genius/s/$/\n    disabled: true/g" \
-e "/name: wallhaven/s/$/\n    disabled: true/g" \
-e "/name: artic/s/$/\n    disabled: true/g" \
-e "/name: flickr/s/$/\n    disabled: true/g" \
-e "/name: unsplash/s/$/\n    disabled: true/g" \
-e "/name: gentoo/s/$/\n    disabled: true/g" \
-e "/name: openverse/s/$/\n    disabled: true/g" \
-e "/name: google videos/s/$/\n    disabled: true/g" \
-e "/name: yahoo news/s/$/\n    disabled: true/g" \
-e "/name: bing news/s/$/\n    disabled: true/g" \
-e "/name: tineye/s/$/\n    disabled: true/g" \
-e "/engine: startpage/s/$/\n    disabled: true/g" \
-e "/name: ddg definitions/,+5{/disabled: true/d;}" \
-e "/shortcut: fd/{n;s/.*/    disabled: false/}" \
searx/settings.yml;

# Set permissions
RUN chown -R atomic:atomic /usr/local/searxng

# Switch to non-root user
USER atomic

# Healthcheck for cloud platforms
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --spider -q http://localhost:8080/healthz || exit 1

EXPOSE 8080

# Environment variables with defaults
ENV GRANIAN_PROCESS_NAME="atomic-search" \
    GRANIAN_INTERFACE="wsgi" \
    GRANIAN_HOST="0.0.0.0" \
    GRANIAN_PORT="8080" \
    GRANIAN_WEBSOCKETS="false" \
    GRANIAN_BLOCKING_THREADS="4" \
    GRANIAN_WORKERS_KILL_TIMEOUT="30" \
    GRANIAN_BLOCKING_THREADS_IDLE_TIMEOUT="300" \
    IMAGE_PROXY="true" \
    NAME="Atomic Search"

CMD ["sh", "-c", "source /usr/local/bin/run.sh && exec /opt/venv/bin/granian searx.privau_wsgi:app"]
