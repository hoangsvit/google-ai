"""Offline regressions for account email redaction in child stdout.

AGENTS.md safety rule 6 forbids printing Google account emails. The TUI masks
its own status card through ``tui_core.mask_email``, but child stdout is
rendered almost verbatim in the technical log, so every human-readable line
printed by ``ultra0.py`` must be redacted at the source.

Two kinds of text must stay raw:

* the structured ``Account <email>`` line emitted by ``macos_runner.py``,
  which ``tui.py`` parses to bind the verified account, and
* the ``--es authAccount <email>`` argument, which is a command operand and
  is captured by ``sh()`` rather than echoed.
"""
import importlib.util
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

script = Path(__file__).resolve().parents[1] / "ultra0.py"
spec = importlib.util.spec_from_file_location("ai_email_redaction", script)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

RAW = "alice.smith@gmail.com"
MASKED = "al***@gmail.com"


class RedactHelperTests(unittest.TestCase):
    def test_masks_a_full_address(self):
        self.assertEqual(mod.redact_emails(f"Processing account: {RAW}"),
                         f"Processing account: {MASKED}")

    def test_is_idempotent(self):
        once = mod.redact_emails(RAW)
        self.assertEqual(mod.redact_emails(once), once)

    def test_masks_every_address_on_a_line(self):
        text = f"expected {RAW}, saw bob.jones@yahoo.co.uk"
        result = mod.redact_emails(text)
        self.assertNotIn(RAW, result)
        self.assertNotIn("bob.jones@yahoo.co.uk", result)

    def test_leaves_plain_text_untouched(self):
        for text in ("Google Play account verified.", "   ✅ Billing module installed", ""):
            self.assertEqual(mod.redact_emails(text), text)


class NarrationIsRedactedTests(unittest.TestCase):
    """Exercise the real print paths and inspect what reaches stdout."""

    def _capture(self, call, *args, **kwargs):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            try:
                call(*args, **kwargs)
            except (Exception, SystemExit):
                # The narration happens before device work; aborting here keeps
                # the test offline instead of driving a real Frida session.
                pass
        return buffer.getvalue()

    def test_add_account_narration_is_masked(self):
        with patch.object(mod, "sh", side_effect=RuntimeError("offline")):
            output = self._capture(mod.add_account, RAW, "secret")
        self.assertNotIn(RAW, output)
        self.assertIn(MASKED, output)

    def test_switch_play_narration_is_masked(self):
        with patch.object(mod, "sh", side_effect=RuntimeError("offline")), \
             patch.object(mod.time, "sleep"):
            output = self._capture(mod.switch_play, RAW)
        self.assertNotIn(RAW, output)
        self.assertIn(MASKED, output)

    def test_processing_banner_is_masked(self):
        # Stub the account step so process() prints its banner and returns
        # without touching a device. add_account returning False short-circuits
        # the workflow before any Play Store or Frida call.
        with patch.object(mod, "add_account", return_value=False):
            output = self._capture(mod.process, RAW)
        self.assertNotIn(RAW, output)
        self.assertIn(MASKED, output)


class ProtocolTextStaysRawTests(unittest.TestCase):
    def test_auth_account_operand_is_not_masked(self):
        """The ADB argument carries identity; masking it would break the switch."""
        seen = []

        def sh(*args, **kwargs):
            seen.append(" ".join(str(a) for a in args))
            return ""

        with patch.object(mod, "sh", side_effect=sh), \
             patch.object(mod.time, "sleep"):
            try:
                mod.switch_play(RAW)
            except Exception:
                pass
        auth = [c for c in seen if "authAccount" in c]
        self.assertTrue(auth, seen)
        self.assertIn(RAW, auth[0])

    def test_runner_protocol_line_is_not_redacted(self):
        """tui.py binds the verified account from this exact line."""
        runner = (script.parent / "macos_runner.py").read_text(encoding="utf-8")
        self.assertIn('print(f"Account {account}", flush=True)', runner)
        self.assertNotIn("redact_emails", runner)


if __name__ == "__main__":
    unittest.main()
