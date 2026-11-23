"""Offline regression tests for private Telegram bot; no network or Android calls."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

from device_diagnostics import ConnectionDiagnosis, ConnectionStatus
from telegram_bot import BotConfig, TelegramDiagnosticsBot, TelegramTransport, BotApiError


class FakeTransport:
    def __init__(self):
        self.calls = []

    def call(self, method, payload):
        self.calls.append((method, payload))
        return True


def update(user_id=1234, chat_id=1234, chat_type="private", text="/status"):
    return {
        "update_id": 77,
        "message": {
            "from": {"id": user_id},
            "chat": {"id": chat_id, "type": chat_type},
            "text": text,
        },
    }


class TelegramBotTests(unittest.TestCase):
    def setUp(self):
        self.transport = FakeTransport()
        self.bot = TelegramDiagnosticsBot(
            BotConfig("fake-token", frozenset({1234})), self.transport
        )

    def test_missing_authentication_fails_closed(self):
        with patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "abc",
            "TELEGRAM_ALLOWED_USER_IDS": "",
        }):
            with self.assertRaises(ValueError):
                BotConfig.from_env()
        with patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "abc",
            "TELEGRAM_ALLOWED_USER_IDS": "1234, attacker",
        }):
            with self.assertRaises(ValueError):
                BotConfig.from_env()

    def test_strict_private_user_and_chat_authorization(self):
        for bad in (
            update(4321, 4321),
            update(1234, -1001234, "supergroup"),
            update(1234, 4321, "private"),
            update(True, True),
            update("1234", "1234"),
        ):
            self.bot.handle_update(bad)
        self.assertEqual(self.transport.calls, [])

    def test_allowed_user_can_request_status(self):
        with patch("telegram_bot.poll_connection",
                   return_value=ConnectionStatus("connected", ("emulator-5554",))):
            self.bot.handle_update(update())
        self.assertEqual(len(self.transport.calls), 1)
        method, payload = self.transport.calls[0]
        self.assertEqual(method, "sendMessage")
        self.assertEqual(payload["chat_id"], 1234)
        self.assertIn("Online devices: 1", payload["text"])
        self.assertNotIn("emulator-5554", payload["text"])

    def test_device_diagnostic_filters_transport_and_paths(self):
        diagnosis = ConnectionDiagnosis(
            "connected", "Basic Android connection found",
            (
                "Host: POSIX shell", "ADB: /private/bin/adb",
                "Android serial: SECRET-SERIAL", "Android ABI: x86_64",
                "Google Play Store: installed", "Google One: installed",
                "ADB shell: root", "Frida host: 16.5.9",
            ),
            "Use Step 1 to inspect offers.",
        )
        with patch("telegram_bot.inspect_connection", return_value=diagnosis):
            message = self.bot.response_for("/check")
        self.assertIn("Google One: installed", message)
        self.assertNotIn("SECRET-SERIAL", message)
        self.assertNotIn("/private/bin", message)

    def test_no_remote_checkout_commands(self):
        for cmd in ("/step 2", "/run 2", "/buy", "/subscribe", "/allstages"):
            message = self.bot.response_for(cmd)
            self.assertIn("Unknown command", message)

    def test_offer_check_requires_opt_in_and_confirm(self):
        with patch.object(TelegramDiagnosticsBot, "_offer_check") as check:
            self.assertIn("set TELEGRAM_ALLOW_OFFER_CHECKS", self.bot.response_for("/offers"))
            self.assertIn("disabled", self.bot.response_for("/offers confirm"))
            check.assert_not_called()
            allowed = TelegramDiagnosticsBot(
                BotConfig("fake-token", frozenset({1234}), allow_offers=True),
                self.transport,
            )
            self.assertIn("set TELEGRAM_ALLOW_OFFER_CHECKS", allowed.response_for("/offers"))
            check.assert_not_called()
            allowed.response_for("/offers confirm")
            check.assert_called_once()

    def test_offer_execution_invokes_only_list_flags_and_masks_output(self):
        allowed = TelegramDiagnosticsBot(
            BotConfig("fake-token", frozenset({1234}), allow_offers=True),
            self.transport,
        )
        with tempfile.TemporaryDirectory() as folder:
            report = Path(folder) / "current.json"
            report.write_text(json.dumps({
                "status": "listed",
                "email": "private@example.com",
                "purchase_token": "SUPER_SECRET_TOKEN",
            }), encoding="utf-8")
            fake = MagicMock()
            fake.returncode = 0
            fake.stdout = "private@example.com SUPER_SECRET_TOKEN"
            with (
                patch("telegram_bot.REPORT", report),
                patch("telegram_bot.poll_connection",
                      return_value=ConnectionStatus("connected", ("emulator-5554",))),
                patch("telegram_bot.subprocess.run", return_value=fake) as call,
            ):
                message = allowed.response_for("/offers confirm")
            argv = call.call_args.args[0]
            self.assertIn("--list", argv)
            self.assertIn("--no-add", argv)
            self.assertIn("--no-switch", argv)
            self.assertNotIn("--force", argv)
            self.assertNotIn("--stack", argv)
            self.assertNotIn("private@example.com", message)
            self.assertNotIn("SUPER_SECRET_TOKEN", message)
            self.assertIn("listed", message)

    def test_offer_execution_does_not_run_on_multiple_devices(self):
        with patch("telegram_bot.poll_connection",
                   return_value=ConnectionStatus("connected", ("first", "second"))):
            with patch("telegram_bot.subprocess.run") as run:
                self.assertIn("Exactly one", self.bot._offer_check())
                run.assert_not_called()

    def test_webhook_conflict_fails_closed(self):
        transport = MagicMock()
        transport.call.return_value = {"url": "https://somewhere.example/webhook"}
        bot = TelegramDiagnosticsBot(BotConfig("fake-token", frozenset({1234})), transport)
        with self.assertRaises(BotApiError):
            bot.run()
        transport.call.assert_called_once_with("getWebhookInfo", {})

    def test_transport_error_never_exposes_token(self):
        token = "12345:PRIVATE-TOKEN"
        transport = TelegramTransport(token)
        with patch("telegram_bot.request.urlopen", side_effect=OSError(
            f"https://api.telegram.org/bot{token}/getUpdates is not available"
        )):
            with self.assertRaises(BotApiError) as context:
                transport.call("getUpdates", {"timeout": 1})
        self.assertNotIn(token, str(context.exception))


if __name__ == "__main__":
    unittest.main()
