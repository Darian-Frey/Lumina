#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Lumina build script
# -----------------------------------------------------------------------------
# Builds a standalone executable via PyInstaller.
#
# Usage:
#     ./build.sh
#
# The resulting binary will be in dist/Lumina. You can then run it directly
# or wrap it in an AppImage (see docs/packaging.md).
# -----------------------------------------------------------------------------

set -e

# Prefer Python 3.13 if available, fall back to python3
if command -v python3.13 &> /dev/null; then
    PYTHON=python3.13
else
    PYTHON=python3
fi

echo "Using Python: $($PYTHON --version)"

# Clean previous build artefacts
echo "Cleaning previous build..."
rm -rf build dist __pycache__

# Ensure PyInstaller is installed
if ! $PYTHON -c "import PyInstaller" &> /dev/null; then
    echo "PyInstaller not found. Install with: pip3 install --user pyinstaller"
    exit 1
fi

# Build
echo "Building Lumina..."
$PYTHON -m PyInstaller lumina.spec --clean --noconfirm

# Report result
if [ -f dist/Lumina ]; then
    SIZE=$(du -h dist/Lumina | cut -f1)
    echo ""
    echo "Build complete: dist/Lumina ($SIZE)"
    echo "Run with: ./dist/Lumina"
else
    echo ""
    echo "Build failed — no executable produced."
    exit 1
fi
