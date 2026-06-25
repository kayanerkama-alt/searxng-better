#!/bin/sh

# Atomic Search - Theme Build Script

if [ ! -d build ]
then
    git clone https://github.com/searxng/searxng.git build
else
    cd build
    # Don't restore index.less - we need our custom version
    git checkout -- client/simple/src/less/index.less 2>/dev/null || true
    git pull https://github.com/searxng/searxng.git
    cd ..
fi

echo "🔄 Replacing Atomic Search theme definitions..."
# Copy custom themes and features
mkdir -p build/client/simple/src/less/themes && cp -v src/less/themes/* build/client/simple/src/less/themes/
cp -v src/less/result_types/* build/client/simple/src/less/result_types/
cp -v src/js/* build/client/simple/src/js/main/

# Fix index.less to use img tag instead of background (MUST be after git restore)
echo "🔧 Fixing index.less for logo display..."
if grep -q 'background: url("./img/searxng.png")' build/client/simple/src/less/index.less; then
  sed -i 's|background: url("./img/searxng.png") no-repeat;|img.index-logo { max-width: 200px; height: auto; margin: 0 auto 2rem; display: block; }|g' build/client/simple/src/less/index.less
  sed -i 's|min-height: 4rem;|min-height: 0;|g' build/client/simple/src/less/index.less
  sed -i 's|background-position: center;||g' build/client/simple/src/less/index.less
  sed -i 's|background-size: contain;||g' build/client/simple/src/less/index.less
  echo "✅ index.less fixed"
else
  echo "⚠️ index.less already fixed or not found"
fi

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

# Add logo CSS directly to the CSS file (fallback if less compilation doesn't include it)
echo "📝 Adding logo CSS to compiled stylesheets..."
LOGO_CSS=".index-logo{max-width:200px;height:auto;margin:0 auto 2rem;display:block}.logo{max-height:40px;width:auto}"
for css_file in out/sxng-ltr.min.css out/sxng-rtl.min.css build/searxng/searx/static/themes/simple/sxng-ltr.min.css build/searxng/searx/static/themes/simple/sxng-rtl.min.css; do
  if [ -f "$css_file" ]; then
    echo "$LOGO_CSS" >> "$css_file"
    echo "✅ Added logo CSS to $css_file"
  fi
done

echo "✅ Build complete!"
