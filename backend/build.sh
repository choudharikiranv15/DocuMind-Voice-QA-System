#!/bin/bash
# Optimized build script for Render with aggressive caching

set -e  # Exit on error

echo "========================================="
echo "DokGuru Voice - Optimized Build Process"
echo "========================================="

# Upgrade pip and install wheel support
echo "→ Upgrading pip..."
pip install --quiet --upgrade pip setuptools wheel

# Check if we can use cached dependencies
CACHE_KEY="requirements-production.txt"
CACHE_FILE="/opt/render/.cache/pip-installed-${CACHE_KEY//\//-}.flag"

if [ -f "$CACHE_FILE" ] && ! git diff --quiet HEAD@{1} HEAD -- requirements-production.txt 2>/dev/null; then
    echo "✓ Requirements unchanged - using cached dependencies"
    echo "→ This should be much faster!"
else
    echo "→ Installing Python dependencies..."
    echo "   (This may take 15-20 minutes on first build due to ML packages)"

    # Install with prefer-binary to use pre-built wheels
    pip install -r requirements-production.txt \
        --prefer-binary \
        --compile \
        --no-warn-script-location

    # Mark cache as valid
    mkdir -p "$(dirname "$CACHE_FILE")"
    touch "$CACHE_FILE"

    echo "✓ Dependencies installed and cached"
fi

echo "========================================="
echo "✓ Build completed successfully"
echo "========================================="
