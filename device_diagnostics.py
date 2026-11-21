"""Non-purchasing connection diagnostics for Windows and macOS.

This module does not install tools, change emulator settings, start Frida,
load Google One, or launch Google Play Billing. Calling 'adb devices' can
start the *local* ADB server, so this is not a zero-side-effect probe.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


FRIDA_REQUIRED = "16.5.9"
GOOGLE_ONE = "com.google.android.apps.subscriptions.red"
GOOGLE_PLAY = "com.android.vending"
SAFE_TEXT = re.compile(r"^[a-zA-Z0-9._:/-]{1,90}$")


@dataclass(frozen=True)
class ConnectionDiagnosis:
    status: str
    headline: str
    details: tuple[str, ...]
    guidance: str


def _clean(value: str, fallback: str = "unknown") -> str:
    text = value.strip()
    return text if SAFE_TEXT.fullmatch(text) else fallback


def locate_adb(platform_name: str | None = None) -> str | None:
    """Find an already-installed ADB binary; never download anything."""
    platform_name = platform_name or sys.platform
    configured = os.environ.get("ADB_PATH")
    if configured and Path(configured).is_file():
        return configured
    found = shutil.which("adb")
    if found:
        return found
    home = Path.home()
    if platform_name == "win32":
        paths = [
            Path(__file__).resolve().parent / "platform-tools/adb.exe",
            Path(os.environ.get("LOCALAPPDATA") or home / ".cache") / "google-ai/platform-tools/adb.exe",
            home / "AppData/Local/Android/Sdk/platform-tools/adb.exe",
            Path(os.environ.get("LOCALAPPDATA") or home) / "Android/Sdk/platform-tools/adb.exe",
            Path("C:/Program Files/Netease/MuMuPlayer-12.0/shell/adb.exe"),
            Path("C:/Program Files/Netease/MuMuPlayerGlobal-12.0/shell/adb.exe"),
            Path("C:/Program Files (x86)/Netease/MuMuPlayer-12.0/shell/adb.exe"),
            Path("D:/Program Files/Netease/MuMu/nx_main/adb.exe"),
            Path("D:/Program Files/Netease/MuMu/nx_device/12.0/shell/adb.exe"),
            Path("C:/Program Files/Netease/MuMu/nx_main/adb.exe"),
            Path(os.environ.get("PROGRAMFILES") or "C:/Program Files")
            / "Netease/MuMu Player 12/shell/adb.exe",
        ]
    else:
        paths = [
            Path("/opt/homebrew/bin/adb"),
            Path("/usr/local/bin/adb"),
            home / "Library/Android/sdk/platform-tools/adb",
            home / "Android/Sdk/platform-tools/adb",
        ]
    return next((str(path) for path in paths if path.is_file()), None)


def _run(adb: str, args: list[str]):
    try:
        return subprocess.run(
            [adb, *args], capture_output=True, text=True, errors="replace",
            timeout=8, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def inspect_connection(platform_name: str | None = None) -> ConnectionDiagnosis:
    """Inspect host/Android prerequisites without touching billing or account data."""
    platform_name = platform_name or sys.platform
    mac = platform_name == "darwin"
    details = [f"Host: {'macOS Terminal' if mac else 'Windows / PowerShell' if platform_name == 'win32' else 'POSIX shell'}"]
    try:
        frida = metadata.version("frida")
    except metadata.PackageNotFoundError:
        frida = ""
    details.append(
        f"Frida host: {frida or 'not installed'} "
        f"(toolkit expects {FRIDA_REQUIRED}; no installation attempted)"
    )
    install = ("Install ADB with: brew install android-platform-tools"
               if mac else "Install Android SDK Platform-Tools or enable MuMu ADB")
    adb = locate_adb(platform_name)
    if not adb:
        return ConnectionDiagnosis(
            "missing_adb", "ADB not found", tuple(details),
            f"{install}. Then open the rooted Android emulator/device and retry.",
        )
    details.append(f"ADB: {_clean(adb, 'installed (path hidden)')}")
    response = _run(adb, ["devices"])
    if response is None or response.returncode != 0:
        return ConnectionDiagnosis(
            "adb_error", "ADB did not respond", tuple(details),
            "Check the Android SDK installation and ADB permissions. No checkout was started.",
        )
    devices = []
    for line in response.stdout.splitlines()[1:]:
        fields = line.split()
        if len(fields) >= 2 and SAFE_TEXT.fullmatch(fields[0]):
            devices.append((fields[0], fields[1]))
    online = [serial for serial, state in devices if state == "device"]
    if not online:
        states = ", ".join(sorted({state for _, state in devices})) or "none"
        details.append(f"Android devices: {len(devices)} (states: {_clean(states, 'see adb devices')})")
        if any(state == "unauthorized" for _, state in devices):
            fix = "Unlock Android and approve its USB debugging authorization prompt."
        elif any(state == "offline" for _, state in devices):
            fix = "Restart the Android instance and verify that ADB reports 'device', not 'offline'."
        else:
            fix = "Start MuMu or connect a rooted Android phone, enable USB debugging, then run adb devices."
        return ConnectionDiagnosis("no_online_device", "No authorized Android device", tuple(details), fix)
    if len(online) != 1:
        details.append(f"Online Android transports: {len(online)}")
        return ConnectionDiagnosis(
            "ambiguous", "Multiple Android transports", tuple(details),
            "Choose one explicit ADB serial in the toolkit. This diagnostic never guesses which account/device to use.",
        )
    serial = online[0]
    details.append(f"Android serial: {_clean(serial)}")
    abi = _run(adb, ["-s", serial, "shell", "getprop", "ro.product.cpu.abi"])
    if abi is not None and abi.returncode == 0:
        details.append(f"Android ABI: {_clean(abi.stdout)}")
    play = _run(adb, ["-s", serial, "shell", "pm", "path", GOOGLE_PLAY])
    play_installed = play is not None and play.returncode == 0 and "package:" in play.stdout
    details.append("Google Play Store: installed" if play_installed else "Google Play Store: not detected")
    app = _run(adb, ["-s", serial, "shell", "pm", "path", GOOGLE_ONE])
    installed = app is not None and app.returncode == 0 and "package:" in app.stdout
    details.append("Google One: installed" if installed else "Google One: not detected")
    root = _run(adb, ["-s", serial, "shell", "id"])
    if root is not None and root.returncode == 0:
        details.append(
            "ADB shell: root" if "uid=0(" in root.stdout
            else "ADB shell: non-root (root may be available through su)"
        )
    if not play_installed:
        return ConnectionDiagnosis(
            "missing_google_play", "Google Play Store not detected", tuple(details),
            "Enable Google Play Store or use an emulator image that includes Google Play. Billing was not checked.",
        )
    if not installed:
        return ConnectionDiagnosis(
            "missing_google_one", "Android connection found", tuple(details),
            "Install Google One from a trusted source on the selected Android device. Billing was not checked.",
        )
    if frida != FRIDA_REQUIRED:
        return ConnectionDiagnosis(
            "frida_mismatch", "Android connection found", tuple(details),
            "The toolkit uses Frida 16.5.9. Use the platform's existing setup workflow to verify compatibility; no changes were made.",
        )
    return ConnectionDiagnosis(
        "connected", "Basic Android connection found", tuple(details),
        "Root, Android-side Frida, account, offer eligibility and billing remain unverified. Use Step 1 to inspect offers.",
    )
