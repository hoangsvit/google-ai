"""Read-only vphoned health probe; no app, account or billing operations."""
from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

TIMEOUT = 20
MAX_RESPONSE = 65536


def health_command(root: Path, cid: int) -> list[str]:
    if type(cid) is not int or not 3 <= cid <= 2147483647:
        raise ValueError("Specify a valid guest CID from the VM list")
    root = root.resolve(strict=True)
    script = root / "tools" / "vphoned.sh"
    if not script.is_file() or not script.resolve().is_relative_to(root):
        raise ValueError("vphoned.sh is missing from the reviewed checkout")
    return ["bash", str(script), "-c", str(cid), "GET", "/v1/health"]


def status(root: Path, cid: int) -> dict:
    args = health_command(root, cid)
    if platform.system() != "Linux" or not shutil.which("bash") or not shutil.which("socat"):
        raise ValueError("Run inside Linux/WSL2 with bash and socat")
    state = "unreachable"
    try:
        result = subprocess.run(args, cwd=root.resolve(), stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                timeout=TIMEOUT, check=False)
        if result.returncode == 0:
            if len(result.stdout) > MAX_RESPONSE:
                state = "invalid_response"
            else:
                try:
                    payload = json.loads(result.stdout)
                    state = ("daemon_responding" if isinstance(payload, dict)
                             and payload.get("status") == "ok" else "invalid_response")
                except (ValueError, RecursionError):
                    state = "invalid_response"
    except subprocess.TimeoutExpired:
        state = "timeout"
    return {"daemon": state, "vm_boot": "unverified",
            "ui_ready": "unverified", "network": "unverified",
            "google_app": "unverified", "google_account": "unverified",
            "storekit": "unverified", "live_discovery": "not_implemented",
            "checkout_supported": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vphone-dir", required=True, type=Path)
    parser.add_argument("--cid", required=True, type=int)
    args = parser.parse_args(argv)
    try:
        result = status(args.vphone_dir, args.cid)
    except (OSError, ValueError):
        print("Unable to run health probe. Check the reviewed vPhone checkout, CID, bash and socat.",
              file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result["daemon"] == "daemon_responding" else 1


if __name__ == "__main__":
    raise SystemExit(main())
