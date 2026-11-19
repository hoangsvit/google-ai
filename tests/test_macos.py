"""Offline macOS compatibility tests; never touch ADB or Google Play."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import macos_runner
from tui_core import command_for_step


class MacBridgeTests(unittest.TestCase):
    def test_commands_are_explicitly_readonly(self):
        check = macos_runner.readonly_command(0, "emulator-5554", "python3")
        listing = macos_runner.readonly_command(1, "emulator-5554", "python3")
        self.assertIn("--check", check)
        self.assertIn("--list", listing)
        self.assertIn("--no-add", listing)
        self.assertIn("--no-switch", listing)
        self.assertNotIn("--stack", listing)
        self.assertNotIn("--force", listing)
        for step in (2, 3, 4, 5):
            with self.assertRaises(ValueError):
                macos_runner.readonly_command(step, "emulator-5554")

    def test_macos_maps_only_steps_zero_and_one(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "macos_runner.py").write_text("# mock")
            with patch("tui_core.sys.platform", "darwin"):
                for step in (0, 1):
                    command = command_for_step(step, root)
                    self.assertEqual(command[-2:], ["--step", str(step)])
                    self.assertEqual(command[0], sys.executable)
                with self.assertRaises(ValueError):
                    command_for_step(2, root)

    def test_readonly_bridge_never_calls_checkout(self):
        with patch.object(macos_runner, "preflight", return_value="emulator-5554"):
            with patch.object(macos_runner.subprocess, "call", return_value=0) as called:
                self.assertEqual(macos_runner.main(["--step", "1"]), 0)
                args = called.call_args.args[0]
                self.assertIn("--list", args)
                self.assertNotIn("--stack", args)
                self.assertNotIn("--force", args)


class MacTextualTests(unittest.IsolatedAsyncioTestCase):
    async def test_macos_ui_hides_checkout_modes(self):
        from textual.widgets import Select
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as temp:
            with patch("tui.is_macos_platform", return_value=True):
                app = GoogleAITUI(repo=Path(temp))
            with patch("tui.subprocess.Popen") as spawn:
                async with app.run_test(size=(90, 20)) as pilot:
                    self.assertTrue(app.macos_readonly)
                    self.assertTrue(app.query_one("#mode", Select).disabled)
                    self.assertEqual(
                        [v for _, v in app.query_one("#step", Select)._options],
                        [0, 1],
                    )
                    app._confirm_stage(2, True)
                    app._start(3, True)
                    self.assertFalse(app.busy)
                spawn.assert_not_called()

    async def test_macos_cannot_start_paid_stage_at_construction(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as temp:
            with patch("tui.is_macos_platform", return_value=True):
                with self.assertRaises(ValueError):
                    GoogleAITUI(repo=Path(temp), selected_step=3)


if __name__ == "__main__":
    unittest.main()
