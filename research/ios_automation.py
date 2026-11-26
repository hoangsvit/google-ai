"""Offline iOS readiness and SKU-report research CLI; no checkout or interception."""
from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import sys
from pathlib import Path

MAX_BYTES = 1024 * 1024
MAX_ROWS = 300
SKU = re.compile(r"(?:g1\.|com\.google\.(?:one|gemini)\.)[A-Za-z0-9][A-Za-z0-9._-]{0,159}")


def readiness(vphone: Path | None = None) -> dict:
    """Inspect local prerequisites only; do not execute external programs."""
    system = platform.system()
    scripts = ("setup/setup.sh", "setup/create-vm.sh", "setup/start-vm.sh")
    present = bool(vphone and all((vphone / name).is_file() for name in scripts))
    return {
        "host": system,
        "architecture": platform.machine(),
        "git_available": shutil.which("git") is not None,
        "wsl_available": system == "Windows" and shutil.which("wsl.exe") is not None,
        "vphone_scripts_present": present,
        "vm_boot": "unverified",
        "network": "unverified",
        "google_app": "unverified",
        "google_account": "unverified",
        "storekit": "unverified",
        "live_discovery": "not_implemented",
        "checkout_supported": False,
    }


def normalize_report(document: object) -> dict:
    """Import only observed SKU identifiers from a user-authorized local report."""
    if not isinstance(document, dict) or document.get("schemaVersion") != 1:
        raise ValueError("Unsupported report schema")
    scan = document.get("scan")
    if not isinstance(scan, dict) or not isinstance(scan.get("skus"), list):
        raise ValueError("Missing scan SKU list")
    rows = scan["skus"]
    seen: set[str] = set()
    items = []
    for row in rows[:MAX_ROWS]:
        if not isinstance(row, dict):
            continue
        sku = row.get("id")
        if not isinstance(sku, str) or not SKU.fullmatch(sku) or sku.endswith(".") or sku in seen:
            continue
        seen.add(sku)
        items.append({"sku": sku, "platform": "ios", "source": "local_report",
                      "eligibility_verified": False, "subscription_active_verified": False})
    return {"status": "observed_identifiers" if items else "no_identifiers",
            "items": items, "truncated": len(rows) > MAX_ROWS,
            "eligibility_verified": False, "account_binding_verified": False,
            "subscription_active_verified": False, "checkout_supported": False}


def load_report(path: Path) -> dict:
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Report exceeds size limit")
    return normalize_report(json.loads(raw))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("diagnose", help="Check local prerequisites without changing settings")
    check.add_argument("--vphone-dir", type=Path)
    report = sub.add_parser("import-report", help="Normalize a local, authorized SKU report")
    report.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        result = readiness(args.vphone_dir) if args.command == "diagnose" else load_report(args.path)
    except (OSError, ValueError, RecursionError):
        print("iOS research: could not read or validate local input.", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
