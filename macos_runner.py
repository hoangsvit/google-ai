#!/usr/bin/env python3
"""Native macOS and Linux stage adapter; reuse ultra0.py without Windows setup.

Steps 2–5 can request real Google Play charges. The adapter checks the
selected device, current Play account, offer ID and today's introductory
price before invoking the unchanged upstream billing flow. It never uses
--force or account switching. A checkout request is not activation proof.
"""
from __future__ import annotations

import argparse
import base64
from importlib import metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import time

from device_diagnostics import inspect_connection, linux_frida_compatibility_issue, locate_adb
from device_selector import auto_select_device, online_serials
from tui_core import MESSAGES, offer_explorer_lines, read_fresh_report

ROOT = Path(__file__).resolve().parent
FRIDA_REQUIRED = "16.5.9"
REPORT_DIR = ROOT / "ultra0-report"
LINUX_WORKDIR = "EPLUS_LINUX_STAGE_WORKDIR"
CHECKOUT_PRODUCT = "g1.2tb.ai.subs_variant"
EMAIL = re.compile(r"^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$")
STAGES = {
    2: ("pro12", "12months-eft", False),
    3: ("pro6", "6months-eft", True),
    4: ("pro6b", "6months-eft-2", True),
    5: ("pro6c", "6months-eft-ss-2026", True),
}


def stage_command(step: int, serial: str, account: str = "",
                  python: str = sys.executable) -> list[str]:
    if type(step) is not int or step not in range(6):
        raise ValueError("Step must be an integer between 0 and 5")
    if not serial or serial.startswith("-"):
        raise ValueError("Selected Android device must have an explicit ADB serial")
    base = [python, str(ROOT / "ultra0.py")]
    if step == 0:
        return base + ["--check", "--serial", serial]
    if step == 1:
        return base + ["--list", "--no-add", "--no-switch", "--plan", "pro12",
                       "--account", "current@device", "--serial", serial]
    if not EMAIL.fullmatch(account):
        raise ValueError("A verified Google Play email is required before checkout")
    plan, _offer, stack = STAGES[step]
    result = base + ["--account", account, "--no-add", "--no-switch",
                     "--plan", plan, "--serial", serial]
    if stack:
        result.append("--stack")
    return result


def preflight(expected_serial: str = "") -> tuple[str, str]:
    linux = sys.platform == "linux"
    adb = locate_adb("linux") if linux else os.environ.get("ADB_PATH") or shutil.which("adb")
    if not adb:
        raise RuntimeError(
            "ADB is missing. Install Android SDK Platform-Tools and add adb to PATH or set ADB_PATH."
        )
    if linux:
        # The engine runs from a private directory for each Linux invocation.
        adb = os.path.abspath(adb)
    try:
        installed = metadata.version("frida")
    except metadata.PackageNotFoundError:
        installed = None
    if installed != FRIDA_REQUIRED:
        launcher = "run-linux.sh" if linux else "run-macos.sh"
        raise RuntimeError(
            f"Frida {FRIDA_REQUIRED} required (found {installed or 'none'}). "
            f"Use {launcher} to prepare the local virtual environment."
        )
    devices = online_serials(adb)
    if not devices:
        if linux:
            raise RuntimeError(inspect_connection("linux").guidance)
        raise RuntimeError("No online Android device. Check adb devices.")
    if expected_serial and expected_serial not in devices:
        raise RuntimeError("Android device changed since Step 1; no checkout started")
    if linux:
        # Never guess which of multiple authorized transports is intended.
        serials = set(devices)
        serial = next(iter(serials)) if len(serials) == 1 else None
    else:
        serial = expected_serial or auto_select_device(adb, serials=devices)
    if not serial:
        raise RuntimeError("Multiple different Android devices detected. Disconnect extras.")
    if expected_serial and serial != expected_serial:
        raise RuntimeError("Android device changed since Step 1; no checkout started")
    if linux and (issue := linux_frida_compatibility_issue(adb, serial)):
        raise RuntimeError(issue)
    return adb, serial


def show_android_details(adb: str, serial: str) -> None:
    try:
        result = subprocess.run(
            [adb, "-s", serial, "shell",
             "getprop ro.build.version.release; getprop ro.build.version.sdk; getprop ro.product.cpu.abi"],
            capture_output=True, text=True, errors="replace", timeout=5, check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return
    properties = [line.strip() for line in result.stdout.splitlines()]
    if len(properties) == 3 and all(properties):
        release, sdk, abi = properties
        print(f"Android {release} (SDK {sdk}), ABI {abi}", flush=True)


def run_engine(command: list[str], env: dict[str, str]) -> int:
    workdir = env.get(LINUX_WORKDIR)
    if workdir is None:
        return subprocess.call(command, cwd=ROOT, env=env)
    # Engine messages can contain tokens and device/account identifiers. Emit
    # only fixed progress and error messages, while letting stdin reach it.
    notices = (
        ("connected adb device:", "Android device connected."),
        ("root is unavailable", "Root is unavailable. Check root authorization on Android."),
        ("environment preflight passed", "Android environment preflight passed."),
        ("downloading official matching frida", "Downloading the matching Android Frida server."),
        ("frida-server 16.5.9 started", "Android Frida server started."),
        ("could not start", "An Android service could not start. Check device root and compatibility."),
        ("calledprocesserror", "An Android command failed. Check USB connection and device permissions."),
        ("action required:", "Action required: Complete the prompt on Android, then confirm here."),
        ("google play store process is running", "Google Play Store is running."),
        ("offer_query_failed", "Google Play offer query failed. Open Google One and Google Play, then retry."),
    )
    with subprocess.Popen(command, cwd=workdir, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, encoding="utf-8", errors="replace") as child:
        assert child.stdout is not None
        for line in child.stdout:
            for marker, message in notices:
                if marker in line.lower():
                    print(message, flush=True)
                    break
        code = child.wait()
    if code:
        print("Android stage failed. Check the USB connection, root access and Android Frida compatibility.",
              flush=True)
    return code


def read_play_account(serial: str, env: dict[str, str]) -> str:
    """Resolve the Google Play profile without importing Windows setup code."""
    command = [sys.executable, str(ROOT / "scripts/runtime-lookup.py"),
               "play-account", "--serial", serial]
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                            text=True, errors="replace", timeout=60)
    if result.returncode:
        raise RuntimeError("Google Play account lookup failed; no checkout started")
    lines = [line.removeprefix("RUNTIME_RESULT:") for line in result.stdout.splitlines()
             if line.startswith("RUNTIME_RESULT:")]
    if len(lines) != 1:
        raise RuntimeError("Google Play account lookup returned an ambiguous result")
    try:
        account = base64.b64decode(lines[0], validate=True).decode("utf-8").strip().lower()
    except (ValueError, UnicodeError) as error:
        raise RuntimeError("Google Play account lookup returned invalid text") from error
    return account if EMAIL.fullmatch(account) else ""


def fresh_report(filename: str, since_ns: int, directory: Path | None = None) -> dict:
    path = (REPORT_DIR if directory is None else directory) / filename
    try:
        if path.stat().st_mtime_ns < since_ns:
            raise RuntimeError("The result belongs to an older invocation")
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise RuntimeError("A new matching report was not produced") from error
    if not isinstance(obj, dict) or not isinstance(obj.get("status"), str):
        raise RuntimeError("The result report has an invalid format")
    return obj


def list_offers(serial: str, env: dict[str, str], plan: str = "pro12") -> dict:
    command = stage_command(1, serial)
    if plan != "pro12":
        command[command.index("--plan") + 1] = plan
    directory = engine_report_dir(env)
    linux = LINUX_WORKDIR in env
    # A private, initially empty path proves freshness without relying on a
    # filesystem timestamp that may lag the process clock.
    if linux and (directory / "current.json").exists():
        raise RuntimeError("The result belongs to an older invocation")
    start_ns = 0 if linux else time.time_ns()
    if run_engine(command, env):
        raise RuntimeError("Google Play offer listing failed; checkout not started")
    report = fresh_report("current.json", start_ns, directory)
    if report["status"] in ("app_not_started", "play_store_not_started"):
        raise RuntimeError(f"Offer listing could not start: {report['status']}")
    if report["status"] != "listed" or not isinstance(report.get("offers"), list):
        raise RuntimeError("No successful offer listing; checkout not started")
    return report


def verified_account(serial: str, env: dict[str, str], report: dict,
                     *, require_lookup: bool = False) -> str:
    current = read_play_account(serial, env)
    listed = str(report.get("detected_play_account") or "").strip().lower()
    if listed and not EMAIL.fullmatch(listed):
        raise RuntimeError("Invalid Google Play account reported during offer listing")
    if current and listed and current != listed:
        raise RuntimeError("Google Play account changed during checks; stop before checkout")
    account = current if require_lookup else listed or current
    if not account or not EMAIL.fullmatch(account) or (require_lookup and not listed):
        raise RuntimeError("Could not verify Google Play account; no checkout started")
    return account


def check_offer(report: dict, step: int) -> None:
    _plan, expected, _stack = STAGES[step]
    matches = [offer for offer in report["offers"] if isinstance(offer, dict) and
               offer.get("product") == CHECKOUT_PRODUCT and offer.get("id") == expected and
               str(offer.get("micros")) == "0"]
    if not matches:
        raise RuntimeError(
            f"Step {step} offer {expected} on {CHECKOUT_PRODUCT} has no verified zero-priced first phase. "
            "No checkout started."
        )


def engine_report_dir(env: dict[str, str]) -> Path:
    workdir = env.get(LINUX_WORKDIR)
    return Path(workdir) / "ultra0-report" if workdir else REPORT_DIR


def publish_result(path: Path, report: dict) -> None:
    """Send only dashboard fields from a verified invocation."""
    status = report["status"]
    result = {"status": status if status in MESSAGES else "unverified"}
    if status == "listed":
        result["offers"] = [
            {field: offer.get(field) for field in ("product", "id", "period", "micros")}
            for offer in report["offers"] if isinstance(offer, dict)
        ]
    sheet = report.get("sheet")
    if isinstance(sheet, dict) and isinstance(reason := sheet.get("reason"), str):
        if reason == "zero_today_and_duration_verified" and sheet.get("confirmed") is True:
            # The current TUI requires both fields before offering the next
            # separately approved stage. Never publish tokens, emails or prices.
            result["sheet"] = {"reason": reason, "confirmed": True}
        elif reason in MESSAGES:
            result["sheet"] = {"reason": reason}
    with path.open("x", encoding="utf-8") as output:
        json.dump(result, output)


def run_stage(step: int, serial: str, env: dict[str, str],
              confirmed: bool = False, active_confirmed: bool = False,
              result_file: Path | None = None,
              expected_account: str = "", expected_device: str = "") -> int:
    linux = LINUX_WORKDIR in env
    if step >= 2 and expected_device and serial != expected_device:
        raise RuntimeError("Android device changed since Step 1; no checkout started")
    if step == 0:
        return run_engine(stage_command(0, serial), env)
    if step == 1:
        report = list_offers(serial, env)
        if linux and expected_account:
            listed = str(report.get("detected_play_account") or "").strip().lower()
            if listed != expected_account.lower():
                raise RuntimeError("Selected Google Play account does not match the listed account; no checkout started")
        if linux:
            # Offer inspection can complete when the current Play profile
            # could not be read. Checkout performs its own mandatory lookup.
            listed = str(report.get("detected_play_account") or "").strip().lower()
            if EMAIL.fullmatch(listed):
                print("Google Play account verified.", flush=True)
            else:
                print("Google Play account could not be verified.", flush=True)
        else:
            account = verified_account(serial, env, report)
            print(f"Account {account}", flush=True)
        print(f"Offers {len(report['offers'])} (eligibility not guaranteed)", flush=True)
        if result_file is not None:
            publish_result(result_file, report)
        elif linux:
            for line in offer_explorer_lines(report):
                print(line, flush=True)
        return 0
    if not confirmed or (step >= 3 and not active_confirmed):
        raise RuntimeError("Explicit checkout and existing-plan confirmations required")
    print("Checking Android environment before paid stage...", flush=True)
    if run_engine(stage_command(0, serial), env):
        raise RuntimeError("Android environment checks failed; no checkout started")
    if not linux:
        print("EPLUS_STAGE_DONE:0", flush=True)
    plan, _offer, _stack = STAGES[step]
    report = list_offers(serial, env, plan)
    account = verified_account(serial, env, report, require_lookup=linux)
    if expected_account and account != expected_account.lower():
        raise RuntimeError("Selected Google Play account does not match the current account; no checkout started")
    check_offer(report, step)
    # Verify the account once again immediately before entering checkout.
    if read_play_account(serial, env) != account:
        raise RuntimeError("Google Play account changed; no checkout started")
    print("Google Play account verified." if linux else f"Account {account}", flush=True)
    print(f"Step {step} offer inspected; first phase zero-priced.", flush=True)
    print("CAUTION: Checkout may incur charges. Verify all terms in Google Play.", flush=True)
    directory = engine_report_dir(env)
    if linux and any(path.name != "current.json" for path in directory.glob("*.json")):
        raise RuntimeError("An earlier checkout report is present. No checkout started.")
    code = run_engine(stage_command(step, serial, account), env)
    if linux and code == 0:
        report = read_fresh_report(directory, step, 0, expected_account=account)
        if report is None:
            raise RuntimeError("No fresh result for the verified account. Review Google Play before retrying.")
        if result_file is not None:
            publish_result(result_file, report)
        else:
            print(MESSAGES.get(report["status"], ("Review Google Play for the result.", ""))[0], flush=True)
    return code


def main(argv: list[str] | None = None) -> int:
    linux = sys.platform == "linux"
    parser = argparse.ArgumentParser(description="ePlus AI Toolkit native stage adapter")
    parser.add_argument("--step", type=int, required=True, choices=range(6))
    parser.add_argument("--confirmed", action="store_true",
                        help="Explicitly authorize the selected checkout stage")
    parser.add_argument("--active-confirmed", action="store_true",
                        help="Confirm existing active plan for Steps 3–5")
    parser.add_argument("--result-file", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--expected-account", default="",
                        help="Expected Google Play account selected in the toolkit")
    parser.add_argument("--expected-device", default="",
                        help="ADB serial verified by the Step 1 offer check")
    args = parser.parse_args(argv)
    if args.result_file is not None and not linux:
        parser.error("--result-file is reserved for the Linux dashboard")
    if args.step >= 2 and not args.confirmed:
        parser.error("Steps 2–5 require explicit --confirmed; may initiate real charges")
    if args.step >= 3 and not args.active_confirmed:
        parser.error("Steps 3–5 also require --active-confirmed")
    if args.expected_account and not EMAIL.fullmatch(args.expected_account.lower()):
        parser.error("Expected Google Play account is invalid")
    try:
        adb, serial = preflight(args.expected_device if args.step >= 2 else "")
        env = os.environ.copy()
        env["ADB_PATH"] = adb
        env["PYTHONIOENCODING"] = "utf-8:backslashreplace"
        env["PYTHONUTF8"] = "1"
        env.pop(LINUX_WORKDIR, None)
        if linux:
            parent = args.result_file.parent if args.result_file else None
            with TemporaryDirectory(prefix="eplus-android-", dir=parent) as workdir:
                env[LINUX_WORKDIR] = workdir
                # The engine also uses fixed names for downloaded setup
                # files. Keep those files isolated with this invocation.
                env["TMPDIR"] = workdir
                return run_stage(args.step, serial, env, args.confirmed, args.active_confirmed,
                                 args.result_file, args.expected_account, args.expected_device)
        print(f"Device {serial}", flush=True)
        show_android_details(adb, serial)
        return run_stage(args.step, serial, env, args.confirmed, args.active_confirmed,
                         None, args.expected_account, args.expected_device)
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        if linux:
            if isinstance(error, RuntimeError):
                print(f"Stage stopped: {error}", file=sys.stderr, flush=True)
            else:
                print("Stage stopped: A local command or report failed. Check ADB and review Google Play if checkout began.",
                      file=sys.stderr, flush=True)
        else:
            from tui_core import runtime_error_outcome
            issue = runtime_error_outcome(str(error), args.step)
            if os.environ.get("EPLUS_TUI") == "1":
                print(f"EPLUS_ISSUE:{issue.code}", flush=True)
            print(f"{issue.title}. Next: {issue.instruction}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
