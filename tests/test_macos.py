"""macOS port tests. All Android/checkout interactions are mocked."""
import base64
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import macos_runner
from tui_core import command_for_step


class MacStageAdapterTests(unittest.TestCase):
    def test_paid_stage_mapping_and_no_force(self):
        offers = {
            2: ("pro12", "12months-eft", False),
            3: ("pro6", "6months-eft", True),
            4: ("pro6b", "6months-eft-2", True),
            5: ("pro6c", "6months-eft-ss-2026", True),
            6: ("ultra19", "g1.ai.ultra.3months_ip_90p.acq", False),
        }
        for step, (plan, expected, stacking) in offers.items():
            with self.subTest(step=step):
                cmd = macos_runner.stage_command(step, "emulator-5554", "alice@example.com", "python")
                self.assertEqual(cmd[cmd.index("--plan") + 1], plan)
                self.assertEqual(macos_runner.STAGES[step][1], expected)
                self.assertEqual("--stack" in cmd, stacking)
                self.assertIn("--no-switch", cmd)
                self.assertIn("--no-add", cmd)
                self.assertNotIn("--force", cmd)
        for step in (-1, 7, True, "2"):
            with self.assertRaises(ValueError):
                macos_runner.stage_command(step, "emulator-5554")
        for step in (2, 3, 4, 5, 6):
            with self.assertRaises(ValueError):
                macos_runner.stage_command(step, "emulator-5554", "current@device")

    def test_list_never_opens_checkout(self):
        cmd = macos_runner.stage_command(1, "emulator-5554")
        for flag in ("--list", "--no-add", "--no-switch"):
            self.assertIn(flag, cmd)
        for forbidden in ("--force", "--stack", "--confirmed"):
            self.assertNotIn(forbidden, cmd)

    def test_play_account_is_read_from_exact_lookup_result(self):
        token = base64.b64encode(b"alice@example.com").decode("ascii")
        response = type("Result", (), {
            "returncode": 0, "stdout": f"RUNTIME_RESULT:{token}\n"
        })()
        with patch("macos_runner.subprocess.run", return_value=response) as invoke:
            self.assertEqual(macos_runner.read_play_account("device-1", {}), "alice@example.com")
            self.assertIn("play-account", invoke.call_args.args[0])
            self.assertEqual(invoke.call_args.args[0][-2:], ["--serial", "device-1"])

    def test_paid_stage_refuses_unconfirmed_or_wrong_account(self):
        report = {"status": "listed", "offers": [{"id": "12months-eft", "micros": "0"}],
                  "detected_play_account": "alice@example.com"}
        with self.assertRaisesRegex(RuntimeError, "confirmations"):
            macos_runner.run_stage(2, "device-1", {})
        with patch("macos_runner.run_engine", return_value=0):
            with patch("macos_runner.list_offers", return_value=report):
                with patch("macos_runner.read_play_account", return_value="bob@example.com"):
                    with self.assertRaisesRegex(RuntimeError, "changed"):
                        macos_runner.run_stage(2, "device-1", {}, confirmed=True)

    def test_paid_stage_rejects_nonzero_offer(self):
        report = {"status": "listed", "offers": [{"id": "12months-eft", "micros": "3000000"}],
                  "detected_play_account": "alice@example.com"}
        with patch("macos_runner.run_engine", return_value=0) as send:
            with patch("macos_runner.list_offers", return_value=report):
                with patch("macos_runner.read_play_account", return_value="alice@example.com"):
                    with self.assertRaisesRegex(RuntimeError, "zero-priced"):
                        macos_runner.run_stage(2, "device-1", {}, confirmed=True)
            self.assertEqual(send.call_count, 1)  # environment only; no checkout

    def test_paid_stage_invokes_original_engine_only_after_checks(self):
        report = {"status": "listed", "offers": [{"id": "6months-eft", "micros": 0}],
                  "detected_play_account": "alice@example.com"}
        with patch("macos_runner.run_engine", return_value=0) as send:
            with patch("macos_runner.list_offers", return_value=report):
                with patch("macos_runner.read_play_account", return_value="alice@example.com"):
                    self.assertEqual(
                        macos_runner.run_stage(3, "device-1", {}, confirmed=True,
                                               active_confirmed=True), 0
                    )
            self.assertEqual(send.call_count, 2)  # environment check then paid engine
            paid = send.call_args.args[0]
            self.assertIn("--stack", paid)
            self.assertNotIn("--force", paid)
            self.assertEqual(paid[paid.index("--account") + 1], "alice@example.com")
            with self.assertRaisesRegex(RuntimeError, "confirmations"):
                macos_runner.run_stage(3, "device-1", {}, confirmed=True)

    def test_ultra_paid_stage_rejects_missing_renewal_or_wrong_currency(self):
        required = {"product": "g1.ai.ultra.3months_ip_90p.acq",
                    "micros": "19990000", "currency": "USD",
                    "period": "P1M", "cycles": 3,
                    "renewal_micros": "199990000",
                    "renewal_period": "P1M", "renewal_currency": "USD"}
        for change in ({"currency": "EUR"}, {"micros": "49990000"},
                       {"cycles": 1}, {"renewal_micros": ""}):
            with self.subTest(change=change):
                offer = {**required, **change}
                report = {"status": "listed", "offers": [offer]}
                with self.assertRaisesRegex(RuntimeError, "Ultra USD 19.99"):
                    macos_runner.check_offer(report, 6)
        macos_runner.check_offer({"status": "listed", "offers": [required]}, 6)

    def test_ultra_paid_requires_clean_account_attestation_before_preflight(self):
        with patch("macos_runner.run_engine") as execute:
            with self.assertRaisesRegex(RuntimeError, "clean account"):
                macos_runner.run_stage(6, "emulator-5554", {}, confirmed=True)
            execute.assert_not_called()

    def test_ultra_is_independent_no_stack_and_does_not_require_active_plan(self):
        command = macos_runner.stage_command(6, "emulator-5554",
                                              "alice@example.com", "python")
        self.assertIn("--plan", command)
        self.assertIn("ultra19", command)
        self.assertNotIn("--stack", command)
        self.assertNotIn("--force", command)
        self.assertIn("--clean-account-confirmed", command)
        with patch("macos_runner.run_engine", return_value=0) as execute, \
             patch("macos_runner.list_offers", return_value={
                 "status": "listed", "offers": [{
                     "product": "g1.ai.ultra.3months_ip_90p.acq",
                     "micros": "19990000", "currency": "USD",
                     "period": "P1M", "cycles": 3,
                     "renewal_micros": "199990000",
                     "renewal_period": "P1M", "renewal_currency": "USD"
                 }], "detected_play_account": "alice@example.com"}), \
             patch("macos_runner.read_play_account", return_value="alice@example.com"):
            self.assertEqual(macos_runner.run_stage(6, "emulator-5554", {},
                                                    confirmed=True,
                                                    clean_account_confirmed=True), 0)
            self.assertEqual(execute.call_count, 2)

    def test_tui_core_mac_passes_explicit_checkout_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "macos_runner.py").write_text("# mock", encoding="utf-8")
            with patch("tui_core.sys.platform", "darwin"):
                for step in range(7):
                    command = command_for_step(step, root)
                    self.assertEqual(command[0], sys.executable)
                    self.assertEqual(command[command.index("--step") + 1], str(step))
                    self.assertEqual("--confirmed" in command, step >= 2)
                    self.assertEqual("--active-confirmed" in command, 3 <= step <= 5)
                    self.assertEqual("--clean-account-confirmed" in command, step == 6)

    def test_reports_must_be_fresh(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(macos_runner, "REPORT_DIR", Path(temp)):
                path = Path(temp) / "current.json"
                path.write_text(json.dumps({"status": "listed"}), encoding="utf-8")
                with self.assertRaises(RuntimeError):
                    macos_runner.fresh_report("current.json", time.time_ns() + 1_000_000_000)

    def test_launcher_help_is_explicit_about_real_charges(self):
        src = (Path(__file__).resolve().parents[1] / "run-macos.sh").read_text(encoding="utf-8")
        self.assertIn("Steps 2–5 can submit real charges", src)
        self.assertIn("sh run-macos.sh", src)
        self.assertNotIn("ultra0.py --force", src)


class MacTuiTests(unittest.IsolatedAsyncioTestCase):
    async def test_macos_exposes_ultra_separately_but_never_auto_runs(self):
        from textual.widgets import Button, Select
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as temp:
            with patch("tui.is_macos_platform", return_value=True):
                app = GoogleAITUI(repo=Path(temp), selected_step=3)
            with patch("tui.subprocess.Popen") as child:
                async with app.run_test(size=(100, 30)) as pilot:
                    self.assertEqual(app.query_one("#step", Select).value, 3)
                    self.assertEqual(len(app.query("#controls .workflow-step")), 7)
                    self.assertFalse(app.query_one("#mode", Select).disabled)
                    self.assertFalse(app.busy)
                    await pilot.pause()
                child.assert_not_called()

    async def test_macos_tui_requires_checkout_approval_modal(self):
        from tui import GoogleAITUI, Approval
        with tempfile.TemporaryDirectory() as temp:
            with patch("tui.is_macos_platform", return_value=True):
                app = GoogleAITUI(repo=Path(temp), selected_step=3)
            with patch("tui.subprocess.Popen") as child:
                async with app.run_test(size=(100, 30)) as pilot:
                    app._confirm_stage(3, False)
                    await pilot.pause()
                    self.assertIsInstance(app.screen, Approval)
                    self.assertFalse(app.busy)
                child.assert_not_called()


if __name__ == "__main__":
    unittest.main()
