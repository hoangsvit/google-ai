#!/usr/bin/env python3
"""macOS bridge for safe Android environment and offer diagnostics.

Only steps 0/1 are supported. Never call the checkout path from this bridge.
The original ultra0.py owns Frida, account inspection and offer listing.
"""
from __future__ import annotations

import argparse
from importlib import metadata
from pathlib import Path
import os
import shutil
import subprocess
import sys

from device_selector import auto_select_device, online_serials

ROOT = Path(__file__).resolve().parent
FRIDA_VERSION = "16.5.9"


def readonly_command(step: int, serial: str, python: str = sys.executable) -> list[str]:
    if step not in (0, 1):
        raise ValueError("macOS currently supports read-only Steps 0 and 1 only")
    base = [python, str(ROOT / "ultra0.py")]
    if step == 0:
        return base + ["--check", "--serial", serial]
    return base + ["--list", "--no-add", "--no-switch",
                   "--account", "current@device", "--serial", serial]


def preflight() -> str:
    adb = os.environ.get("ADB_PATH") or shutil.which("adb")
    if not adb:
        raise RuntimeError(
            "ADB not installed. Install Android SDK Platform-Tools (for example "
            "'brew install android-platform-tools') and restart Terminal."
        )
    try:
        version = metadata.version("frida")
    except metadata.PackageNotFoundError:
        version = None
    if version != FRIDA_VERSION:
        raise RuntimeError(
            f"Frida {FRIDA_VERSION} is required (installed: {version or 'none'}). "
            f"Run: {sys.executable} -m pip install frida=={FRIDA_VERSION}"
        )
    devices = online_serials(adb)
    if not devices:
        raise RuntimeError(
            "No online Android device. Start a rooted Android emulator or connect "
            "a device via ADB. Check: adb devices"
        )
    serial = auto_select_device(adb, serials=devices)
    if not serial:
        raise RuntimeError(
            "Multiple distinct Android devices detected. Disconnect extras "
            "to avoid selecting the wrong account."
        )
    print(f"Device  {serial}", flush=True)
    return serial


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ePlus AI Toolkit macOS read-only bridge")
    parser.add_argument("--step", type=int, required=True, choices=(0, 1))
    args = parser.parse_args(argv)
    try:
        serial = preflight()
        command = readonly_command(args.step, serial)
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8:backslashreplace"
        env["PYTHONUTF8"] = "1"
        env["ADB_PATH"] = os.environ.get("ADB_PATH") or shutil.which("adb") or "adb"
        print("Checking Android environment..." if args.step == 0
              else "Checking Google Play offers (read-only)...", flush=True)
        return subprocess.call(command, cwd=ROOT, env=env)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
