"""Pure state and subprocess helpers for the Textual frontend.

No checkout is initiated by this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import importlib.metadata
import json
import re
import shutil
import sys
import time


@dataclass(frozen=True)
class Stage:
    number: int
    label: str
    offer: str


FRIDA_VERSION = "16.5.9"


def needs_setup() -> bool:
    """Only install Android Python tooling when the required Frida build is absent."""
    try:
        return importlib.metadata.version("frida") != FRIDA_VERSION
    except importlib.metadata.PackageNotFoundError:
        return True


STAGES = (
    Stage(0, "Environment", ""),
    Stage(1, "Available offers", ""),
    Stage(2, "Pro 12 months", "12months-eft"),
    Stage(3, "Pro +6 months", "6months-eft"),
    Stage(4, "Pro +6 months (second)", "6months-eft-2"),
    Stage(5, "Optional +6 months", "6months-eft-ss-2026"),
)


@dataclass(frozen=True)
class Outcome:
    code: str
    title: str
    instruction: str
    can_review: bool = False


MESSAGES = {
    "checkout_account_mismatch": (
        "Checkout is using a different account",
        "Review the account shown in Google Play checkout. Close checkout, select the intended account in Play Store and Google One, then run Check Device & Offers again. Verify any earlier purchase in Google Play.",
    ),
    "checkout_account_unverified": (
        "Checkout account could not be read",
        "Expand the account details in Google Play checkout and verify the email matches the account selected in the toolkit. Close checkout and run Check Device & Offers again before another attempt.",
    ),
    "listed": ("Offers loaded", "Offer metadata is not proof of eligibility."),
    "checkout_requested": (
        "Checkout submitted - not yet verified",
        "Check Google Play Subscriptions, renewal date and charges before proceeding.",
    ),
    "checkout_security_blocked": (
        "Google Play requires account verification",
        "Review Google Account Security and Google Payments alerts (OR-REH-04). Stop retrying.",
    ),
    "already_subscribed": (
        "This plan is already subscribed",
        "No extra months are verified. Check the renewal date; do not repeat checkout.",
    ),
    "payment_security_blocked": (
        "Google Play requires account verification",
        "Review Google Account Security and Google Payments alerts (OR-REH-04). Stop retrying.",
    ),
    "today_price_unverified": (
        "Today's checkout amount is unclear",
        "Check the amount payable today on the Android screen before trying again.",
    ),
    "trial_duration_unverified": (
        "Trial duration could not be verified",
        "Check the duration and future pricing shown by Google Play.",
    ),
    "ineligible": (
        "This account is not eligible",
        "Review Google Play's offer terms. Force mode cannot change eligibility.",
    ),
    "purchase_unavailable": (
        "Google Play says this item is unavailable",
        "Check the account, Play country and Google One availability. No purchase was confirmed.",
    ),
    "backup_payment_methods_prompt": (
        "Google Play asked about backup payments",
        "Review that optional setting in Google Play; it does not confirm a subscription.",
    ),
    "processing": (
        "Google Play is processing a transaction",
        "Check payment history before another attempt.",
    ),
    "checkout_not_confirmed": (
        "Checkout was not confirmed",
        "Check the Google Play subscription status before retrying.",
    ),
    "offer_query_failed": (
        "Could not load offers",
        "Open Google One and Google Play, then retry the read-only offer check.",
    ),
    "offer_not_available": (
        "Offer not available",
        "Use Step 1 to review current offers. Do not assume eligibility.",
    ),
    "launch_failed": (
        "Could not open Google Play checkout",
        "The app did not confirm that the checkout screen opened. Check Google One and "
        "Google Play on Android, then review your subscription and payment history before retrying.",
    ),
    "billing_flow_error": (
        "Google Play could not open checkout",
        "Google Play returned a checkout error. Check the Android screen and payment history "
        "before trying this step again.",
    ),
    "billing_launch_error": (
        "Could not start Google Play checkout",
        "The tool encountered a problem while opening checkout. Review Google One, the "
        "Android screen and technical details. Check Google Play payments before retrying.",
    ),
    "activity_lookup_failed": (
        "Could not access the Google One screen",
        "Reopen Google One on Android and check the ADB/Frida connection in technical details. "
        "Check Google Play subscriptions before another payment attempt.",
    ),
    "no_activity": (
        "Google One is not ready",
        "Bring Google One to the foreground and try the device check again. If you already "
        "attempted checkout, first verify its outcome in Google Play.",
    ),
    "app_not_started": (
        "Google One could not be opened",
        "Restart the Android device or emulator and wait for it to boot. Then run Check Device & Offers again from Step 1.",
    ),
    "play_store_not_started": (
        "Google Play Store could not be opened",
        "Restart the Android device or emulator and wait for it to boot. Then run Check Device & Offers again from Step 1.",
    ),
    "subscription_update_unavailable": (
        "Could not prepare the subscription change",
        "The app could not find the required existing-subscription information. Check the "
        "current subscription in Google Play; do not repeat a paid step blindly.",
    ),
    "subscribe_button_not_found": (
        "Could not find the checkout confirmation button",
        "Check the current Google Play screen and pricing. No subscription change was verified.",
    ),
    "checkout_not_visible": (
        "Could not see the Google Play checkout screen",
        "Open Google Play on Android and review subscriptions and charges before retrying.",
    ),
    "price_unverified": (
        "Could not verify the checkout price",
        "Review the amount due today and renewal pricing in Google Play before proceeding.",
    ),
    "add_account_failed": (
        "Could not add the Google account",
        "Open Android Settings and Google Play to check sign-in. Verify the intended account before continuing.",
    ),
    "add_account_error": (
        "Google account setup was interrupted",
        "Check Android account settings and your sign-in prompts. Do not continue until the account is verified.",
    ),
    "payment_method_not_confirmed": (
        "Could not verify the payment method",
        "Check Google Play payment methods manually. No successful payment or subscription change was verified.",
    ),
    "play_account_switch_failed": (
        "Could not switch Google Play accounts",
        "Select the intended account in Play Store manually, then perform the offer check again.",
    ),
    "frida_missing": (
        "Android instrumentation is not ready",
        "On macOS, relaunch using run-macos.sh to prepare Frida. Check the Android connection before retrying.",
    ),
    "environment_failed": (
        "Android environment check did not finish",
        "Check ADB, Google One and Frida before retrying. If checkout was previously attempted, verify Google Play first.",
    ),
    "confirmation_required": (
        "Approval is required to continue",
        "Use the on-screen confirmation for the selected paid step. No automatic checkout will be started.",
    ),
    "exception": (
        "An unexpected error occurred",
        "Open Debug for details. Do not retry a payment until the outcome is known.",
    ),
}

# These are fixed strings, rather than arbitrary child output, so the normal
# status panel cannot expose account details or a payment token.
CLI_ISSUES = {
    "app_not_started": (
        MESSAGES["app_not_started"][0],
        "Close MuMu and reopen it. Wait for Android to finish booting, then run Check Device & Offers again from Step 1.",
    ),
    "play_store_not_started": (
        MESSAGES["play_store_not_started"][0],
        "Close MuMu and reopen it. Wait for Android to finish booting, then run Check Device & Offers again from Step 1.",
    ),
    "device_missing": ("Android device is not connected", "Start your Android device or emulator and enable ADB debugging, then run the device check."),
    "device_mismatch": ("Android device changed since the offer check", "Reconnect the Android device verified in Step 1 and run Check Device & Offers again. No checkout started."),
    "device_ambiguous": ("More than one Android device is connected", "Disconnect extra Android devices, leaving only the intended device connected, then retry."),
    "app_missing": ("An Android app is missing or disabled", "Enable Google Play and Google One; install Google One from Play Store, or use a Google Play-enabled emulator image."),
    "adb_missing": ("ADB is unavailable", "Run setup_env.py on Windows or install Android SDK platform-tools."),
    "python_missing": ("Python is unavailable", "Install Python 3.10 or newer and restart the toolkit."),
    "runtime_lookup_failed": ("Android device inspection failed", "Check ADB, the selected emulator and the local Debug log."),
    "account_unavailable": ("Google Play account could not be identified", "Open the Play Store profile and verify the intended account."),
    "account_mismatch": ("Google Play account changed", "Select the intended account in Play Store and check it before continuing."),
    "offer_query_failed": MESSAGES["offer_query_failed"],
    "offers_unavailable": MESSAGES["offer_query_failed"],
    "report_missing": ("The tool did not return a result", "Open Debug for details."),
    "account_unverified": ("Google Play account was not verified", "Open the Play Store profile and confirm the intended account before continuing."),
    "wrong_account": ("Google Play is using the wrong account", "Switch to the intended Google Play account and run Step 1 again."),
}


def cli_issue_outcome(lines: list[str], step: int) -> Outcome | None:
    """Use only known explicit wrapper codes; never infer success or authorize checkout."""
    for line in reversed(lines):
        match = re.fullmatch(r"\s*EPLUS_ISSUE:([a-z_]+)\s*", line)
        if not match:
            continue
        code = match.group(1)
        if code in ("listed", "checkout_requested"):
            return None
        entry = CLI_ISSUES.get(code) or MESSAGES.get(code)
        if not entry:
            entry = (
                "Could not complete this step",
                "Check the Android screen and technical details. Do not retry paid steps before verifying Google Play.",
            )
        title, instruction = entry
        if step >= 2:
            instruction += " Check Google Play subscriptions and payment history before another paid attempt."
        return Outcome(code, title, instruction, can_review=False)
    return None


def readable_issue_line(line: str) -> str:
    """Replace the private CLI protocol marker with safe, actionable text."""
    match = re.fullmatch(r"\s*EPLUS_ISSUE:([a-z_]+)\s*", line)
    if not match:
        # Never display an internal marker, even if a child process appends
        # unexpected characters to a status line.
        if "EPLUS_ISSUE:" in line:
            return "The step could not be completed. Review the status and open technical details."
        return line
    code = match.group(1)
    if code in ("listed", "checkout_requested"):
        return "Step result received. Review Google Play to verify the outcome."
    entry = CLI_ISSUES.get(code) or MESSAGES.get(code)
    if not entry:
        return "The step could not be completed. Review the status and open technical details."
    title, guidance = entry
    return f"{title}. Next: {guidance}"


def runtime_error_outcome(message: str, step: int) -> Outcome:
    """Classify macOS adapter failures without rendering raw exceptions."""
    validate_step(step)
    detail = message.lower()
    cases = (
        ("adb is missing", "adb_missing"),
        ("no online android device", "device_missing"),
        ("android device changed since step 1", "device_mismatch"),
        ("multiple different android devices", "device_ambiguous"),
        ("frida ", "frida_missing"),
        ("google play account changed", "account_mismatch"),
        ("account changed during checks", "account_mismatch"),
        ("google play account lookup", "account_unavailable"),
        ("could not verify google play account", "account_unavailable"),
        ("invalid google play account", "account_unavailable"),
        ("verified google play email", "account_unavailable"),
        ("offer listing could not start: app_not_started", "app_not_started"),
        ("offer listing could not start: play_store_not_started", "play_store_not_started"),
        ("offer listing", "offer_query_failed"),
        ("zero-priced first phase", "offer_not_available"),
        ("new matching report", "report_missing"),
        ("result report", "report_missing"),
        ("result belongs to an older", "report_missing"),
        ("android environment checks failed", "environment_failed"),
        ("confirmations required", "confirmation_required"),
    )
    code = next((name for fragment, name in cases if fragment in detail), "unknown")
    entry = MESSAGES.get(code) or CLI_ISSUES.get(code) or (
        "Could not complete this step",
        "Check the Android screen and technical details. Verify Google Play payments before retrying.",
    )
    title, instruction = entry
    if step >= 2:
        instruction += " Confirm the actual subscription and payment history in Google Play."
    return Outcome(code, title, instruction, can_review=False)


def safe_launch_diagnostic(error: Exception) -> str:
    """Classify local launch exceptions without exposing file paths or secrets."""
    message = str(error).lower()
    if isinstance(error, FileNotFoundError):
        for filename in ("setup_env.py", "run-all.ps1", "macos_runner.py"):
            if filename in message:
                return f"Required toolkit file missing: {filename}. Restore the repository files."
        return "A required local file is missing. Check the toolkit installation."
    if isinstance(error, PermissionError):
        return "Access denied while starting a local tool. Check file permissions."
    if "powershell was not found" in message:
        return "PowerShell could not be located. Check the Windows PowerShell installation."
    if isinstance(error, OSError):
        return "The local process could not start. Check installed tools and permissions."
    return "An unexpected startup error occurred. Check local tools and the Android connection."


def validate_step(step: int) -> int:
    if type(step) is not int or not 0 <= step <= 5:
        raise ValueError("Step must be a number between 0 and 5")
    return step


def command_for_step(step: int, repo: Path, shell: str | None = None,
                     account: str | None = None, device: str | None = None) -> list[str]:
    validate_step(step)
    if sys.platform in ("darwin", "linux") and shell is None:
        bridge = repo / "macos_runner.py"
        if not bridge.is_file():
            raise FileNotFoundError("macos_runner.py is missing")
        command = [sys.executable, str(bridge), "--step", str(step)]
        # The Textual app shows a separate approval modal for each paid stage.
        # The native adapter requires explicit flags as a second fail-closed gate.
        if step >= 2:
            command.append("--confirmed")
        if step >= 3:
            command.append("--active-confirmed")
        if account and (step >= 2 or (sys.platform == "linux" and step == 1)):
            command.extend(["--expected-account", account])
        if step >= 2 and device:
            command.extend(["--expected-device", device])
        return command
    executable = shell or shutil.which("powershell.exe") or shutil.which("pwsh")
    if not executable:
        raise RuntimeError("PowerShell was not found. Install PowerShell or run on Windows.")
    script = repo / "run-all.ps1"
    if not script.is_file():
        raise FileNotFoundError("run-all.ps1 is missing from the project directory")
    # Single steps are non-interactive at the PowerShell approval layer.
    # Using the existing wrapper keeps ADB, Frida, Play-account, offer and
    # checkout validation in one place instead of copying billing code.
    command = [executable, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
               "-File", str(script), "-Step", str(step)]
    if step >= 2 and account:
        command.extend(["-Email", account])
    if step >= 2 and device:
        command.extend(["-Serial", device])
    return command


def read_fresh_report(directory: Path, step: int, started_at: float,
                      expected_account: str | None = None) -> dict | None:
    """Read only fresh reports for the account verified by this invocation."""
    validate_step(step)
    if not directory.exists():
        return None
    # A paid result without a verified Google Play account is ambiguous.
    if step >= 2 and not expected_account:
        return None
    expected = (expected_account or "").strip().lower()
    candidates = []
    for path in directory.glob("*.json"):
        try:
            # The previous two-second grace period could accept a report
            # generated by an earlier invocation and unlock a later checkout.
            # Only accept reports written after this stage was launched.
            if path.stat().st_mtime_ns < int(started_at * 1_000_000_000):
                continue
            if step == 1 and path.name != "current.json":
                continue
            if step >= 2 and path.name == "current.json":
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("status"), str):
                if step >= 2 and str(data.get("email", "")).strip().lower() != expected:
                    continue
                candidates.append(data)
        except (OSError, ValueError, UnicodeError):
            continue
    # Multiple matching reports still cannot be assigned unambiguously to a
    # single invocation. Refuse to authorize another checkout.
    return candidates[0] if len(candidates) == 1 else None


def outcome_for_stage(step: int, exit_code: int, report: dict | None) -> Outcome:
    validate_step(step)
    if exit_code != 0 and step == 1 and report and report.get("status") == "exception":
        return Outcome("exception", "Could not connect to Android tools",
                       "The read-only check failed. Open Debug; check Frida, ADB and Google One, then retry.")
    # A failed process can still produce a fresh, safely classified report.
    # Preserve its actionable explanation without treating a checkout as successful.
    if exit_code != 0:
        status = str(report.get("status", "")) if isinstance(report, dict) else ""
        sheet = report.get("sheet") if isinstance(report, dict) else None
        reason = str(sheet.get("reason", "")) if isinstance(sheet, dict) else ""
        code = reason if reason in MESSAGES else status
        issue = CLI_ISSUES.get(code) or MESSAGES.get(code)
        if issue and code not in ("listed", "checkout_requested"):
            title, instruction = issue
            return Outcome(code, title, instruction, can_review=False)
        return Outcome("tool_error", "The step could not finish",
                       "Check Debug and the Android screen before retrying.")
    if step == 0:
        return Outcome("environment_ok", "Android environment checked",
                       "You can now list available offers.")
    if report is None:
        return Outcome("missing_report", "Could not verify the result",
                       "A fresh result report was not found. Do not proceed to another paid step.")
    status = str(report.get("status", "unknown"))
    sheet = report.get("sheet")
    reason = str(sheet.get("reason", "")) if isinstance(sheet, dict) else ""
    # A report may have a contradictory checkout_requested status but an
    # unsuccessful or missing sheet. Never enable the next paid step in that case.
    tapped_with_verified_terms = bool(
        isinstance(sheet, dict) and sheet.get("confirmed") is True
        and reason == "zero_today_and_duration_verified"
    )
    if status == "checkout_requested" and not tapped_with_verified_terms:
        code = reason if reason in MESSAGES else "checkout_not_confirmed"
    else:
        code = reason if status != "checkout_requested" and reason in MESSAGES else status
    title, instruction = (CLI_ISSUES.get(code) or MESSAGES.get(
        code, ("Could not verify this step",
               "Check the Android screen and Debug before retrying.")))
    return Outcome(code, title, instruction,
                   can_review=(step >= 2 and status == "checkout_requested"
                               and tapped_with_verified_terms))


def mask_email(value: str) -> str:
    m = re.fullmatch(r"([^@\s]+)@([^@\s]+)", value.strip())
    if not m:
        return "Not detected"
    name, domain = m.groups()
    return f"{name[:2]}***@{domain}"


def report_summary(report: dict | None) -> str:
    if not report:
        return "No fresh report"
    offers = report.get("offers")
    if isinstance(offers, list):
        return f"{len(offers)} offers returned (eligibility not verified)"
    status = str(report.get("status", ""))
    entry = CLI_ISSUES.get(status) or MESSAGES.get(status)
    return entry[0] if entry else "Review the result in Live Status"


# Only display the non-secret metadata that the existing Step 1 report supplies.
# Tokens, account identifiers, raw titles and purchase objects must not be rendered.
_SAFE_OFFER_FIELD = re.compile(r"^[A-Za-z0-9._:-]{1,72}$")


def _offer_field(value: object) -> str:
    text = str(value) if value is not None else ""
    return text if _SAFE_OFFER_FIELD.fullmatch(text) else "(unavailable)"


def offer_explorer_lines(report: dict | None, limit: int = 20) -> list[str]:
    """Format observed introductory phases; never infer eligibility or renewal.

    The source report contains only the *first* pricing phase for each offer.
    Never call a non-zero first phase 'free', never guess the currency, and do
    not render raw Frida payloads (which may include offer tokens).
    """
    if not isinstance(report, dict) or not isinstance(report.get("offers"), list):
        return ["No fresh offer details available."]
    items = [o for o in report["offers"] if isinstance(o, dict)]
    if not items:
        return ["No offers returned. Eligibility remains unknown."]
    rows = ["PRODUCT / OFFER  |  FIRST PHASE  |  INTRO PRICE"]
    for offer in items[:max(0, limit)]:
        product = _offer_field(offer.get("product"))
        offer_id = _offer_field(offer.get("id"))
        period = _offer_field(offer.get("period"))
        micros = offer.get("micros")
        if isinstance(micros, (int, str)) and str(micros) == "0":
            price = "zero (not eligibility)"
        elif isinstance(micros, (int, str)) and str(micros).isdigit():
            price = "nonzero (currency unknown)"
        else:
            price = "unknown"
        rows.append(f"{product} / {offer_id}  |  {period}  |  {price}")
    if len(items) > max(0, limit):
        rows.append(f"... {len(items) - max(0, limit)} more offer(s) not shown.")
    rows.append("Future renewal price, account eligibility and active subscription NOT verified.")
    return rows
