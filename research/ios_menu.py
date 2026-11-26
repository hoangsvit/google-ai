"""Separate interactive research console; the Android dashboard is unchanged."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from research.ios_automation import load_report, readiness
from research.ios_status import status
from research.ios_vphone import run

MENU = """
ePlus AI Toolkit — iOS Research
  1. Check host prerequisites
  2. Install/build vPhone environment
  3. Create virtual iPhone
  4. List virtual iPhones
  5. Start virtual iPhone
  6. Check vphoned health
  7. Import local SKU report
  8. Stop virtual iPhone
  0. Exit
Experimental: no live offer discovery, checkout or eligibility verification.
"""


def show(value: dict) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=True))


def choose(root: Path, choice: str) -> bool:
    if choice == "0":
        return False
    if choice == "1":
        show(readiness(root))
    elif choice in ("2", "3", "5", "8"):
        action = {"2": "setup", "3": "create", "5": "start", "8": "stop"}[choice]
        vm = input("VM name from list: ").strip() if action in ("start", "stop") else None
        run(root, action, vm=vm)
        if input("Execute this upstream action? [y/N] ").strip().lower() == "y":
            print("Exit code:", run(root, action, vm=vm, execute=True))
        else:
            print("Canceled.")
    elif choice == "4":
        print("Exit code:", run(root, "list"))
    elif choice == "6":
        cid = int(input("Guest CID from list: ").strip())
        show(status(root, cid))
    elif choice == "7":
        path = Path(input("Authorized local JSON report path: ").strip()).expanduser()
        show(load_report(path))
    else:
        print("Select a listed number.")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vphone-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    if not sys.stdin.isatty():
        print("Use an interactive terminal.", file=sys.stderr)
        return 1
    while True:
        try:
            print(MENU)
            if not choose(args.vphone_dir, input("Select: ").strip()):
                return 0
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Check the VM list before retrying an interrupted operation.")
            return 130
        except (OSError, ValueError, RecursionError):
            print("Action failed. Check your local paths, report format and upstream setup.",
                  file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
