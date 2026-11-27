#!/usr/bin/env python3
"""Capture the running Textual app through a PTY and xterm.js in Chromium.

All states are synthetic; no emulator, real account, or transaction is used.
"""
import codecs
import fcntl
import os
import pty
import re
import select
import signal
import struct
import subprocess
import sys
import termios
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(os.environ.get("PREVIEW_OUTPUT", "terminal-previews"))
XTERM = Path(os.environ["XTERM_DIST"])
CASES = [
    ("01-startup", "startup", 110, 35, ("Check Device & Offers", "Ready — no check started", "Auto-detect", "Not checked", "LIVE STATUS")),
    ("02-disconnected", "disconnected", 110, 35, ("Android is not connected", "Got it")),
    ("03-offer-found", "offer_found", 110, 35, ("Continue to Step 2", "Later")),
    ("04-step-picker-compact", "step_picker", 90, 20, ("Run this step", "Only this step will run")),
    ("05-approval-compact", "approval", 90, 20, ("Start initial 12-month checkout", "not guaranteed", "Cancel", "Continue")),
    ("06-play-review", "review", 110, 35, ("Verified in Google Play",)),
    ("07-linux-startup", "linux_startup", 110, 35, ("GET STARTED", "Diagnose Android connection", "Ready — no check started")),
    ("08-linux-step-picker", "linux_step_picker", 110, 35, ("Choose a step", "Run this step")),
    ("09-step1-sku-offers", "sku_offers", 120, 55,
     ("SKU / PRODUCT / OFFER", "PLAY ACCOUNT UNVERIFIED", "g1.play.20tb", "19.99 USD", "Check Device & Offers")),
    ("10-step1-sku-missing", "sku_missing", 120, 55,
     ("No subscription offers returned", "Not returned", "Check Device & Offers")),
    ("11-step1-discovered-offers", "sku_extra_steps", 120, 55,
     ("5. Optional", "6months-eft-ss-2026", "PRODUCT / OFFER", "Check Device & Offers")),
    ("12-step0-ready", "environment_ready", 120, 42,
     ("Environment ready (SIMULATED)", "Check Device & Offers")),
    ("13-step0-adb-missing", "adb_missing", 120, 42,
     ("ADB not found", "Retry connection", "Got it")),
    ("14-account-picker", "account_picker", 120, 42,
     ("Google accounts on this device", "pr***e@example.invalid", "Use selected account")),
    ("15-step1-error", "offer_error", 120, 42,
     ("Offer check failed (SIMULATED)", "Check Android connection", "Got it")),
    ("16-step1-running", "offer_running", 120, 42,
     ("Checking offers", "Checking device and offers (SIMULATED)", "Stop")),
    ("17-step3-approval", "approval_3", 120, 42,
     ("Start Step 3 (+6 months)?", "Card check 2 of 3", "Cancel", "Continue")),
    ("18-step4-approval", "approval_4", 120, 42,
     ("Start Step 4 (+6 months)?", "Card check 3 of 3", "Cancel", "Continue")),
    ("19-step5-approval", "approval_5", 120, 42,
     ("Start Step 5 (+6 months)?", "Step 5 is optional", "Cancel", "Continue")),
    ("20-step3-review", "review_3", 120, 42,
     ("Step 3 submitted (SIMULATED)", "Verified in Google Play")),
    ("21-step4-review", "review_4", 120, 42,
     ("Step 4 submitted (SIMULATED)", "Review the actual subscription in Google Play")),
    ("22-step5-review", "review_5", 120, 42,
     ("Step 5 submitted (SIMULATED)", "Review the actual subscription in Google Play")),
    ("23-step3-retry", "retry_3", 120, 42,
     ("Start Step 3 (+6 months)?", "RETRY SAFETY", "Cancel", "Continue")),
    ("24-step1-unverified", "account_unverified", 120, 42,
     ("Review the offer check", "Verify the active Play account", "Got it")),
    ("25-step2-approval-wide", "approval_2", 120, 42,
     ("Start initial 12-month checkout", "Card check 1 of 3", "Cancel", "Continue")),
    ("26-step5-picker", "optional_picker", 120, 52,
     ("5. Optional", "Run optional Step 5", "Known optional offer")),
]


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        launch = {"headless": True, "args": ["--no-sandbox"]}
        if os.environ.get("CHROMIUM_PATH"):
            launch["executable_path"] = os.environ["CHROMIUM_PATH"]
        browser = playwright.chromium.launch(**launch)
        try:
            for name, scenario, cols, rows, expected in CASES:
                master, slave = pty.openpty()
                fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
                env = dict(os.environ, PREVIEW_SCENARIO=scenario, TERM="xterm-256color",
                           COLORTERM="truecolor", COLUMNS=str(cols), LINES=str(rows),
                           PYTHONIOENCODING="utf-8")
                process = subprocess.Popen([sys.executable, str(ROOT / "scripts/ci/terminal_preview_app.py")],
                                           cwd=ROOT, stdin=slave, stdout=slave, stderr=slave,
                                           env=env, start_new_session=True, close_fds=True)
                os.close(slave)
                page = browser.new_page(viewport={"width": cols * 10 + 48, "height": rows * 21 + 48},
                                        device_scale_factor=1)
                page.set_content('<html><head></head><body style="margin:0;background:#081424"><div id="terminal"></div></body></html>')
                page.add_style_tag(path=str(XTERM / "css/xterm.css"))
                page.add_script_tag(path=str(XTERM / "lib/xterm.js"))
                page.evaluate('''({cols,rows}) => {
                    window.term = new Terminal({cols, rows, fontFamily: 'monospace', fontSize: 16,
                        lineHeight: 1.25, cursorBlink: false, cursorStyle: 'bar', scrollback: 0,
                        allowProposedApi: true, theme: {background: '#081424', foreground:'#e8f2fc'}});
                    term.open(document.getElementById('terminal'));
                }''', {"cols": cols, "rows": rows})
                decoder = codecs.getincrementaldecoder("utf-8")("replace")
                deadline = time.monotonic() + 12
                found = False
                found_at = None
                visible = ""
                try:
                    while time.monotonic() < deadline:
                        ready, _, _ = select.select([master], [], [], 0.1)
                        if ready:
                            try:
                                data = os.read(master, 65536)
                            except OSError:
                                data = b""
                            if not data:
                                break
                            text = decoder.decode(data)
                            page.evaluate("text => new Promise(resolve => term.write(text, resolve))", text)
                        if process.poll() is not None:
                            break
                        visible = page.evaluate('''() => Array.from({length:term.rows}, (_,i) =>
                            term.buffer.active.getLine(i)?.translateToString(true) || '').join('\\n')''')
                        matches = all(label in visible for label in expected)
                        if scenario.startswith("sku_"):
                            # Unsupported synthetic offers must not appear as purchasable steps.
                            # Match the complete stage number, not Step 16's
                            # static Ultra reference label.
                            matches = matches and not re.search(r"(?<!\d)6\.\s+Ultra", visible)
                            if scenario != "sku_extra_steps":
                                matches = matches and not re.search(r"(?<!\d)5\.\s+Optional", visible)
                        if not matches:
                            found_at = None
                        elif found_at is None:
                            found_at = time.monotonic()
                        if matches and found_at is not None and time.monotonic() - found_at >= 0.5:
                            found = True
                            break
                    if not found:
                        print(f"{name} missing preview labels; visible screen:\n{visible}", flush=True)
                        raise RuntimeError(f"{name}: expected visible text not found: {expected!r}")
                    page.screenshot(path=str(OUTPUT / f"{name}.png"))
                    print(f"Captured {name}: {cols}x{rows} (fixture: {scenario})", flush=True)
                finally:
                    page.close()
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    os.close(master)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
