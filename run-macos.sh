#!/bin/sh
# Native macOS launcher for ePlus AI Toolkit. Checkout requires TUI approval.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

usage() {
  printf '%s\n' \
    "ePlus AI Toolkit — macOS (Textual, Steps 0–5)" \
    "Usage: sh run-macos.sh [--check | --list | --step N [--sequence] | --sequence | --help]" \
    "  (no flags)    Textual dashboard, including optional confirmed checkout" \
    "  --check       Android/Frida setup diagnostics" \
    "  --list        Query offers (no checkout)" \
    "  --step N      Open the dashboard with Step 0..6 selected" \
    "  --sequence    Open dashboard with guided sequence controls" \
    "  --help        Display usage" \
    "Steps 2–5 can submit real charges after explicit TUI confirmations." \
    "Step 6 opens a separate Ultra 19.99 paid checkout for manual approval."
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
      0|1|2|3|4|5|6) : ;;
      *) usage >&2; exit 2 ;;
    esac
    if [ "$#" -eq 3 ] && [ "$3" != "--sequence" ]; then usage >&2; exit 2; fi
    MODE="tui" ;;
  *) usage >&2; exit 2 ;;
esac

if [ "$(uname -s)" != "Darwin" ]; then
  printf '%s\n' "This launcher requires macOS; on Windows use .\\run-all.ps1" >&2
  exit 2
fi
if ! command -v python3 >/dev/null 2>&1 ||
   ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
  printf '%s\n' "Install Python 3.10+ to run this toolkit." >&2
  exit 2
fi
if ! command -v adb >/dev/null 2>&1; then
  printf '%s\n' "Install Android SDK Platform-Tools and check 'adb devices'." >&2
  exit 2
fi
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
PYTHON=.venv/bin/python
if ! "$PYTHON" -c "import importlib.metadata as m; import textual, frida; assert m.version('frida') == '16.5.9'" >/dev/null 2>&1; then
  "$PYTHON" -m pip install --disable-pip-version-check -r requirements-tui.txt "frida==16.5.9"
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
