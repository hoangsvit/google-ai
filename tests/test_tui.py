"""Offline tests for the Textual frontend and its safe execution boundary."""
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from tui_core import (
    Outcome, cli_issue_outcome, command_for_step, mask_email, needs_setup, outcome_for_stage,
    readable_issue_line, read_fresh_report, report_summary, runtime_error_outcome,
    safe_launch_diagnostic, validate_step,
)


class CoreTests(unittest.TestCase):
    def test_structured_cli_error_shows_actionable_failure(self):
        result = cli_issue_outcome(["Device emulator-5554", "EPLUS_ISSUE:app_missing"], 1)
        self.assertEqual(result.code, "app_missing")
        self.assertIn("Google One", result.instruction)
        self.assertFalse(result.can_review)

    def test_ui_capture_failure_has_restart_guidance_and_never_authorizes_checkout(self):
        for step in (1, 3):
            for result in (runtime_error_outcome("Android UI capture failed", step),
                           cli_issue_outcome(["EPLUS_ISSUE:ui_capture_failed"], step)):
                self.assertEqual(result.code, "ui_capture_failed")
                self.assertIn("restart", result.instruction)
                self.assertIn("Step 1", result.instruction)
                self.assertFalse(result.can_review)
                if step >= 2:
                    self.assertIn("payment history", result.instruction)

    def test_paid_cli_errors_never_authorize_next_and_warn_about_payments(self):
        result = cli_issue_outcome(["EPLUS_ISSUE:offer_query_failed"], 2)
        self.assertFalse(result.can_review)
        self.assertIn("payment history", result.instruction)
        self.assertIsNone(cli_issue_outcome(["EPLUS_ISSUE:checkout_requested"], 2))

    def test_cli_error_rejects_untrusted_text(self):
        self.assertIsNone(cli_issue_outcome(["EPLUS_ISSUE:app_missing private@example.com"], 1))
        self.assertEqual(cli_issue_outcome(["EPLUS_ISSUE:unknown"], 1).title,
                         "Could not complete this step")

    def test_launch_error_has_friendly_title_and_next_action(self):
        for code, phrase in (
            ("launch_failed", "Google Play checkout"),
            ("billing_flow_error", "Google Play"),
            ("activity_lookup_failed", "Google One"),
            ("no_activity", "Google One"),
        ):
            with self.subTest(code=code):
                result = cli_issue_outcome([f"EPLUS_ISSUE:{code}"], 3)
                self.assertIsNotNone(result)
                self.assertIn(phrase, result.title)
                self.assertIn("Google Play", result.instruction)
                self.assertFalse(result.can_review)

    def test_fresh_billing_error_report_is_explained_even_on_nonzero_exit(self):
        report = {"status": "launch_failed"}
        for code in (0, 1):
            with self.subTest(exit_code=code):
                result = outcome_for_stage(3, code, report)
                self.assertEqual(result.code, "launch_failed")
                self.assertIn("Could not open Google Play checkout", result.title)
                self.assertFalse(result.can_review)
        self.assertEqual(report_summary(report), "Could not open Google Play checkout")

    def test_cli_protocol_markers_are_humanized_for_screen_and_debug(self):
        readable = readable_issue_line("EPLUS_ISSUE:launch_failed")
        self.assertIn("Could not open Google Play checkout", readable)
        self.assertIn("Next:", readable)
        self.assertNotIn("EPLUS_ISSUE:", readable)
        self.assertNotIn("launch_failed", readable)
        self.assertEqual(
            readable_issue_line("EPLUS_ISSUE:unknown"),
            "The step could not be completed. Review the status and open technical details.",
        )
        self.assertEqual(readable_issue_line("Normal progress line"), "Normal progress line")
        # Do not accept untrusted or malformed markers containing account data.
        self.assertEqual(
            readable_issue_line("EPLUS_ISSUE:launch_failed person@example.com"),
            "The step could not be completed. Review the status and open technical details.",
        )
    def test_every_known_engine_failure_has_user_guidance(self):
        statuses = (
            "add_account_failed", "add_account_error",
            "payment_method_not_confirmed", "account_unverified",
            "wrong_account", "play_account_switch_failed", "app_not_started",
            "offer_query_failed", "checkout_security_blocked",
            "checkout_not_confirmed", "launch_failed", "billing_flow_error",
            "billing_launch_error", "activity_lookup_failed", "no_activity",
            "subscription_update_unavailable", "ineligible",
            "purchase_unavailable", "today_price_unverified",
            "trial_duration_unverified", "already_subscribed",
            "processing", "backup_payment_methods_prompt",
            "subscribe_button_not_found", "checkout_not_visible",
        )
        for status in statuses:
            with self.subTest(status=status):
                result = outcome_for_stage(3, 0, {"status": status})
                self.assertNotIn("Could not verify this step", result.title)
                self.assertTrue(result.instruction)
                self.assertFalse(result.can_review)
                self.assertNotIn("EPLUS_ISSUE:", result.instruction)
                self.assertNotEqual(report_summary({"status": status}), status)

    def test_startup_debug_does_not_leak_private_paths_or_account_data(self):
        examples = (
            (FileNotFoundError("setup_env.py is missing from C:/Users/private@example.com"),
             "Required toolkit file missing: setup_env.py"),
            (FileNotFoundError("C:/Users/private@example.com/private.json"),
             "A required local file is missing"),
            (PermissionError("Access denied: /Users/private@example.com"),
             "Access denied"),
            (RuntimeError("PowerShell was not found."),
             "PowerShell could not be located"),
            (RuntimeError("Token secret-private@example.com"), "An unexpected startup error"),
        )
        for error, expected in examples:
            with self.subTest(error=type(error).__name__):
                diagnosis = safe_launch_diagnostic(error)
                self.assertIn(expected, diagnosis)
                self.assertNotIn("private@example.com", diagnosis)

    def test_macos_runtime_failures_are_mapped_to_safe_guidance(self):
        examples = {
            "ADB is missing. Install Android SDK Platform-Tools.": "adb_missing",
            "No online Android device. Check adb devices.": "device_missing",
            "Android device changed since Step 1; no checkout started": "device_mismatch",
            "Multiple different Android devices detected. Disconnect extras.": "device_ambiguous",
            "Frida 16.5.9 required (found none).": "frida_missing",
            "Google Play account changed during checks; stop before checkout": "account_mismatch",
            "Google Play account lookup failed; no checkout started": "account_unavailable",
            "Google Play offer listing failed; checkout not started": "offer_query_failed",
            "Step 3 offer 6months-eft has no verified zero-priced first phase.": "offer_not_available",
            "A new matching report was not produced": "report_missing",
            "Android environment checks failed; no checkout started": "environment_failed",
            "Explicit checkout and existing-plan confirmations required": "confirmation_required",
        }
        for error, code in examples.items():
            with self.subTest(code=code):
                result = runtime_error_outcome(error, 3)
                self.assertEqual(result.code, code)
                self.assertTrue(result.title)
                self.assertIn("Google Play", result.instruction) if code not in (
                    "adb_missing", "device_missing", "device_ambiguous", "frida_missing",
                    "confirmation_required",
                ) else None
                self.assertFalse(result.can_review)
        fallback = runtime_error_outcome("Unexpected private error@example.com", 2)
        self.assertEqual(fallback.code, "unknown")
        self.assertNotIn("error@example.com", fallback.instruction)

    def test_macos_tui_marker_round_trip_keeps_device_recovery_guidance(self):
        for message, code in (
            ("No online Android device. Check adb devices.", "device_missing"),
            ("Multiple different Android devices detected. Disconnect extras.", "device_ambiguous"),
        ):
            with self.subTest(code=code):
                native = runtime_error_outcome(message, 1)
                shown = cli_issue_outcome([f"EPLUS_ISSUE:{native.code}"], 1)
                self.assertEqual(shown.code, native.code)
                self.assertEqual(shown.instruction, native.instruction)
                self.assertIn("Android", shown.instruction)
                self.assertNotIn("MuMu", shown.instruction)
                self.assertNotIn("select a serial in the CLI", shown.instruction)
                self.assertFalse(shown.can_review)

    def test_setup_only_when_pinned_frida_is_missing(self):
        with patch("tui_core.importlib.metadata.version", return_value="16.5.9"):
            self.assertFalse(needs_setup())
        with patch("tui_core.importlib.metadata.version", return_value="16.4.0"):
            self.assertTrue(needs_setup())
        from importlib.metadata import PackageNotFoundError
        with patch("tui_core.importlib.metadata.version", side_effect=PackageNotFoundError):
            self.assertTrue(needs_setup())

    def test_step_range(self):
        for step in range(6):
            self.assertEqual(validate_step(step), step)
        for value in (-1, 6, "2", True):
            with self.assertRaises(ValueError):
                validate_step(value)

    def test_reuses_single_step_powershell_wrapper(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            (p / "run-all.ps1").write_text("# test")
            command = command_for_step(3, p, shell="powershell.exe")
            self.assertEqual(command[-4:], ["-File", str(p / "run-all.ps1"), "-Step", "3"])
            self.assertNotIn("-AllStages", command)
            self.assertNotIn("-Force", command)

    def test_windows_paid_command_pins_verified_serial(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "run-all.ps1").write_text("# test", encoding="utf-8")
            command = command_for_step(3, root, shell="pwsh",
                                       account="alice@example.com", device="device-a")
            self.assertEqual(command[-4:], ["-Email", "alice@example.com", "-Serial", "device-a"])
            self.assertNotIn("-Force", command)

    def test_no_shell_or_script_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):
                command_for_step(1, Path(folder), shell="pwsh")

    def test_stale_reports_cannot_confirm_old_checkout(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "report"
            p.mkdir()
            f = p / "test.json"
            f.write_text(json.dumps({"status": "checkout_requested", "email": "alice@example.com"}))
            now = time.time()
            import os
            os.utime(f, (now - 600, now - 600))
            self.assertIsNone(read_fresh_report(p, 3, now, expected_account="alice@example.com"))
            result = outcome_for_stage(3, 0, None)
            self.assertFalse(result.can_review)

    def test_recent_previous_report_cannot_authorize_checkout(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            report = p / "account.json"
            report.write_text(json.dumps({"status": "checkout_requested", "email": "alice@example.com"}))
            started_at = time.time()
            # A completed run 0.5 seconds earlier must not be treated as
            # belonging to a new request just because file mtime is recent.
            import os
            os.utime(report, (started_at - 0.5, started_at - 0.5))
            self.assertIsNone(read_fresh_report(p, 3, started_at, expected_account="alice@example.com"))

    def test_conflicting_account_reports_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            started_at = time.time() - 10
            (p / "account-a.json").write_text(
                json.dumps({"status": "checkout_requested", "email": "alice@example.com"}))
            (p / "account-b.json").write_text(
                json.dumps({"status": "checkout_requested", "email": "alice@example.com"}))
            self.assertIsNone(read_fresh_report(
                p, 3, started_at, expected_account="alice@example.com"))
            self.assertFalse(outcome_for_stage(3, 0, None).can_review)

    def test_one_fresh_checkout_report_can_be_reviewed(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            started_at = time.time() - 10
            (p / "account.json").write_text(
                json.dumps({"status": "checkout_requested", "email": "alice@example.com",
                            "sheet": {"confirmed": True, "reason": "zero_today_and_duration_verified"}}))
            report = read_fresh_report(p, 3, started_at, expected_account="alice@example.com")
            self.assertIsNotNone(report)
            self.assertTrue(outcome_for_stage(3, 0, report).can_review)

    def test_foreign_checkout_report_is_never_eligible_for_review(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            (p / "account-foreign.json").write_text(json.dumps({
                "email": "other@example.com", "status": "checkout_requested",
            }))
            started_at = time.time() - 10
            self.assertIsNone(read_fresh_report(
                p, 3, started_at, expected_account="alice@example.com"))
            self.assertIsNone(read_fresh_report(p, 3, started_at))
            # The account matches, but the report belongs to another person.
            self.assertIsNotNone(read_fresh_report(
                p, 3, started_at, expected_account="other@example.com"))

    def test_step_one_remains_account_independent(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            (p / "current.json").write_text(json.dumps({
                "email": "current@device", "status": "listed", "offers": [],
            }))
            self.assertIsNotNone(read_fresh_report(p, 1, time.time() - 10))

    def test_security_block_and_duplicate_cannot_continue(self):
        for reason in ("payment_security_blocked", "already_subscribed",
                       "trial_duration_unverified"):
            result = outcome_for_stage(3, 0, {
                "status": "checkout_not_confirmed", "sheet": {"reason": reason}
            })
            self.assertFalse(result.can_review)

    def test_requested_is_not_claimed_active(self):
        result = outcome_for_stage(3, 0, {
            "status": "checkout_requested",
            "sheet": {"confirmed": True, "reason": "zero_today_and_duration_verified"},
        })
        self.assertTrue(result.can_review)
        self.assertNotIn("activated", result.title.lower())
        self.assertIn("Check Google Play", result.instruction)

    def test_incomplete_or_conflicting_checkout_report_cannot_continue(self):
        for sheet in (
            None,
            {"reason": "purchase_unavailable", "confirmed": True},
            {"reason": "zero_today_and_duration_verified", "confirmed": False},
        ):
            with self.subTest(sheet=sheet):
                result = outcome_for_stage(3, 0, {
                    "status": "checkout_requested", "sheet": sheet,
                })
                self.assertFalse(result.can_review)
                self.assertNotEqual(result.code, "checkout_requested")

    def test_exit_error_never_allows_next(self):
        result = outcome_for_stage(3, 1, {"status": "checkout_requested"})
        self.assertFalse(result.can_review)

    def test_numbered_masked_account_picker_hints(self):
        from tui_core import account_picker_label
        first = account_picker_label("alice@example.com", 1)
        second = account_picker_label("alicia@example.com", 2)
        self.assertNotEqual(first, second)
        self.assertNotIn("alice@example.com", first)
        self.assertNotIn("alicia@example.com", second)

    def test_colliding_picker_hints_and_short_local_parts(self):
        from tui_core import account_picker_options
        options = account_picker_options(["albert@example.com", "allent@example.com"])
        self.assertEqual(len(options), 2)
        self.assertNotEqual(options[0][0].split(". ", 1)[1], options[1][0].split(". ", 1)[1])
        self.assertEqual(account_picker_options(["a@example.com", "ab@example.com"]), [])
        self.assertEqual(mask_email("ab@example.com"), "***@example.com")
        self.assertEqual(account_picker_options(["albert@example.com", "alxert@example.com"]), [])

    def test_redacted_diagnostic_preserves_nonidentity_details(self):
        from tui_core import redact_diagnostic
        self.assertEqual(redact_diagnostic("Account alice@example.com"), "Account [account hidden]")
        self.assertEqual(redact_diagnostic("Device emulator-5554"), "Device [device hidden]")
        self.assertEqual(redact_diagnostic("ADB emulator-5554 ready", "emulator-5554"), "ADB [device hidden] ready")

    def test_account_mask(self):
        self.assertEqual(mask_email("example@gmail.com"), "ex***@gmail.com")
        self.assertEqual(mask_email("invalid"), "Not detected")


class AccountCommandTests(unittest.TestCase):
    def test_windows_paid_step_pins_selected_account(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "run-all.ps1").touch()
            with patch("tui_core.sys.platform", "win32"):
                cmd = command_for_step(3, root, shell="powershell.exe",
                                       account="selected@example.com")
                self.assertEqual(cmd[-2:], ["-Email", "selected@example.com"])
                check = command_for_step(1, root, shell="powershell.exe",
                                          account="selected@example.com")
                self.assertNotIn("-Email", check)

    def test_macos_paid_step_pins_selected_account(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "macos_runner.py").touch()
            with patch("tui_core.sys.platform", "darwin"):
                cmd = command_for_step(3, root, account="selected@example.com")
                self.assertEqual(cmd[-2:], ["--expected-account", "selected@example.com"])


class TextualSmokeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # These regression tests exercise the Windows frontend even when CI
        # itself runs on Linux. The Linux route has dedicated test_linux.py.
        platform_patcher = patch("tui.sys.platform", "win32")
        platform_patcher.start()
        self.addCleanup(platform_patcher.stop)
        # Smoke tests must not depend on host ADB state or a five-second timer.
        from tui import GoogleAITUI
        patcher = patch.object(GoogleAITUI, "_poll_connection")
        patcher.start()
        self.addCleanup(patcher.stop)

    async def test_research_steps_are_in_scrollable_sidebar(self):
        from tui import GoogleAITUI
        from research_offer_catalog import STEP_REFERENCES, research_sidebar_label
        from textual.containers import VerticalScroll

        for size in ((90, 20), (110, 35)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=size) as pilot:
                    await pilot.pause()
                    scroll = app.query_one("#research_workflow", VerticalScroll)
                    for step in STEP_REFERENCES:
                        node = scroll.query_one(f"#stage_{step}")
                        self.assertIn(research_sidebar_label(step), str(node.render()))
                    self.assertLess(scroll.region.height, len(STEP_REFERENCES))
                    app._set_workflow(9, "review")
                    self.assertIn("!", str(scroll.query_one("#stage_9").render()))

    async def test_header_clock_shows_local_date_time_and_utc_offset(self):
        from datetime import datetime, timedelta, timezone
        from tui import GoogleAITUI, LocalClock

        local_zone = timezone(timedelta(hours=7))
        for size in ((58, 20), (90, 20), (110, 35)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch("tui.datetime") as host_time:
                    host_time.now.return_value.astimezone.return_value = datetime(
                        2026, 11, 25, 23, 59, 59, tzinfo=local_zone,
                    )
                    async with app.run_test(size=size) as pilot:
                        await pilot.pause()
                        clock = app.query_one(LocalClock)
                        self.assertEqual(str(clock.render()), "2026-11-25 23:59:59 UTC+07:00")
                        self.assertEqual(clock.region.right, size[0])
                        self.assertGreaterEqual(clock.region.width, len(str(clock.render())))
                        self.assertLessEqual(app.query_one("HeaderTitle").region.right, clock.region.x)
                        host_time.now.return_value.astimezone.return_value = datetime(
                            2026, 11, 26, tzinfo=local_zone,
                        )
                        clock.update_time()
                        self.assertEqual(str(clock.render()), "2026-11-26 00:00:00 UTC+07:00")

    async def test_mode_refresh_ignores_unmounted_widgets(self):
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(90, 20)):
                # A delayed Select.Changed event can arrive during shutdown
                # after Textual has removed its widgets.
                with patch.object(app, "query", return_value=[]):
                    app._update_run_mode()

    async def test_choose_account_requires_new_read_only_check(self):
        from textual.widgets import Select
        from tui import AccountPicker, GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                app._offer_check_ready = True
                app._offer_ready_account = "old@example.com"
                app._account_candidates_loaded(["first@example.com", "second@example.com"])
                await pilot.pause()
                self.assertIsInstance(app.screen, AccountPicker)
                app.screen.query_one("#account_choice", Select).value = "second@example.com"
                await pilot.click("#account_accept")
                await pilot.pause()
                self.assertEqual(app._selected_account, "second@example.com")
                self.assertFalse(app._offer_check_ready)
                self.assertIsNone(app._offer_ready_account)

    async def test_account_picker_close_preserves_completed_lookup_status(self):
        from textual.widgets import Static
        from tui import AccountPicker, GoogleAITUI

        cases = ((None, "Account list unavailable"), ([], "No Android accounts detected"),
                 (["first@example.com"], "Account lookup complete"))
        for accounts, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=(110, 35)) as pilot:
                    app._set_status("Reading Android accounts...")
                    app._account_candidates_loaded(accounts, "emulator-5554")
                    await pilot.pause()
                    self.assertIsInstance(app.screen, AccountPicker)
                    self.assertTrue(await pilot.click("#account_cancel"))
                    await pilot.pause()
                    self.assertIn(expected, str(app.query_one("#state", Static).render()))
                    self.assertFalse(app._accounts_loading)

    async def test_manage_accounts_opens_settings_and_requires_fresh_offer_check(self):
        from device_diagnostics import ConnectionStatus
        from textual.widgets import Button
        from tui import AccountPicker, GoogleAITUI, SetupNotice

        for size in ((58, 20), (90, 20), (110, 35)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=size) as pilot:
                    serial = "emulator-5554"
                    app._connection_state = ConnectionStatus("connected", (serial,))
                    app._offer_check_ready = True
                    app._offer_ready_device = serial
                    app._selected_account = app._verified_account = app._offer_ready_account = "old@example.com"
                    app.sequence = True
                    self.assertFalse(app.query("#account_remove"))
                    with patch.object(app, "_account_runtime_value", return_value="opened") as lookup:
                        app._account_candidates_loaded(None, serial)
                        await pilot.pause()
                        self.assertIsInstance(app.screen, AccountPicker)
                        self.assertFalse(app.screen.query("#account_accept"))
                        self.assertTrue(await pilot.click("#account_remove"))
                        await app.workers.wait_for_complete()
                    await pilot.pause()
                    lookup.assert_called_once_with("android-account-settings-connected", serial, timeout=35)
                    self.assertIsInstance(app.screen, SetupNotice)
                    self.assertEqual(str(app.screen.query_one("#notice_close", Button).label), "Done managing")
                    self.assertTrue(app.query_one("#quickstart", Button).disabled)
                    with patch.object(app, "run_stage") as run:
                        app._start(1, False)
                        run.assert_not_called()
                    self.assertTrue(await pilot.click("#notice_close"))
                    await pilot.pause()
                    self.assertFalse(app.query_one("#quickstart", Button).disabled)
                    self.assertFalse(app._offer_check_ready)
                    self.assertIsNone(app._offer_ready_device)
                    self.assertIsNone(app._offer_ready_account)
                    self.assertIsNone(app._selected_account)
                    self.assertIsNone(app._verified_account)
                    self.assertFalse(app.sequence)

    async def test_manage_accounts_explains_multiple_devices_and_rejects_running_stage(self):
        from tui import GoogleAITUI, SetupNotice

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(90, 20)) as pilot:
                with patch.object(app, "_account_runtime_value", return_value="multiple_devices") as lookup:
                    with patch.object(app, "busy", True):
                        app._manage_android_accounts("")
                        lookup.assert_not_called()
                    app._account_candidates_loaded([])
                    await pilot.pause()
                    self.assertTrue(await pilot.click("#account_remove"))
                    await app.workers.wait_for_complete()
                await pilot.pause()
                self.assertIsInstance(app.screen, SetupNotice)
                self.assertIn("only the intended MuMu device", app.screen.instruction)
                self.assertTrue(await pilot.click("#notice_close"))
                await pilot.pause()
                self.assertFalse(app._diagnosing)

    async def test_selected_account_must_match_read_only_check(self):
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)):
                app._selected_account = "second@example.com"
                app._checked_device = "emulator-5554"
                app._verified_account = "first@example.com"
                app._finished(1, Outcome("listed", "Offers listed", "Review first phase."), {
                    "status": "listed", "detected_play_account": "first@example.com",
                    "offers": [{"id": "6months-eft", "micros": "0"}],
                })
                self.assertFalse(app._offer_check_ready)
                self.assertIsNone(app._offer_ready_account)

    async def test_unlocking_step_two_also_unlocks_steps_three_through_four(self):
        from textual.widgets import Button, Select, Static
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                app.query_one("#step", Select).value = 3
                # The Select.Changed message may be queued behind layout
                # events on Windows. Synchronize the guard deterministically
                # before asserting a state transition caused by the selector.
                app._update_run_mode()
                await pilot.pause()
                self.assertEqual(app.query_one("#step", Select).value, 3)
                self.assertTrue(app.query_one("#run", Button).disabled)

                # The single successful read-only Step 1 check unlocks every
                # fixed paid choices 2-4; Step 5+ require observed extra offers.
                app._checked_device = "emulator-5554"
                app._verified_account = "first@example.com"
                app._finished(1, Outcome("listed", "Offers listed", "Review first phase."), {
                    "status": "listed",
                    "detected_play_account": "first@example.com",
                    "offers": [{"id": "12months-eft", "micros": "0"}],
                })
                await pilot.pause()
                self.assertTrue(app._offer_check_ready)
                self.assertEqual(app._offer_ready_account, "first@example.com")
                self.assertEqual(app._offer_ready_device, "emulator-5554")
                if app.screen is not app:
                    app.screen.dismiss(False)
                    await pilot.pause()

                for step in (2, 3, 4):
                    with self.subTest(step=step):
                        app.query_one("#step", Select).value = step
                        await pilot.pause()
                        self.assertFalse(app.query_one("#run", Button).disabled)
                        self.assertIn("unlocked", str(app.query_one("#mode_hint", Static).render()))

                # A paid stage may fail before its runner emits fresh account
                # details. That uncertainty is not evidence of a changed
                # account: leave all choices open and let the NEXT paid run
                # revalidate the identity/offer before billing.
                app.current_step = 2
                app._checked_device = None
                app._verified_account = None
                app._finished(2, Outcome("tool_error", "Step failed", "Review Google Play."), None)
                await pilot.pause()
                self.assertTrue(app._offer_check_ready)
                for step in (2, 3, 4):
                    with self.subTest(step_after_failure=step):
                        app.query_one("#step", Select).value = step
                        await pilot.pause()
                        self.assertFalse(app.query_one("#run", Button).disabled)

    async def test_verified_identity_failure_relocks_every_paid_step(self):
        from textual.widgets import Button, Select
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                app._offer_check_ready = True
                app._offer_ready_device = "emulator-5554"
                app._offer_ready_account = "first@example.com"
                app.current_step = 3
                app._finished(3, Outcome("account_mismatch",
                                         "Wrong account", "Check Play Store."), None)
                self.assertFalse(app._offer_check_ready)
                self.assertIsNone(app._offer_ready_account)
                for step in (2, 3, 4):
                    app.query_one("#step", Select).value = step
                    for _ in range(20):
                        if app.query_one("#run", Button).disabled:
                            break
                        await pilot.pause(0.05)
                    self.assertTrue(app.query_one("#run", Button).disabled)

    async def test_paid_retry_rejects_verified_device_replacement(self):
        from textual.widgets import Static
        from device_diagnostics import ConnectionStatus
        from tui import Approval, GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)):
                app._offer_check_ready = True
                app._offer_ready_device = "device-a"
                app._offer_ready_account = "alice@example.com"
                app._connection_state = ConnectionStatus("connected", ("device-b",))
                app._confirm_stage(3, False)
                self.assertFalse(app._offer_check_ready)
                self.assertNotIsInstance(app.screen, Approval)
                self.assertIn("device changed", app.query_one("#state", Static).render().plain.lower())
                app._start(3, False)
                self.assertFalse(app.busy)

    async def test_failed_paid_stage_can_retry_only_on_same_account_and_device(self):
        from tui import Approval, GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                app._offer_check_ready = True
                app._offer_ready_account = "first@example.com"
                app._offer_ready_device = "emulator-5554"
                app._verified_account = "first@example.com"
                app._checked_device = "emulator-5554"
                app.current_step = 3
                app._finished(3, Outcome("purchase_unavailable",
                                         "Purchase unavailable", "Check Google Play."), {
                    "status": "purchase_unavailable",
                })
                self.assertTrue(app._offer_check_ready)
                app._confirm_stage(3, False)
                await pilot.pause()
                self.assertIsInstance(app.screen, Approval)
                self.assertIn("RETRY SAFETY", app.screen.message_text)

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)):
                app._offer_check_ready = True
                app._offer_ready_account = "first@example.com"
                app._offer_ready_device = "emulator-5554"
                app._verified_account = "other@example.com"
                app._checked_device = "emulator-5554"
                app._finished(3, Outcome("purchase_unavailable",
                                         "Purchase unavailable", "Check Google Play."), None)
                self.assertFalse(app._offer_check_ready)

    async def test_start_screen_shows_status_and_primary_action(self):
        from tui import GoogleAITUI
        for size in ((90, 20), (110, 35)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=size) as pilot:
                    await pilot.pause()
                    status = app.query_one("#status_panel").region
                    state = app.query_one("#state").region
                    action = app.query_one("#quickstart").region
                    self.assertGreaterEqual(state.y, status.y)
                    self.assertLessEqual(state.bottom, status.bottom - 1)
                    self.assertGreaterEqual(action.y, 0)
                    self.assertLessEqual(action.bottom, size[1])
    async def test_checkout_dialog_fits_compact_terminal(self):
        from tui import GoogleAITUI, Approval
        for size in ((90, 20), (60, 20), (110, 35), (155, 40)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=size) as pilot:
                    app._offer_check_ready = True
                    app._confirm_stage(4 if size[1] >= 35 else 2, False)
                    await pilot.pause()
                    self.assertIsInstance(app.screen, Approval)
                    card = app.screen.query_one("#approval_card").region
                    self.assertGreaterEqual(card.y, 0)
                    self.assertLessEqual(card.bottom, size[1])
                    for selector in ("#cancel", "#approve", "#approval_scroll"):
                        region = app.screen.query_one(selector).region
                        self.assertGreaterEqual(region.y, card.y)
                        self.assertLessEqual(region.bottom, card.bottom)
                    if size[1] >= 35:
                        message = app.screen.query_one("#approval_message").region
                        actions = app.screen.query_one("#approval_actions").region
                        self.assertLessEqual(actions.y - message.bottom, 2)
    async def test_step_picker_defaults_to_one_step_and_hides_extra_options(self):
        from textual.widgets import Button, Select
        from tui import GoogleAITUI
        for size in ((110, 35), (90, 20)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch.object(GoogleAITUI, "_confirm_stage") as confirm:
                    async with app.run_test(size=size) as pilot:
                        app.advanced_pressed()
                        # Windows runners can need several refreshes for the
                        # deferred scroll and layout to settle.
                        for _ in range(30):
                            await pilot.pause(0.1)
                            viewport = app.query_one("#results").region
                            if all(viewport.y <= app.query_one(q).region.y and
                                   app.query_one(q).region.bottom <= viewport.bottom
                                   for q in ("#step", "#run")):
                                break
                        self.assertFalse(app.query_one("#mode_field").display)
                        self.assertTrue(app.query_one("#step", Select).display)
                        viewport = app.query_one("#results").region
                        for selector in ("#step", "#run"):
                            region = app.query_one(selector).region
                            self.assertGreaterEqual(region.y, viewport.y)
                            self.assertLessEqual(region.bottom, viewport.bottom)
                        self.assertIn("Run this step", str(app.query_one("#run", Button).label))
                        self.assertEqual(app.query_one("#mode", Select).value, "single")
                        app.selected_pressed()
                        confirm.assert_called_with(1, False)
                        # The advanced modes are accessible at the end of
                        # the step dropdown, without a separate third button.
                        app.query_one("#step", Select).value = 99
                        for _ in range(20):
                            await pilot.pause(0.05)
                            if app.query_one("#mode_field").display:
                                break
                        self.assertTrue(app.query_one("#mode_field").display)
                        self.assertEqual(app.query_one("#step", Select).value, 1)
                        app.query_one("#mode", Select).value = "from"
                        app.query_one("#step", Select).value = 99
                        for _ in range(20):
                            await pilot.pause(0.05)
                            if not app.query_one("#mode_field").display:
                                break
                        self.assertFalse(app.query_one("#mode_field").display)
                        self.assertEqual(app.query_one("#mode", Select).value, "single")

    async def test_run_hint_sits_below_the_run_button_not_beside_it(self):
        from tui import GoogleAITUI
        for size in ((110, 35), (90, 20)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch.object(GoogleAITUI, "_confirm_stage"):
                    async with app.run_test(size=size) as pilot:
                        app.advanced_pressed()
                        # Windows runners can need several refreshes for the
                        # deferred scroll and layout to settle.
                        for _ in range(30):
                            await pilot.pause(0.1)
                            viewport = app.query_one("#results").region
                            hint = app.query_one("#mode_hint").region
                            if viewport.y <= hint.y and hint.bottom <= viewport.bottom:
                                break
                        run = app.query_one("#run").region
                        step = app.query_one("#step").region
                        hint = app.query_one("#mode_hint").region
                        # The primary action must match the step selector in
                        # both compact and regular terminal layouts.
                        self.assertEqual(run.x, step.x)
                        self.assertEqual(run.width, step.width)
                        self.assertGreaterEqual(hint.y, run.bottom)
                        viewport = app.query_one("#results").region
                        for region in (run, hint):
                            self.assertGreaterEqual(region.y, viewport.y)
                            self.assertLessEqual(region.bottom, viewport.bottom)

    async def test_connection_monitor_warns_once_and_recovers_without_unlocking_checkout(self):
        from tui import GoogleAITUI, ConnectionNotice
        from device_diagnostics import ConnectionStatus
        from textual.widgets import Static
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                app._offer_check_ready = True
                app._connection_polled(ConnectionStatus("disconnected"))
                await pilot.pause()
                self.assertIsInstance(app.screen, ConnectionNotice)
                card = app.screen.query_one("#notice_card").region
                self.assertGreater(card.x, 0)
                self.assertGreater(card.y, 0)
                self.assertFalse(app._offer_check_ready)
                app._connection_polled(ConnectionStatus("disconnected"))
                await pilot.pause()
                self.assertIsInstance(app.screen, ConnectionNotice)
                app._connection_polled(ConnectionStatus("connected", ("emulator-5554",)))
                await pilot.pause()
                self.assertNotIsInstance(app.screen, ConnectionNotice)
                self.assertFalse(app._offer_check_ready)
                self.assertIn("connected", str(app.query_one("#device", Static).render()).lower())

    async def test_startup_without_android_shows_notice_once_until_connection_changes(self):
        from device_diagnostics import ConnectionStatus
        from textual.widgets import Button
        from tui import ConnectionNotice, GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory), startup_probe=True)
            async with app.run_test(size=(90, 20)) as pilot:
                disconnected = ConnectionStatus("disconnected")
                app._connection_polled(disconnected, app._connection_generation, startup=True)
                await pilot.pause()
                self.assertIsInstance(app.screen, ConnectionNotice)
                self.assertEqual(app.screen.notice_title, "Android is not connected")
                self.assertFalse(app.screen.query_one("#connection_start_mumu", Button).disabled)
                self.assertTrue(await pilot.click("#notice_close"))
                await pilot.pause()

                app._connection_polled(disconnected, app._connection_generation)
                await pilot.pause()
                self.assertNotIsInstance(app.screen, ConnectionNotice)

                with patch.object(app, "discover_account_candidates"):
                    app._connection_polled(ConnectionStatus("connected", ("emulator-5554",)))
                app._connection_polled(disconnected, app._connection_generation)
                await pilot.pause()
                self.assertIsInstance(app.screen, ConnectionNotice)
                self.assertFalse(app._offer_check_ready)

    async def test_connection_results_are_ignored_during_checkout(self):
        from tui import GoogleAITUI
        from device_diagnostics import ConnectionStatus
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)):
                app.busy = True
                app.current_step = 2
                app._offer_check_ready = True
                app._connection_polled(ConnectionStatus("disconnected"))
                self.assertTrue(app._offer_check_ready)
                self.assertIsNone(app._connection_state)

    async def test_stale_poll_from_before_stage_cannot_erase_fresh_readiness(self):
        from tui import GoogleAITUI, CheckComplete, ConnectionNotice
        from device_diagnostics import ConnectionStatus
        from tui_core import Outcome

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                old_generation = app._connection_generation
                app._connection_polling = True
                with patch.object(GoogleAITUI, "run_stage"):
                    app._start(1, False)
                    app._received("Device emulator-5554")
                    app._verified_account = "test@example.com"
                    app._finished(1, Outcome("listed", "Offers loaded", "Review"), {
                        "offers": [{"id": "12months-eft", "micros": "0"}],
                        "detected_play_account": "test@example.com",
                    })
                await pilot.pause()
                self.assertIsInstance(app.screen, CheckComplete)
                await pilot.click("#check_later")
                await pilot.pause()
                app._connection_polled(ConnectionStatus("disconnected"), old_generation)
                self.assertTrue(app._offer_check_ready)
                self.assertNotIsInstance(app.screen, ConnectionNotice)
                self.assertEqual(app._connection_state.devices, ("emulator-5554",))

    async def test_stale_poll_from_before_diagnosis_is_ignored(self):
        from tui import GoogleAITUI, ConnectionNotice
        from device_diagnostics import ConnectionStatus

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)):
                old_generation = app._connection_generation
                app._connection_polling = True
                with patch.object(GoogleAITUI, "inspect_android_connection"):
                    app.diagnose_pressed()
                app._diagnosing = False
                app._connection_polled(ConnectionStatus("disconnected"), old_generation)
                self.assertIsNone(app._connection_state)
                self.assertNotIsInstance(app.screen, ConnectionNotice)

    async def test_step_one_ready_device_survives_first_postcheck_poll(self):
        from tui import GoogleAITUI, CheckComplete
        from device_diagnostics import ConnectionStatus
        from tui_core import Outcome

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                app._connection_state = ConnectionStatus("connected", ("emulator-5554",))
                app._received("Device emulator-5556")
                app._verified_account = "test@example.com"
                app._finished(1, Outcome("listed", "Offers loaded", "Review"), {
                    "offers": [{"id": "12months-eft", "micros": "0"}],
                    "detected_play_account": "test@example.com",
                })
                await pilot.pause()
                self.assertIsInstance(app.screen, CheckComplete)
                await pilot.click("#check_later")
                await pilot.pause()
                self.assertEqual(app._offer_ready_device, "emulator-5556")
                app._connection_polled(ConnectionStatus("connected", ("emulator-5556",)))
                self.assertTrue(app._offer_check_ready)
                app._connection_polled(ConnectionStatus("connected", ("emulator-5558",)))
                self.assertFalse(app._offer_check_ready)
                self.assertIsNone(app._offer_ready_device)

    async def test_application_branding(self):
        from tui import GoogleAITUI
        self.assertEqual(GoogleAITUI.TITLE, "ePlus AI Toolkit")
        self.assertEqual(GoogleAITUI.SUB_TITLE, "ePlus.DEV")

    async def test_telegram_support_channel_is_clickable(self):
        from textual.widgets import Link, Static
        from tui import GoogleAITUI

        for size in ((110, 35), (90, 20)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch("tui.subprocess.Popen") as launch:
                    async with app.run_test(size=size) as pilot:
                        await pilot.pause()
                        channel = app.query_one("#support_link", Link)
                        self.assertEqual(channel.url, "https://t.me/eplus_news")
                        self.assertTrue(channel.display)
                        self.assertGreater(channel.region.width, 8)
                        self.assertIn(
                            "Support:", str(app.query_one("#support_label", Static).render())
                        )
                    launch.assert_not_called()

    async def test_github_credits_are_clickable_links(self):
        from textual.widgets import Link
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch("tui.subprocess.Popen") as popen:
                async with app.run_test(size=(110, 35)):
                    self.assertEqual(
                        app.query_one("#original_author", Link).url,
                        "https://github.com/gylive",
                    )
                    self.assertEqual(
                        app.query_one("#maintainer", Link).url,
                        "https://github.com/hoangsvit",
                    )
                popen.assert_not_called()

    async def test_play_subscriptions_link_is_visible_and_opens_on_request(self):
        from textual.widgets import Link
        from tui import GoogleAITUI

        url = "https://play.google.com/store/account/subscriptions"
        for size in ((58, 20), (90, 20), (110, 35)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch.object(app, "open_url") as open_url:
                    async with app.run_test(size=size) as pilot:
                        await pilot.pause()
                        link = app.query_one("#play_subscriptions", Link)
                        support = app.query_one("#support_link", Link)
                        self.assertEqual(link.url, url)
                        self.assertGreaterEqual(link.region.x, support.region.right)
                        self.assertLessEqual(link.region.right, size[0])
                        self.assertGreaterEqual(link.region.width, len(link.text))
                        open_url.assert_not_called()
                        link.focus()
                        await pilot.press("enter")
                        open_url.assert_called_once_with(url)
                        open_url.reset_mock()
                        self.assertTrue(await pilot.click("#play_subscriptions"))
                        open_url.assert_called_once_with(url)

    async def test_tui_loads_without_starting_any_checkout(self):
        from textual.widgets import Button, Select, Static
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory), selected_step=3)
            with patch("tui.subprocess.Popen") as popen:
                async with app.run_test(size=(110, 35)) as pilot:
                    self.assertEqual(app.query_one("#step", Select).value, 3)
                    self.assertIn("Ready", str(app.query_one("#state", Static).render()))
                    self.assertTrue(app.query_one("#next", Button).disabled)
                    await pilot.press("d")
                    self.assertTrue(app.debug_visible)
                popen.assert_not_called()

    async def test_first_run_shows_clear_workflow_mode(self):
        from textual.widgets import Button, Select, Static
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch("tui.subprocess.Popen") as popen:
                async with app.run_test(size=(90, 20)) as pilot:
                    self.assertFalse(app.query_one("#workflow_actions").display)
                    self.assertTrue(app.query_one("#quickstart", Button).display)
                    self.assertEqual(app.query_one("#mode", Select).value, "single")
                    self.assertEqual(app.query_one("#step", Select).value, 1)
                    self.assertFalse(app.query_one("#stop", Button).display)
                    self.assertFalse(app.query_one("#next", Button).display)
                    self.assertIn("Run this step", str(app.query_one("#run", Button).label))
                    app.query_one("#mode", Select).value = "all"
                    # Select.Changed can be queued behind layout work on Windows.
                    # Wait for the event rather than asserting after one idle tick.
                    for _ in range(20):
                        if app.query_one("#step", Select).disabled:
                            break
                        await pilot.pause(0.05)
                    self.assertTrue(app.query_one("#step", Select).disabled)
                    self.assertEqual(str(app.query_one("#run", Button).label), "Step 1 check required")
                    self.assertTrue(app.query_one("#run", Button).disabled)
                popen.assert_not_called()

    async def test_run_controls_use_wide_content_not_sidebar(self):
        from textual.widgets import Button, Select
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch("tui.subprocess.Popen") as popen:
                async with app.run_test(size=(110, 35)) as pilot:
                    await pilot.pause()
                    app.advanced_pressed()
                    app.toggle_more_modes()
                    await pilot.pause()
                    sidebar = app.query_one("#controls").region
                    for selector in ("#mode", "#step", "#run"):
                        widget = app.query_one(selector)
                        self.assertGreaterEqual(widget.region.x, sidebar.right)
                        self.assertGreater(widget.region.width, 15)
                    self.assertTrue(app.query_one("#run", Button).display)
                    self.assertTrue(app.query_one("#quickstart", Button).display)
                    self.assertEqual(app.query_one("#mode", Select).value, "single")
                popen.assert_not_called()

    async def test_compact_run_controls_remain_visible(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(90, 20)) as pilot:
                await pilot.pause()
                self.assertTrue(app.query_one("#quickstart").display)
                self.assertFalse(app.query_one("#workflow_actions").display)
                self.assertGreater(app.query_one("#quickstart").region.width, 15)
                self.assertGreater(app.query_one("#status_panel").region.height, 3)

    async def test_all_and_from_modes_route_to_expected_step(self):
        from textual.widgets import Select
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "_confirm_stage") as confirm:
                async with app.run_test(size=(110, 35)) as pilot:
                    app.query_one("#mode", Select).value = "all"
                    await pilot.pause()
                    app.selected_pressed()
                    confirm.assert_called_with(2, True)
                    app.query_one("#mode", Select).value = "from"
                    app.query_one("#step", Select).value = 4
                    await pilot.pause()
                    app.selected_pressed()
                    confirm.assert_called_with(4, True)
                    app.query_one("#mode", Select).value = "single"
                    await pilot.pause()
                    app.selected_pressed()
                    confirm.assert_called_with(4, False)

    async def test_new_run_clears_stale_debug_and_device_account_cards(self):
        from textual.widgets import Button, RichLog, Static
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage"):
                async with app.run_test(size=(110, 35)) as pilot:
                    app._received("Account alice@example.com")
                    app._received("Device emulator-5554")
                    app.action_toggle_debug()
                    await pilot.pause()
                    self.assertEqual(len(app.query_one("#debug_log", RichLog).lines), 2)
                    app._start(1, False)
                    await pilot.pause()
                    self.assertFalse(app._last_output)
                    self.assertFalse(app._run_output)
                    self.assertEqual(len(app.query_one("#debug_log", RichLog).lines), 0)
                    self.assertIn("Checking…", str(app.query_one("#account", Static).render()))
                    self.assertNotIn("al***", str(app.query_one("#account", Static).render()))
                    self.assertIn("Auto-detect", str(app.query_one("#device", Static).render()))
                    self.assertFalse(app.query_one("#manual", Button).display)

    async def test_step_one_keeps_masked_account_hint_and_drops_it_on_device_change(self):
        from device_diagnostics import ConnectionStatus
        from textual.widgets import Static
        from tui import GoogleAITUI
        from tui_core import mask_email

        for device_changed in (False, True):
            with self.subTest(device_changed=device_changed), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=(110, 35)) as pilot:
                    serial = "emulator-5554"
                    account = "fixture@example.com"
                    app._connection_state = ConnectionStatus("connected", (serial,))
                    app._display_account_candidates([account], serial)
                    with patch.object(app, "run_stage") as run:
                        self.assertTrue(await pilot.click("#quickstart"))
                    run.assert_called_once_with(1)
                    card = app.query_one("#account", Static)
                    self.assertIn(mask_email(account), str(card.render()))
                    self.assertIn("Checking", str(card.render()))
                    self.assertNotIn(account, str(card.render()))
                    self.assertIsNone(app._verified_account)
                    app._received("Device " + ("emulator-5556" if device_changed else serial))
                    app._finished(1, Outcome("listed", "Offers listed", "Review offers."), {"offers": []})
                    self.assertEqual(mask_email(account) in str(card.render()), not device_changed)
                    self.assertIn("Play unverified", str(card.render()))
                    self.assertFalse(app._offer_check_ready)

    async def test_debug_reopen_includes_hidden_lines_without_duplicates(self):
        from textual.widgets import RichLog
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                app._received("ADB first line")
                app.action_toggle_debug()
                await pilot.pause()
                self.assertEqual(len(app.query_one("#debug_log", RichLog).lines), 1)
                app.action_toggle_debug()  # Hide technical details
                app._received("ADB second line")
                app.action_toggle_debug()  # Reopen with the full current-run buffer
                await pilot.pause()
                self.assertEqual(len(app.query_one("#debug_log", RichLog).lines), 2)

    async def test_verified_account_captured_only_from_structured_status(self):
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            with patch("tui.sys.platform", "win32"):
                app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage"):
                async with app.run_test(size=(110, 35)):
                    app._received("Message about Account other@example.com")
                    self.assertIsNone(app._verified_account)
                    app._received("  Account      Alice@Example.com")
                    self.assertEqual(app._verified_account, "alice@example.com")
                    from device_diagnostics import ConnectionStatus
                    app._offer_check_ready = True
                    app._offer_ready_device = "emulator-5554"
                    app._connection_state = ConnectionStatus("connected", ("emulator-5554",))
                    app._start(3, True)
                    self.assertIsNone(app._verified_account)

    async def test_busy_state_locks_run_controls_but_keeps_help_available(self):
        from textual.widgets import Button, Select
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage"):
                async with app.run_test(size=(110, 35)) as pilot:
                    app._start(1, False)
                    self.assertTrue(app.query_one("#run", Button).disabled)
                    self.assertTrue(app.query_one("#mode", Select).disabled)
                    self.assertTrue(app.query_one("#step", Select).disabled)
                    self.assertTrue(app.query_one("#quickstart", Button).disabled)
                    self.assertFalse(app.query_one("#nav_help", Button).disabled)
                    self.assertFalse(app.query_one("#debug", Button).disabled)
                    self.assertTrue(app.query_one("#stop", Button).display)

    async def test_stop_is_real_only_for_read_only_checks(self):
        from tui import GoogleAITUI
        from textual.widgets import Button
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "terminate_readonly_child") as stop:
                async with app.run_test(size=(110, 35)):
                    app.busy = True
                    app.current_step = 1
                    app.stop_pressed()
                    self.assertTrue(app._cancel_requested)
                    stop.assert_called_once()
                    app._cancel_requested = False
                    app.current_step = 3
                    app.stop_pressed()
                    self.assertTrue(app._stop_after_step)
                    self.assertFalse(app._cancel_requested)
                    button = app.query_one("#stop", Button)
                    self.assertTrue(button.disabled)
                    self.assertIn("Stop queued", str(button.label))

    async def test_quit_during_checkout_queues_exit_without_killing_process(self):
        from tui import GoogleAITUI
        from textual.widgets import Button
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "terminate_readonly_child") as stop:
                async with app.run_test(size=(110, 35)):
                    app.busy = True
                    app.current_step = 3
                    app.action_quit_safely()
                    self.assertTrue(app._exit_after_step)
                    self.assertTrue(app._stop_after_step)
                    self.assertFalse(app._cancel_requested)
                    self.assertTrue(app.query_one("#exit", Button).disabled)
                    self.assertIn("Exit queued", str(app.query_one("#stop", Button).label))
                    stop.assert_not_called()

    async def test_checkout_review_marker_keeps_stage_busy(self):
        from tui import GoogleAITUI
        from textual.widgets import Button, Static
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)):
                app.busy = True
                app.current_step = 3
                app._received("EPLUS_CHECKOUT_REVIEW:unconfirmed")
                self.assertIn("could not confirm", str(app.query_one("#activity", Static).render()))
                self.assertTrue(app.busy)
                self.assertTrue(app.query_one("#next", Button).disabled)

    async def test_startup_probe_displays_masked_account_without_approval(self):
        from device_diagnostics import ConnectionStatus
        from tui import GoogleAITUI
        from textual.widgets import Static
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory), startup_probe=True)
            with patch.object(app, "discover_account_candidates") as discover:
                async with app.run_test(size=(110, 35)) as pilot:
                    await pilot.pause()
                    app._poll_connection.assert_called_once_with(startup=True)
                    device = ConnectionStatus("connected", ("fixture-device",))
                    app._connection_polled(device, app._connection_generation, True)
                    discover.assert_called_once_with("fixture-device", app._connection_generation)
                    app._show_detected_accounts("fixture-device", app._connection_generation,
                                                ["fixture@example.test"])
                    self.assertIn("ADB", str(app.query_one("#device", Static).render()))
                    label = str(app.query_one("#account", Static).render())
                    self.assertIn("Play unverified", label)
                    self.assertNotIn("fixture@example.test", label)
                    self.assertFalse(app._offer_check_ready)

    async def test_startup_account_probe_skips_ambiguous_transports(self):
        from device_diagnostics import ConnectionStatus
        from tui import GoogleAITUI
        from textual.widgets import Static
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory), startup_probe=True)
            with patch.object(app, "discover_account_candidates") as discover, patch.object(app, "_poll_connection"):
                async with app.run_test(size=(110, 35)):
                    app._connection_polled(ConnectionStatus("connected", ("fixture-a", "fixture-b")),
                                           app._connection_generation, True)
                    discover.assert_not_called()
                    self.assertIn("device not resolved", str(app.query_one("#account", Static).render()))
                    self.assertFalse(app._offer_check_ready)

    async def test_reconnect_invalidates_old_account_result(self):
        from device_diagnostics import ConnectionStatus
        from tui import GoogleAITUI
        from textual.widgets import Static
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory), startup_probe=True)
            with patch.object(app, "discover_account_candidates"), patch.object(app, "_poll_connection"):
                async with app.run_test(size=(110, 35)):
                    connected = ConnectionStatus("connected", ("fixture-device",))
                    app._connection_polled(connected, app._connection_generation, True)
                    old = app._connection_generation
                    app._connection_polled(ConnectionStatus("disconnected"), old, True)
                    app._connection_polled(connected, app._connection_generation, True)
                    app._show_detected_accounts("fixture-device", old, ["old@example.test"])
                    label = str(app.query_one("#account", Static).render())
                    self.assertNotIn("Play unverified", label)
                    app._show_detected_accounts("fixture-device", app._connection_generation, ["new@example.test"])
                    self.assertIn("Play unverified", str(app.query_one("#account", Static).render()))

    async def test_automatic_account_failure_differs_from_empty_result(self):
        from device_diagnostics import ConnectionStatus
        from tui import GoogleAITUI
        from textual.widgets import Static
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)):
                app._connection_state = ConnectionStatus("connected", ("fixture-device",))
                app._show_detected_accounts("fixture-device", app._connection_generation, None)
                self.assertIn("Lookup unavailable", str(app.query_one("#account", Static).render()))
                app._show_detected_accounts("fixture-device", app._connection_generation, [])
                self.assertIn("No Android account detected", str(app.query_one("#account", Static).render()))

    async def test_late_manual_account_lookup_does_not_interrupt_sku_scan(self):
        from tui import GoogleAITUI
        from textual.widgets import Button, Static
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)):
                app._sku_pending = True
                app._accounts_loading = True
                original = app.screen
                status = str(app.query_one("#state", Static).render())
                app._account_candidates_loaded(["fixture@example.invalid"], "fixture-device")
                self.assertFalse(app._accounts_loading)
                self.assertTrue(app.query_one("#choose_account", Button).disabled)
                self.assertIs(app.screen, original)
                self.assertEqual(str(app.query_one("#state", Static).render()), status)

    async def test_account_picker_updates_card_before_selection(self):
        from tui import AccountPicker, GoogleAITUI
        from textual.widgets import Static
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                app._account_candidates_loaded(["fixture@example.test"], "fixture-device")
                await pilot.pause()
                self.assertIsInstance(app.screen, AccountPicker)
                label = str(app.screen_stack[0].query_one("#account", Static).render())
                self.assertIn("Play unverified", label)
                self.assertNotIn("fixture@example.test", label)
                app.screen.dismiss(None)
                await pilot.pause()
                self.assertIsNone(app._selected_account)
                self.assertFalse(app._offer_check_ready)

    async def test_quit_during_readonly_requests_stop(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "terminate_readonly_child") as stop:
                async with app.run_test(size=(110, 35)):
                    app.busy = True
                    app.current_step = 0
                    app.action_quit_safely()
                    self.assertTrue(app._exit_after_step)
                    self.assertTrue(app._cancel_requested)
                    stop.assert_called_once()

    async def test_quick_check_starts_readonly_step_without_approval(self):
        from textual.widgets import Button
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "_confirm_stage") as confirm:
                async with app.run_test(size=(110, 35)) as pilot:
                    await pilot.click("#quickstart")
                    await pilot.pause()
                    confirm.assert_called_once_with(1, False)
                    self.assertFalse(app.query_one("#workflow_actions").display)
                    self.assertTrue(app.query_one("#status_panel").display)

    async def test_advanced_controls_are_explicitly_opt_in(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                self.assertFalse(app.query_one("#workflow_actions").display)
                await pilot.click("#advanced_toggle")
                await pilot.pause()
                self.assertTrue(app.query_one("#workflow_actions").display)
                app.advanced_pressed()
                self.assertFalse(app.query_one("#workflow_actions").display)

    async def test_welcome_keeps_checkout_notice_out_of_the_read_only_view(self):
        from tui import GoogleAITUI

        for size in ((110, 35), (90, 20)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch("tui.subprocess.Popen") as launch:
                    async with app.run_test(size=size) as pilot:
                        await pilot.pause()
                        self.assertFalse(app.query("#payment_notice, #payment_notice_compact"))
                        self.assertGreater(app.query_one("#status_panel").region.height, 3)
                        self.assertTrue(app.query_one("#quickstart").display)
                    launch.assert_not_called()

    async def test_start_mumu_popup_restores_controls_on_failure(self):
        from tui import ConnectionNotice, GoogleAITUI
        from textual.widgets import Button, Static
        from mumu_remote import MuMuError
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                notice = ConnectionNotice("Disconnected", "Retry the connection.")
                with patch("tui.sys.platform", "win32"):
                    app.push_screen(notice)
                    await pilot.pause()
                with patch("device_diagnostics.locate_adb", return_value="adb"), \
                     patch("mumu_remote.connect_existing_instance", side_effect=MuMuError("Choose an existing instance.")):
                    notice.start_mumu()
                    for control in ("#connection_start_mumu", "#connection_retry", "#notice_close"):
                        self.assertTrue(notice.query_one(control, Button).disabled)
                    for _ in range(50):
                        await pilot.pause(0.02)
                        if notice._retry_started is None:
                            break
                self.assertIsNone(notice._retry_started)
                for control in ("#connection_start_mumu", "#connection_retry", "#notice_close"):
                    self.assertFalse(notice.query_one(control, Button).disabled)
                self.assertIn("Choose an existing instance.", str(notice.query_one("#connection_instruction", Static).render()))
                self.assertFalse(app._offer_check_ready)

    async def test_connection_popup_retry_shows_timer_and_recovers(self):
        from tui import ConnectionNotice, GoogleAITUI
        from device_diagnostics import ConnectionStatus
        from textual.widgets import Button

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(90, 20)) as pilot:
                notice = ConnectionNotice("Disconnected", "Retry the connection.")
                app.push_screen(notice)
                await pilot.pause()
                with patch.object(notice, "_retry_connection_worker") as worker:
                    retry = notice.query_one("#connection_retry", Button)
                    close = notice.query_one("#notice_close", Button)
                    self.assertEqual(retry.region.y, close.region.y)
                    self.assertLessEqual(abs(retry.region.width - close.region.width), 1)
                    notice.retry_connection()
                    self.assertTrue(notice.query_one("#connection_retry", Button).disabled)
                    self.assertEqual(str(notice.query_one("#connection_retry", Button).label), "Retrying… 0s")
                    notice.retry_connection()
                    worker.assert_called_once()
                notice._retry_finished(ConnectionStatus("disconnected"))
                self.assertFalse(notice.query_one("#connection_retry", Button).disabled)
                notice._retry_finished(ConnectionStatus("connected", ("emulator-5554",)))
                await pilot.pause()
                self.assertNotIsInstance(app.screen, ConnectionNotice)

    async def test_paid_selection_without_fresh_check_offers_step_one_action(self):
        from tui import GoogleAITUI
        from textual.widgets import Button, Select

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(90, 20)) as pilot:
                app.query_one("#step", Select).value = 2
                for _ in range(20):
                    if app.query_one("#refresh_offers", Button).display:
                        break
                    await pilot.pause(0.05)
                self.assertTrue(app.query_one("#refresh_offers", Button).display)
                self.assertTrue(app.query_one("#run", Button).disabled)
                with patch.object(app, "_confirm_stage") as confirm:
                    app.refresh_offers_pressed()
                confirm.assert_called_once_with(1, False)
                app._offer_check_ready = True
                app._update_run_mode()
                self.assertFalse(app.query_one("#refresh_offers", Button).display)

    async def test_reload_restarts_idle_dashboard_and_is_blocked_during_stage(self):
        from tui import GoogleAITUI
        from textual.widgets import Button
        import sys

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(90, 20)):
                with patch("tui.os.execv") as restart:
                    app.reload_pressed()
                    restart.assert_called_once_with(
                        sys.executable, [sys.executable, str(app.repo / "tui.py")])
                    restart.reset_mock()
                    with patch.object(app, "run_stage"):
                        app._start(1, False)
                    self.assertTrue(app.query_one("#reload", Button).disabled)
                    app.reload_pressed()
                    restart.assert_not_called()

    async def test_environment_tick_requires_completion_marker_in_current_run(self):
        from tui import GoogleAITUI
        from textual.widgets import Static

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(90, 20)):
                app._received("EPLUS_STAGE_DONE:0")
                self.assertNotIn("✓", app.query_one("#stage_0", Static).render().plain)
                with patch.object(app, "run_stage"):
                    app._start(1, False)
                app._received("Device emulator-5554")
                self.assertNotIn("✓", app.query_one("#stage_0", Static).render().plain)
                app._received("EPLUS_STAGE_DONE:0")
                self.assertIn("✓", app.query_one("#stage_0", Static).render().plain)
                self.assertIn("●", app.query_one("#stage_1", Static).render().plain)

    async def test_startup_restores_attempted_steps_without_unlocking_checkout(self):
        from tui import GoogleAITUI
        from stage_history import record_history
        from textual.widgets import Static

        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            record_history(repo, "selected@example.com", 2, "checkout_requested")
            app = GoogleAITUI(repo=repo)
            async with app.run_test(size=(90, 20)):
                self.assertIn("↺", app.query_one("#stage_2", Static).render().plain)
                self.assertIn("Step 2", app.query_one("#history", Static).render().plain)
                self.assertFalse(app._offer_check_ready)
                self.assertIsNone(app._verified_account)

    async def test_account_history_survives_restart_without_unlocking_paid_steps(self):
        from tui import GoogleAITUI
        from stage_history import record_history
        from textual.widgets import Static

        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            record_history(repo, "selected@example.com", 2, "checkout_requested")
            app = GoogleAITUI(repo=repo)
            async with app.run_test(size=(90, 20)):
                app._account_chosen("selected@example.com")
                history = app.query_one("#history", Static).render().plain
                self.assertIn("Step 2", history)
                self.assertIn("verify in Google Play", history)
                self.assertFalse(app._offer_check_ready)
                app._account_chosen("other@example.com")
                self.assertNotIn("Step 2", app.query_one("#history", Static).render().plain)

    async def test_paid_stage_button_shows_running_step_and_elapsed_seconds(self):
        from tui import GoogleAITUI
        from textual.widgets import Button
        from tui_core import Outcome

        for step in range(2, 5):
            with self.subTest(step=step), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=(90, 20)):
                    with patch.object(app, "run_stage") as run:
                        from device_diagnostics import ConnectionStatus
                        app._offer_check_ready = True
                        app._offer_ready_device = "emulator-5554"
                        app._connection_state = ConnectionStatus("connected", ("emulator-5554",))
                        app._start(step, False)
                        button = app.query_one("#quickstart", Button)
                        self.assertTrue(button.disabled)
                        self.assertTrue(button.display)
                        self.assertTrue(button.has_class("checking"))
                        self.assertEqual(str(button.label), f"Running Step {step}… 0s")
                        run_button = app.query_one("#run", Button)
                        self.assertEqual(str(run_button.label), f"Running Step {step}… 0s")
                        self.assertTrue(run_button.has_class("checking"))
                        with patch("tui.time.monotonic", return_value=app._started_at + 92.5):
                            app._refresh_elapsed()
                        self.assertEqual(str(button.label), f"Running Step {step}… 92s")
                        self.assertEqual(str(run_button.label), f"Running Step {step}… 92s")
                        app.quickstart_pressed()
                        run.assert_called_once_with(step)
                    app._finished(step, Outcome("cancelled", "Stopped", ""), None)
                    self.assertFalse(button.has_class("checking"))
                    self.assertNotIn("Running Step", str(button.label))
                    self.assertFalse(run_button.has_class("checking"))
                    self.assertNotIn("Running Step", str(run_button.label))

    async def test_account_choice_is_next_to_account_and_locked_during_stage(self):
        from tui import GoogleAITUI
        from textual.widgets import Button

        for size in ((90, 20), (110, 35)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=size) as pilot:
                    await pilot.pause()
                    button = app.query_one("#choose_account", Button)
                    account = app.query_one("#account")
                    self.assertEqual(button.region.y, account.region.y)
                    self.assertGreaterEqual(button.region.x, account.region.right)
                    self.assertLessEqual(button.region.right, size[0])
                    with patch.object(app, "run_stage"):
                        app._start(1, False)
                    self.assertTrue(button.disabled)

    async def test_live_status_uses_remaining_height_after_actions(self):
        from tui import GoogleAITUI

        for size in ((90, 20), (110, 35), (150, 45)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=size) as pilot:
                    await pilot.pause()
                    welcome = app.query_one("#welcome_panel")
                    status = app.query_one("#status_panel")
                    self.assertLessEqual(welcome.region.height, 11)
                    self.assertGreaterEqual(status.region.height, 5)
                    if size[1] >= 35:
                        self.assertGreater(status.region.height, welcome.region.height)
                    app.advanced_pressed()
                    await pilot.pause()
                    self.assertGreaterEqual(status.region.height, 5)
                    self.assertTrue(app.query_one("#workflow_actions").display)

    async def test_live_status_shows_latest_activity_above_other_details(self):
        from textual.widgets import Static
        from tui import GoogleAITUI

        for size in ((90, 20), (110, 35)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=size) as pilot:
                    app._received("Preparing Frida")
                    app._received("Querying offers")
                    await pilot.pause()
                    activity = app.query_one("#activity", Static)
                    self.assertEqual(activity.render().plain, "Checking available offers...")
                    self.assertLess(activity.region.y, app.query_one("#state").region.y)
                    self.assertLess(activity.region.y, app.query_one("#elapsed").region.y)
                    self.assertLess(activity.region.y, app.query_one("#status_panel").content_region.bottom)

    async def test_technical_log_reveals_and_follows_latest_output(self):
        from textual.widgets import RichLog
        from tui import GoogleAITUI

        for size in ((90, 20), (110, 35)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=size) as pilot:
                    for number in range(40):
                        app._received(f"Log line {number}")
                    app.action_toggle_debug()
                    await pilot.pause(0.2)
                    log = app.query_one("#debug_log", RichLog)
                    results = app.query_one("#results")
                    # A busy runner may need a few refresh cycles to measure the
                    # newly visible RichLog. Keep a bounded real scroll assertion.
                    for _ in range(12):
                        if log.max_scroll_y > 0 and log.scroll_y == log.max_scroll_y:
                            break
                        await pilot.pause(0.05)
                    self.assertGreater(log.max_scroll_y, 0)
                    self.assertEqual(log.scroll_y, log.max_scroll_y)
                    self.assertGreaterEqual(results.content_region.bottom, log.region.bottom)
                    self.assertIn("Log line 39", log.lines[-1].text)
                    log.scroll_home(animate=False, immediate=True)
                    app._received("Newest log line")
                    await pilot.pause(0.2)
                    self.assertEqual(log.scroll_y, log.max_scroll_y)
                    self.assertIn("Newest log line", log.lines[-1].text)

    async def test_quick_check_shows_elapsed_seconds_while_disabled(self):
        from textual.widgets import Button
        from tui import GoogleAITUI
        from tui_core import Outcome

        for size in ((90, 20), (110, 35)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=size) as pilot:
                    button = app.query_one("#quickstart", Button)
                    with patch.object(app, "run_stage") as run_stage:
                        app._start(1, False)
                        self.assertTrue(button.disabled)
                        self.assertEqual(str(button.label), "Checking offers… 0s")
                        with patch("tui.time.monotonic", return_value=app._started_at + 42.5):
                            app._refresh_elapsed()
                        self.assertEqual(str(button.label), "Checking offers… 42s")
                        await pilot.click("#quickstart")
                        run_stage.assert_called_once_with(1)
                    app._finished(1, Outcome("cancelled", "Check stopped", ""), None)
                    self.assertFalse(button.disabled)
                    self.assertFalse(button.has_class("checking"))
                    self.assertEqual(str(button.label), "Check Device & Offers")

    async def test_android_details_are_visible_and_reset_on_new_check(self):
        from textual.widgets import Static
        from tui import GoogleAITUI

        for size in ((90, 20), (110, 35)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=size) as pilot:
                    card = app.query_one("#device", Static)
                    app._received("  Device      emulator-5554")
                    app._received("  Android     12 (SDK 31), ABI x86_64")
                    await pilot.pause()
                    self.assertIn("Android 12 · SDK 31 · x86_64", card.render().plain)
                    self.assertEqual(card.tooltip, "Android 12 · SDK 31 · x86_64")
                    self.assertGreaterEqual(card.content_region.width, len("Android 12 · SDK 31 · x86_64"))
                    with patch.object(app, "run_stage"):
                        app._start(1, False)
                    self.assertIsNone(card.tooltip)
                    self.assertNotIn("Android 12", card.render().plain)
                    app._received("Device emulator-5556")
                    self.assertEqual(card.tooltip, "Android connected (ADB)")

    async def test_checkout_confirmations_explain_each_one_dollar_event(self):
        from textual.widgets import Static
        from tui import Approval, GoogleAITUI

        for step, expected in ((2, "1"), (3, "2"), (4, "3"), (5, None)):
            with self.subTest(step=step), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch("tui.subprocess.Popen") as launch:
                    async with app.run_test(size=(110, 35)) as pilot:
                        app._offer_check_ready = True
                        if step == 5:
                            from offer_discovery import ExtraOffer
                            app._update_discovered([
                                ExtraOffer("g1.2tb.ai.subs_variant",
                                           "6months-eft-ss-2026", price_micros="0", source="step1")
                            ])
                        app._confirm_stage(step, False)
                        await pilot.pause()
                        self.assertIsInstance(app.screen, Approval)
                        wording = str(app.screen.query_one("#approval_message", Static).render())
                        if expected:
                            self.assertIn("Card check " + expected + " of 3", wording)
                            self.assertIn("NOT one US$3 payment", wording)
                            self.assertIn("temporary hold", wording)
                            self.assertIn("not guaranteed", wording)
                        else:
                            self.assertIn("Step 5 is optional", wording)
                            self.assertIn("outside the 3 x US$1", wording)
                        await pilot.click("#cancel")
                        await pilot.pause()
                    launch.assert_not_called()

    async def test_step_click_requires_approval_before_subprocess(self):
        from tui import GoogleAITUI, Approval

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory), selected_step=3)
            with patch("tui.subprocess.Popen") as popen:
                async with app.run_test(size=(110, 35)) as pilot:
                    app._offer_check_ready = True
                    app._update_run_mode()
                    await pilot.click("#advanced_toggle")
                    await pilot.pause()
                    await pilot.click("#run")
                    await pilot.pause()
                    self.assertIsInstance(app.screen, Approval)
                    await pilot.click("#cancel")
                    await pilot.pause()
                    popen.assert_not_called()

    async def test_paid_steps_blocked_until_fresh_verified_offer_check(self):
        from textual.widgets import Button, Select
        from tui import GoogleAITUI, Approval
        from tui_core import Outcome

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory), selected_step=2)
            with patch.object(GoogleAITUI, "run_stage") as run:
                async with app.run_test(size=(110, 35)) as pilot:
                    app._update_run_mode()
                    self.assertTrue(app.query_one("#run", Button).disabled)
                    app.action_run_selected()
                    app.query_one("#mode", Select).value = "all"
                    app.selected_pressed()
                    app.query_one("#mode", Select).value = "from"
                    app.selected_pressed()
                    app.sequence_pressed()
                    app._start(2, False)
                    self.assertFalse(app.busy)
                    self.assertNotIsInstance(app.screen, Approval)
                    run.assert_not_called()
                    app.query_one("#mode", Select).value = "single"

                    app._received("Device emulator-5554")
                    app._verified_account = "test@example.com"
                    report = {"status": "listed", "offers": [{"id": "test"}],
                              "detected_play_account": "test@example.com"}
                    app._finished(1, Outcome("listed", "Offers loaded", "Review offers"), report)
                    self.assertFalse(app.query_one("#run", Button).disabled)
                    app._confirm_stage(2, False)
                    await pilot.pause()
                    self.assertIsInstance(app.screen, Approval)
                    await pilot.click("#cancel")
                    await pilot.pause()
                    app._finished(1, Outcome("tool_error", "Failed", "Retry"), None)
                    self.assertTrue(app.query_one("#run", Button).disabled)
                    self.assertFalse(app._offer_check_ready)

    async def test_offer_check_without_verified_matching_account_stays_locked(self):
        from tui import GoogleAITUI
        from tui_core import Outcome
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)):
                app._verified_account = "first@example.com"
                app._finished(1, Outcome("listed", "Offers loaded", "Review"),
                              {"offers": [{"id": "test"}], "detected_play_account": "other@example.com"})
                self.assertFalse(app._offer_check_ready)

    async def test_success_prompts_next_but_requires_separate_checkout_approval(self):
        from textual.widgets import Button
        from tui import GoogleAITUI, Approval, CheckComplete
        from tui_core import Outcome
        for size in ((110, 35), (90, 20)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch.object(GoogleAITUI, "run_stage") as run:
                    async with app.run_test(size=size) as pilot:
                        app._received("Device emulator-5554")
                        app._verified_account = "test@example.com"
                        app._finished(1, Outcome("listed", "Offers loaded", "Review"), {
                            "offers": [{"id": "12months-eft", "micros": "0"}],
                            "detected_play_account": "test@example.com"})
                        await pilot.pause()
                        self.assertIsInstance(app.screen, CheckComplete)
                        run.assert_not_called()
                        await pilot.click("#check_continue")
                        await pilot.pause()
                        self.assertIsInstance(app.screen, Approval)
                        run.assert_not_called()
                        await pilot.click("#cancel")
                        await pilot.pause()
                        self.assertIn("Step 2", str(app.query_one("#quickstart", Button).label))

    async def test_local_launch_failure_shows_safe_cause_in_technical_details(self):
        from tui import GoogleAITUI
        from textual.widgets import RichLog

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(90, 20)) as pilot:
                app._record_internal_diagnostic(
                    safe_launch_diagnostic(FileNotFoundError(
                        "setup_env.py is missing from C:/Users/private@example.com"))
                )
                self.assertIn("Required toolkit file missing: setup_env.py", app._last_output[-1])
                self.assertNotIn("private@example.com", app._last_output[-1])
                self.assertFalse(app._run_output)
                app.action_toggle_debug()
                await pilot.pause()
                self.assertGreater(len(app.query_one("#debug_log", RichLog).lines), 0)

    async def test_cli_marker_is_never_shown_raw_in_debug_or_status(self):
        from textual.widgets import Static
        from tui import GoogleAITUI

        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(90, 20)) as pilot:
                app.action_toggle_debug()
                app._received("EPLUS_ISSUE:launch_failed")
                self.assertEqual(app._run_output[-1], "EPLUS_ISSUE:launch_failed")
                self.assertIn("Could not open Google Play checkout", app._last_output[-1])
                self.assertNotIn("EPLUS_ISSUE:", app._last_output[-1])
                result = outcome_for_stage(3, 0, {"status": "launch_failed"})
                with patch.object(app, "_set_status", wraps=app._set_status) as status, \
                     patch.object(app, "_set_message", wraps=app._set_message) as message:
                    app._finished(3, result, {"status": "launch_failed"})
                await pilot.pause()
                status.assert_called_with("Could not open Google Play checkout")
                shown_message = message.call_args.args[0]
                self.assertIn("Google Play", shown_message)
                self.assertNotIn("EPLUS_ISSUE:", shown_message)

    async def test_all_step_one_failures_show_actionable_notice(self):
        from tui import GoogleAITUI, SetupNotice
        from tui_core import Outcome

        for code in ("app_not_started", "activity_lookup_failed",
                     "missing_report", "tool_error", "exception", "unknown"):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=(90, 20)) as pilot:
                    app._finished(1, Outcome(code, "Cannot complete check",
                                            "Check Android setup and try the read-only check again."), None)
                    await pilot.pause()
                    self.assertIsInstance(app.screen, SetupNotice)
                    self.assertIn("Android", app.screen.instruction)
                    await pilot.click("#notice_close")

    async def test_setup_error_shows_actionable_notice(self):
        from tui import GoogleAITUI, SetupNotice
        from tui_core import cli_issue_outcome
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(90, 20)) as pilot:
                app._finished(1, cli_issue_outcome(["EPLUS_ISSUE:device_missing"], 1), None)
                await pilot.pause()
                self.assertIsInstance(app.screen, SetupNotice)
                self.assertIn("ADB", app.screen.instruction)
                await pilot.click("#notice_close")

    async def test_missing_app_notice_opens_play_only_after_button_press(self):
        from textual.widgets import Button, Static
        from tui import GoogleAITUI, MissingAppNotice
        from tui_core import cli_issue_outcome

        for size, launch_result, expected in (
            ((90, 20), "opened", "install or enable Google One"),
            ((110, 35), "store_unavailable", "Google Play is missing or disabled"),
        ):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=size) as pilot:
                    app._checked_device = "emulator-5554"
                    with patch("tui.open_google_one_listing", return_value=launch_result) as open_listing:
                        app._finished(1, cli_issue_outcome(["EPLUS_ISSUE:app_missing"], 1), None)
                        await pilot.pause()
                        self.assertIsInstance(app.screen, MissingAppNotice)
                        open_listing.assert_not_called()
                        self.assertTrue(await pilot.click("#open_google_play"))
                        await app.workers.wait_for_complete()
                    await pilot.pause()
                    open_listing.assert_called_once_with("emulator-5554")
                    self.assertIn(expected, str(app.screen.query_one("#app_notice_instruction", Static).render()))
                    self.assertEqual(app.screen.query_one("#open_google_play", Button).disabled,
                                     launch_result == "opened")
                    self.assertTrue(await pilot.click("#notice_close"))

    async def test_next_checkout_action_is_visible_outside_advanced(self):
        from textual.widgets import Button
        from tui import GoogleAITUI, Approval
        from tui_core import Outcome
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage") as run:
                async with app.run_test(size=(110, 35)) as pilot:
                    app._offer_check_ready = True
                    app.sequence = True
                    app.current_step = 2
                    app._finished(2, Outcome("checkout_requested", "Check Google Play", "Verify", True), {})
                    await pilot.pause()
                    self.assertFalse(app.query_one("#workflow_actions").display)
                    self.assertTrue(app.query_one("#next", Button).display)
                    await pilot.click("#next")
                    await pilot.pause()
                    self.assertIsInstance(app.screen, Approval)
                    run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
