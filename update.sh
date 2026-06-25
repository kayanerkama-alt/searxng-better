#!/bin/sh

# Atomic Search - Theme Build Script

if [ ! -d build ]
then
    git clone https://github.com/searxng/searxng.git build
else
    cd build
    git restore .
    git pull https://github.com/searxng/searxng.git
    cd ..
fi

echo "🔄 Replacing Atomic Search theme definitions..."
cp -v src/less/* build/client/simple/src/less/
mkdir -p build/client/simple/src/less/themes && cp -v src/less/themes/* build/client/simple/src/less/themes/
cp -v src/less/result_types/* build/client/simple/src/less/result_types/
cp -v src/js/* build/client/simple/src/js/main/

echo "📄 Enabling privacy page..."
if ! grep -q '@import "privacypage.less";' build/client/simple/src/less/style.less; then
  sed -i 's/@import "definitions.less";/@import "definitions.less";\n@import "privacypage.less";/' build/client/simple/src/less/style.less
fi

echo "💝 Enabling donation page styles..."
if ! grep -q '@import "donationpage.less";' build/client/simple/src/less/style.less; then
  sed -i 's/@import "privacypage.less";/@import "privacypage.less";\n@import "donationpage.less";/' build/client/simple/src/less/style.less
fi

echo "🔐 Enabling captcha page styles..."
if ! grep -q '@import "captchapage.less";' build/client/simple/src/less/style.less; then
  sed -i 's/@import "donationpage.less";/@import "donationpage.less";\n@import "captchapage.less";/' build/client/simple/src/less/style.less
fi

echo "⚙️ Building static files..."
cd build
make themes.all
cd ..

echo "📦 Copying build files into output folder..."
rm -rf out/*
cp -r -v build/searx/static/themes/simple/* out/

# Preserve Atomic Search logos
echo "🎨 Preserving Atomic Search logos..."
cp -v src/less/../out/img/atomic.svg out/img/ 2>/dev/null || true
cp -v src/less/../out/img/atomic-icon.svg out/img/ 2>/dev/null || true

# Update searxng logo references to atomic
echo "✨ Updating logo references to Atomic Search..."
if [ -f out/img/searxng.svg ]; then
    cp out/img/atomic.svg out/img/searxng.svg
fi
if [ -f out/img/searxng.png ]; then
    # Just keep the PNG, we'll use SVG for logo
    cp out/img/atomic.svg out/img/searxng.svg 2>/dev/null || true
fi

echo "✅ Build complete!"
