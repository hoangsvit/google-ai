#!/bin/sh
# Native Linux launcher for ePlus AI Toolkit. Checkout requires TUI approval.
set -eu

usage() {
  printf '%s\n' \
    "ePlus AI Toolkit — Linux (Textual, Steps 0–5)" \
    "Usage: sh run-linux.sh [--check | --list | --step N [--sequence] | --sequence | --help]" \
    "  (no flags)    Textual dashboard, including optional confirmed checkout" \
    "  --check       Android/Frida setup diagnostics (can change device settings)" \
    "  --list        Query offers (can prepare Android, no checkout)" \
    "  --step N      Open the dashboard with Step 0..5 selected" \
    "  --sequence    Open dashboard with guided sequence controls" \
    "  --help        Display usage" \
    "Steps 2–5 can submit real charges after explicit TUI confirmations."
}
if [ "$#" -eq 1 ] && { [ "$1" = "--help" ] || [ "$1" = "-h" ]; }; then
  usage
  exit 0
fi

MODE=""
case "$#" in
  0) MODE="tui" ;;
  1) case "$1" in
    --check) MODE="check" ;;
    --list) MODE="list" ;;
    --sequence) MODE="tui" ;;
    *) usage >&2; exit 2 ;;
  esac ;;
  2|3)
    if [ "$1" != "--step" ]; then usage >&2; exit 2; fi
    case "$2" in
      0|1|2|3|4|5) : ;;
      *) usage >&2; exit 2 ;;
    esac
    if [ "$#" -eq 3 ] && [ "$3" != "--sequence" ]; then usage >&2; exit 2; fi
    MODE="tui" ;;
  *) usage >&2; exit 2 ;;
esac

if [ "$(uname -s)" != "Linux" ]; then
  printf '%s\n' "This launcher requires Linux. Use run-macos.sh on macOS or run-all.ps1 on Windows." >&2
  exit 2
fi
if ! command -v python3 >/dev/null 2>&1 ||
   ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
  printf '%s\n' "Install Python 3.10+ to run this toolkit." >&2
  exit 2
fi
if ! adb=$(command -v "${ADB_PATH:-adb}") || [ ! -x "$adb" ] || [ -d "$adb" ]; then
  printf '%s\n' "Install Android SDK Platform-Tools and add adb to PATH or set ADB_PATH to its executable." >&2
  exit 2
fi
case "$adb" in
  /*) ;;
  *) adb="$PWD/$adb" ;;
esac
export ADB_PATH="$adb"

cd "$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
if [ ! -x .venv/bin/python ] && ! python3 -m venv .venv; then
  printf '%s\n' "Could not create .venv. Install python3-venv (or the venv package for your Python version) and check this folder is writable." >&2
  exit 1
fi
PYTHON=.venv/bin/python
if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
  printf '%s\n' "The local .venv cannot run Python 3.10+. Move it aside and run this launcher again." >&2
  exit 1
fi
if ! "$PYTHON" -c '
from importlib.metadata import version
from pathlib import Path
import textual, frida

for file in ("requirements-tui.txt", "requirements.txt"):
    package, pinned = Path(file).read_text().strip().split("==")
    if version(package) != pinned:
        raise SystemExit(1)
' >/dev/null 2>&1; then
  if ! "$PYTHON" -m pip install --disable-pip-version-check -r requirements-tui.txt -r requirements.txt; then
    printf '%s\n' "Could not install the pinned dependencies. Check PyPI access and that .venv is writable and has pip." >&2
    exit 1
  fi
fi
export PYTHONIOENCODING=utf-8:backslashreplace
export PYTHONUTF8=1
case "$MODE" in
  check) exec "$PYTHON" macos_runner.py --step 0 ;;
  list)  exec "$PYTHON" macos_runner.py --step 1 ;;
  tui)
    if [ "$#" -eq 0 ]; then exec "$PYTHON" tui.py; fi
    exec "$PYTHON" tui.py "$@" ;;
esac
exit 2
