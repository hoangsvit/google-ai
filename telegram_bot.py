#!/usr/bin/env python3
"""Private Telegram operator bot for ePlus AI Toolkit.

Single trusted operator, private chats only. Bot commands never open checkout.
Long polling requires one running instance and no configured Telegram webhook.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any
from urllib import error, request

from device_diagnostics import inspect_connection, poll_connection

ROOT = Path(__file__).resolve().parent
API_ROOT = "https://api.telegram.org/bot"
REPORT = ROOT / "ultra0-report" / "current.json"

HELP = (
    "ePlus AI Toolkit — private operator bot\n"
    "/status — Bot and ADB connection status\n"
    "/device — Non-purchasing Android diagnostics\n"
    "/check — Check Google Play / Google One prerequisites\n"
    "/offers — Instructions for optional offer listing\n"
    "/offers confirm — Run list-only check (if enabled by operator)\n"
    "/steps — View toolkit stages\n"
    "/help — Show commands\n\n"
    "Subscription checkout (Steps 2–5) is NOT available through Telegram. "
    "Never send passwords, OTPs, payment details, tokens or raw logs."
)
STEPS = (
    "0 Environment; 1 Available offers (listing only).\n"
    "2 Pro 12 months; 3 Pro +6 months; 4 second +6 months; "
    "5 optional +6 months.\n"
    "Steps 2–5 may charge money and require in-device review and explicit "
    "local confirmation. They cannot be launched from this bot."
)
DETAIL_PREFIXES = (
    "Host:", "Frida host:", "Android ABI:", "Google Play Store:",
    "Google One:", "ADB shell:"
)
ALLOWED_RESULT_STATUSES = {
    "listed", "offer_query_failed", "play_store_not_started",
    "app_not_started", "account_unavailable", "already_subscribed",
    "ineligible", "exception", "failed"
}


class BotApiError(RuntimeError):
    """Error deliberately excluding raw request URL/token/API response body."""


@dataclass(frozen=True)
class BotConfig:
    token: str
    allowed_users: frozenset[int]
    allow_offers: bool = False

    @classmethod
    def from_env(cls) -> "BotConfig":
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        ids = os.environ.get("TELEGRAM_ALLOWED_USER_IDS", "").strip()
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN must be configured")
        if not ids or not re.fullmatch(r"\d+(?:\s*,\s*\d+)*", ids):
            raise ValueError("TELEGRAM_ALLOWED_USER_IDS must contain numeric user IDs")
        allowed = frozenset(int(x.strip()) for x in ids.split(","))
        if not allowed or any(x <= 0 for x in allowed):
            raise ValueError("At least one positive allowed Telegram user ID is required")
        return cls(token, allowed, os.environ.get("TELEGRAM_ALLOW_OFFER_CHECKS") == "1")


class TelegramTransport:
    def __init__(self, token: str):
        self._token = token

    def call(self, method: str, payload: dict[str, Any]) -> Any:
        # Method names are fixed by the bot, never from untrusted chat text.
        if method not in {"getMe", "getWebhookInfo", "getUpdates", "sendMessage"}:
            raise ValueError("Unsupported Telegram API method")
        encoded = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{API_ROOT}{self._token}/{method}",
            data=encoded,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=35) as response:
                body = json.load(response)
        except (error.HTTPError, error.URLError, OSError, ValueError, TimeoutError):
            # The urllib exception may contain the token-bearing URL. Never log it.
            raise BotApiError("Telegram connection failed; check the bot token/network") from None
        if not isinstance(body, dict) or body.get("ok") is not True:
            raise BotApiError("Telegram rejected an API request") from None
        return body.get("result")


class TelegramDiagnosticsBot:
    def __init__(self, config: BotConfig, transport: TelegramTransport | None = None):
        self.config = config
        self.transport = transport or TelegramTransport(config.token)
        self.started = time.monotonic()

    def _status(self) -> str:
        state = poll_connection()
        uptime = int(time.monotonic() - self.started)
        return (
            f"ePlus AI Toolkit bot: online\n"
            f"Uptime: {uptime // 3600}h {(uptime % 3600) // 60}m\n"
            f"ADB: {state.state}\n"
            f"Online devices: {len(state.devices)}\n"
            "No purchase/eligibility was checked."
        )

    @staticmethod
    def _diagnose() -> str:
        diagnosis = inspect_connection()
        safe_details = [
            line for line in diagnosis.details
            if any(line.startswith(prefix) for prefix in DETAIL_PREFIXES)
        ]
        return (
            f"Android: {diagnosis.headline}\n"
            f"Status: {diagnosis.status}\n" +
            ("\n".join(safe_details) + "\n" if safe_details else "") +
            f"Next: {diagnosis.guidance}\n"
            "Diagnostic only; no checkout started."
        )

    @staticmethod
    def _offer_check() -> str:
        # Offer listing is a real Android operation: it may prepare ADB/Frida
        # and alter emulator/network settings. It must be opted into explicitly.
        state = poll_connection()
        if state.state != "connected" or len(state.devices) != 1:
            return "Exactly one authorized Android device must be connected before listing offers."
        serial = state.devices[0]
        cmd = [
            sys.executable, str(ROOT / "ultra0.py"), "--list",
            "--account", "current@device", "--no-add", "--no-switch",
            "--serial", serial,
        ]
        began = time.time()
        try:
            result = subprocess.run(
                cmd, cwd=ROOT, capture_output=True, text=True, errors="replace",
                timeout=150, check=False,
                stdin=subprocess.DEVNULL,
            )
        except (OSError, subprocess.TimeoutExpired):
            return (
                "Offer listing failed or timed out. Inspect local logs and "
                "the Android screen before retrying. No checkout was requested."
            )
        # Never send stdout/stderr or report contents to Telegram: they can
        # contain email addresses, tokens and other account information.
        if result.returncode != 0:
            return "Offer listing did not finish successfully. Check the local device and sanitized logs."
        try:
            if REPORT.stat().st_mtime < began - 1:
                raise ValueError("stale result")
            report = json.loads(REPORT.read_text(encoding="utf-8"))
            status = report.get("status", "") if isinstance(report, dict) else ""
        except (OSError, ValueError, json.JSONDecodeError):
            status = ""
        label = status if status in ALLOWED_RESULT_STATUSES else "unverified"
        return (
            f"Offer listing finished. Report status: {label}.\n"
            "Review offers and account on the authorized Android device. "
            "Listing is NOT proof of eligibility, activation or a free subscription."
        )

    def response_for(self, text: str) -> str:
        words = text.strip().split()
        if not words or not words[0].startswith("/"):
            return "Use /help to view supported commands. Do not send account credentials."
        command = words[0].split("@", 1)[0].lower()
        if command in ("/start", "/help"):
            return HELP
        if command == "/status":
            return self._status()
        if command in ("/device", "/check"):
            return self._diagnose()
        if command == "/steps":
            return STEPS
        if command == "/offers":
            if len(words) != 2 or words[1].lower() != "confirm":
                return (
                    "Offer listing is read-only for purchases, but it can "
                    "prepare root/ADB/Frida and change Android settings.\n"
                    "To opt in: set TELEGRAM_ALLOW_OFFER_CHECKS=1 on the trusted "
                    "bot host, then send /offers confirm in this private chat.\n"
                    "No checkout will be started."
                )
            if not self.config.allow_offers:
                return "Offer listing is disabled by the operator. Set TELEGRAM_ALLOW_OFFER_CHECKS=1 to opt in."
            return self._offer_check()
        return "Unknown command. Use /help. Billing stages cannot be launched from Telegram."

    def handle_update(self, update: dict[str, Any]) -> None:
        message = update.get("message")
        if not isinstance(message, dict):
            return
        user = message.get("from")
        chat = message.get("chat")
        if not isinstance(user, dict) or not isinstance(chat, dict):
            return
        user_id = user.get("id")
        chat_id = chat.get("id")
        # Never answer in groups or to people outside the strict allowlist.
        # For a private Telegram chat, chat ID and sender ID must be equal.
        if (
            type(user_id) is not int or type(chat_id) is not int
            or user_id not in self.config.allowed_users
            or chat.get("type") != "private" or chat_id != user_id
        ):
            return
        text = message.get("text")
        if not isinstance(text, str):
            return
        reply = self.response_for(text)
        self.transport.call("sendMessage", {
            "chat_id": chat_id,
            "text": reply[:4000],
            "disable_web_page_preview": True,
        })

    def run(self) -> None:
        webhook = self.transport.call("getWebhookInfo", {})
        if not isinstance(webhook, dict) or webhook.get("url"):
            raise BotApiError(
                "Webhook is configured. Remove it in Telegram settings before starting long polling."
            )
        print("Telegram bot started (private allowlist; no checkout commands).", flush=True)
        offset = 0
        while True:
            try:
                updates = self.transport.call("getUpdates", {
                    "offset": offset,
                    "timeout": 20,
                    "limit": 25,
                    "allowed_updates": ["message"],
                })
                if not isinstance(updates, list):
                    raise BotApiError("Unexpected Telegram update batch")
                for update in updates:
                    if not isinstance(update, dict):
                        continue
                    update_id = update.get("update_id")
                    if type(update_id) is not int or update_id < offset:
                        continue
                    # At-most-once for this process, including if sending fails.
                    offset = update_id + 1
                    self.handle_update(update)
            except BotApiError:
                print("Telegram transport error (token/network details hidden); retrying.", flush=True)
                time.sleep(5)
            except (OSError, ValueError, TypeError):
                print("Telegram update handling error (details hidden); retrying.", flush=True)
                time.sleep(5)


def main() -> int:
    try:
        config = BotConfig.from_env()
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    TelegramDiagnosticsBot(config).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
