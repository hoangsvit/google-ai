"""Windows-native ASoftware research adapter (no WSL, no live billing)."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

RELEASE = "v0.3.1"
RELEASE_URL = "https://github.com/alpersamur3/asoft-ios/releases/tag/" + RELEASE
GIB = 1024 ** 3


def memory_bytes() -> int | None:
    if platform.system() != "Windows":
        return None
    class MemoryStatus(ctypes.Structure):
        _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
            (name, ctypes.c_ulonglong) for name in (
                "total_phys", "avail_phys", "total_page", "avail_page",
                "total_virtual", "avail_virtual", "avail_extended")]
    data = MemoryStatus()
    data.length = ctypes.sizeof(data)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(data)):
        return None
    return data.total_phys


def prerequisites(root: Path) -> dict:
    root = root.resolve()
    existing = root
    while not existing.exists() and existing != existing.parent:
        existing = existing.parent
    free = shutil.disk_usage(existing).free
    memory = memory_bytes()
    cpu = os.cpu_count()
    return {
        "backend": "asoft_windows", "release_reference": RELEASE,
        "host": platform.system(), "windows_native": platform.system() == "Windows",
        "cpu_logical": cpu, "cpu_recommended_met": cpu >= 8 if cpu is not None else None,
        "ram_gib": round(memory / GIB, 1) if memory is not None else None,
        "ram_recommended_met": memory >= 16 * GIB if memory is not None else None,
        "free_disk_gib": round(free / GIB, 1),
        "disk_recommended_met": free >= 50 * GIB,
        "launcher_present": (root / "ASoftware.exe").is_file(),
        "vulkan_1_2_and_external_memory_host": "unverified_use_upstream_check",
        "vm_boot": "unverified", "network": "unverified", "app_install": "unverified",
        "google_app": "unverified", "google_account": "unverified",
        "apple_account": "upstream_reports_not_working",
        "app_store": "upstream_reports_not_working",
        "storekit": "unverified", "checkout_supported": False,
    }


def verify_archive(path: Path, expected: str) -> bool:
    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
        raise ValueError("Expected SHA256 must contain 64 hexadecimal digits")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest() == expected.lower()


def local_file(root: Path, relative: str) -> Path:
    root = root.resolve(strict=True)
    path = (root / relative).resolve(strict=True)
    if not path.is_file() or not path.is_relative_to(root):
        raise ValueError("Expected reviewed file within the selected folder")
    return path


def installer_command(package: Path, destination: Path, *, check: bool = False) -> list[str]:
    script = local_file(package, "installer/Setup-ASoftware.ps1")
    target = destination.resolve()
    if any(c in str(target) for c in (" ", "\n", "\r")):
        raise ValueError("Choose an iOS 26 installation folder without spaces")
    args = ["powershell.exe", "-NoProfile", "-File", str(script),
            "-Version", "ios26", "-Linux", "helper", "-IfNoWsl", "nowsl",
            "-Watch", "no", "-Vision", "no", "-Tv", "no", "-Dir", str(target)]
    if check:
        args.append("-Check")
    return args


def launch_command(root: Path) -> list[str]:
    return [str(local_file(root, "ASoftware.exe"))]


def execute_command(args: list[str], root: Path, *, execute: bool) -> int:
    if not execute:
        print("Plan only. Review the local upstream package before using --execute.")
        print(json.dumps(args))
        return 0
    if platform.system() != "Windows":
        raise ValueError("This adapter requires Windows")
    if not sys.stdin.isatty():
        raise ValueError("Run in an interactive terminal")
    # Never override execution policy, auto-accept prompts or terminate unrelated processes.
    completed = subprocess.run(args, cwd=root.resolve(), check=False)
    return completed.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("release")
    diagnose = sub.add_parser("diagnose")
    diagnose.add_argument("--install-dir", required=True, type=Path)
    verify = sub.add_parser("verify")
    verify.add_argument("archive", type=Path)
    verify.add_argument("--sha256", required=True)
    install = sub.add_parser("install")
    install.add_argument("--package-dir", required=True, type=Path)
    install.add_argument("--install-dir", required=True, type=Path)
    install.add_argument("--check", action="store_true")
    install.add_argument("--execute", action="store_true")
    launch = sub.add_parser("launch")
    launch.add_argument("--install-dir", required=True, type=Path)
    launch.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "release":
            print(RELEASE_URL)
        elif args.action == "diagnose":
            print(json.dumps(prerequisites(args.install_dir), indent=2))
        elif args.action == "verify":
            valid = verify_archive(args.archive, args.sha256)
            print("SHA256 matches" if valid else "SHA256 mismatch; do not run this archive")
            return 0 if valid else 1
        elif args.action == "install":
            return execute_command(installer_command(args.package_dir, args.install_dir,
                                                    check=args.check),
                                   args.package_dir, execute=args.execute)
        elif args.action == "launch":
            return execute_command(launch_command(args.install_dir), args.install_dir,
                                   execute=args.execute)
    except (OSError, ValueError, RuntimeError):
        print("ASoftware research: check paths, host requirements and local permissions.",
              file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted. Check the upstream installer or launcher before retrying.",
              file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
