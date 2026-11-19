#!/bin/sh
# ePlus AI Toolkit macOS launcher — read-only Step 0/1.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if [ "$(uname -s)" != "Darwin" ]; then
  printf '%s\n' "This launcher is for macOS. On Windows use .\\run-all.ps1." >&2
  exit 2
fi
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' "Python 3.10+ is required. Install Python and try again." >&2
  exit 2
fi
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
  printf '%s\n' "Python 3.10+ is required. Upgrade Python and try again." >&2
  exit 2
fi
if ! command -v adb >/dev/null 2>&1; then
  printf '%s\n' "ADB is required. Install Android SDK Platform-Tools (brew install android-platform-tools)." >&2
  exit 2
fi
if [ ! -x .venv/bin/python ]; then
  printf '%s\n' "Preparing a local Python environment (.venv)..."
  python3 -m venv .venv
fi
PYTHON=.venv/bin/python
if ! "$PYTHON" -c "import textual; import frida; assert frida.__version__ == '16.5.9'" >/dev/null 2>&1; then
  printf '%s\n' "Installing pinned Textual and Frida dependencies into .venv..."
  "$PYTHON" -m pip install --disable-pip-version-check -r requirements-tui.txt 'frida==16.5.9'
fi
export PYTHONIOENCODING=utf-8:backslashreplace
export PYTHONUTF8=1
if [ "${1:-}" = "--check" ]; then
  exec "$PYTHON" macos_runner.py --step 0
elif [ "${1:-}" = "--list" ]; then
  exec "$PYTHON" macos_runner.py --step 1
elif [ "$#" -ne 0 ]; then
  printf '%s\n' "macOS supports: ./run-macos.sh [--check | --list]. Checkout stages 2-5 are disabled." >&2
  exit 2
fi
exec "$PYTHON" tui.py
