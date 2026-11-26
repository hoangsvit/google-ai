"""Opt-in local vPhone lifecycle wrapper for Linux and WSL2 research."""
from __future__ import annotations

import argparse
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

VM_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}")
ACTIONS = ("setup", "create", "list", "start", "stop")


def command(root: Path, action: str, *, vm: str | None = None) -> list[str]:
    """Build argv without invoking a shell or implicitly selecting a VM."""
    if action not in ACTIONS:
        raise ValueError("Unknown action")
    if action in ("start", "stop") and (not vm or not VM_NAME.fullmatch(vm)):
        raise ValueError("Start and stop require an explicit simple VM name")
    if action not in ("start", "stop") and vm is not None:
        raise ValueError("VM name is only accepted for start or stop")
    root = root.resolve(strict=True)
    script = root / "setup" / (
        "setup.sh" if action == "setup" else
        "create-vm.sh" if action == "create" else "start-vm.sh"
    )
    if not script.is_file() or not script.resolve().is_relative_to(root):
        raise ValueError("Expected vphone-linux script not found inside checkout")
    args = ["bash", str(script)]
    if action == "list":
        args.append("--list")
    elif action == "start":
        # No automatic screen unlock or account actions.
        args.extend(("--no-unlock", vm))
    elif action == "stop":
        args.extend(("--stop", vm))
    return args


def run(root: Path, action: str, *, vm: str | None = None,
        execute: bool = False) -> int:
    args = command(root, action, vm=vm)
    if not execute and action != "list":
        print("Plan only; rerun with --execute after reviewing the upstream script.")
        print(repr(args))
        return 0
    if platform.system() != "Linux":
        raise ValueError("Run inside Linux or WSL2, not native Windows/macOS")
    if not shutil.which("bash"):
        raise ValueError("Bash is required")
    if action in ("setup", "create") and not sys.stdin.isatty():
        raise ValueError("Setup and creation require an interactive terminal")
    if action in ("setup", "create"):
        print("Upstream setup may download software, use sudo and change this host.")
        print("Review licensing and prompts. The toolkit does not auto-approve them.")
    elif action == "stop":
        print("Upstream shutdown may interrupt guest work. Save your work first.")
    # The chosen upstream checkout is explicitly supplied and trusted by the user.
    # Inherit the terminal for upstream prompts; do not collect or persist its logs.
    result = subprocess.run(args, cwd=root.resolve(), check=False)
    if result.returncode == 0 and action == "start":
        print("Start command returned; iOS boot, UI, network and StoreKit are still unverified.")
    return result.returncode if result.returncode >= 0 else 128 - result.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vphone-dir", required=True, type=Path)
    parser.add_argument("action", choices=ACTIONS)
    parser.add_argument("--vm", help="Explicit name from the upstream VM list")
    parser.add_argument("--execute", action="store_true", help="Opt in to a state-changing operation")
    args = parser.parse_args(argv)
    try:
        return run(args.vphone_dir, args.action, vm=args.vm, execute=args.execute)
    except (OSError, ValueError) as exc:
        print(f"vPhone research: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted; check the VM list before retrying.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
