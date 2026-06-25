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

# Copy Atomic Search logos to build img folder
echo "🎨 Copying Atomic Search logos to build..."
mkdir -p build/client/simple/src/img
cp -v src/static/img/*.svg build/client/simple/src/img/ 2>/dev/null || true

echo "⚙️ Building static files..."
cd build
make themes.all
cd ..
if [ $? -ne 0 ]; then
    echo "⚠️ Theme build failed, using previous build..."
fi

echo "📦 Copying build files into output folder..."
rm -rf out/*
cp -r -v build/searx/static/themes/simple/* out/

# Ensure Atomic Search logos exist in output
echo "✨ Copying Atomic Search logos to output..."
cp -v src/static/img/atomic-logo.svg out/img/atomic.svg 2>/dev/null || true
cp -v src/static/img/searxng.svg out/img/searxng.svg 2>/dev/null || true

echo "✅ Build complete!"
