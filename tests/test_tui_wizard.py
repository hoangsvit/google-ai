"""Offline guided-flow regressions: no emulator, account or billing access."""
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from tui_core import Outcome, initial_checkout_blocker


def listing(**changes):
    report = {"status": "listed", "detected_play_account": "owner@example.invalid",
              "offers": [{"id": "12months-eft", "micros": "0", "period": "P1Y"}]}
    report.update(changes)
    return report


LISTED = Outcome("listed", "Offers loaded", "Eligibility is not verified.")
REQUESTED = Outcome("checkout_requested", "Checkout submitted - not yet verified",
                    "Check Google Play before proceeding.", True)


class WizardReadinessTests(unittest.TestCase):
    def test_matching_listing_only_enables_a_navigation_action(self):
        self.assertEqual(initial_checkout_blocker(LISTED, listing()), "")
        self.assertEqual(initial_checkout_blocker(LISTED, listing(detected_play_account=""), "owner@example.invalid"), "")

    def test_failed_missing_or_malformed_results_cannot_offer_checkout(self):
        for outcome, report in (
            (Outcome("tool_error", "Failed", "Retry"), listing()),
            (LISTED, None), (LISTED, {}), (LISTED, listing(status="checkout_requested")),
            (LISTED, listing(offers=[])), (LISTED, listing(offers="invalid")),
            (LISTED, listing(offers=[None, {"id": "6months-eft", "micros": "0"}])),
            (LISTED, listing(offers=[{"id": "12months-eft", "micros": "1000000"}])),
            (LISTED, listing(offers=[{"id": "12months-eft", "micros": False}])),
            (LISTED, listing(detected_play_account="")),
            (LISTED, listing(detected_play_account="current@device")),
        ):
            with self.subTest(outcome=outcome.code, report=report):
                self.assertTrue(initial_checkout_blocker(outcome, report))

    def test_conflicting_accounts_block_without_exposing_them(self):
        message = initial_checkout_blocker(LISTED, listing(), "different@example.invalid")
        self.assertIn("differ", message)
        self.assertNotIn("@", message)


class WizardFlowTests(unittest.IsolatedAsyncioTestCase):
    async def test_elapsed_timer_is_safe_after_a_busy_screen_has_unmounted(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage"):
                async with app.run_test() as pilot:
                    app._start(1, False)
                    await pilot.pause()
                    app.exit()
                self.assertTrue(app.busy)
                app._refresh_elapsed()

    async def test_ready_action_and_status_fit_all_supported_terminal_sizes(self):
        from tui import GoogleAITUI
        for size in ((110, 35), (90, 20), (60, 20), (48, 20)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=size) as pilot:
                    app._finished(1, LISTED, listing())
                    await pilot.pause()
                    self.assertTrue(app._initial_ready)
                    for selector in ("#continue_initial", "#state", "#message", "#payment_notice_compact"):
                        region = app.query_one(selector).region
                        self.assertGreater(region.height, 0, selector)
                        self.assertLessEqual(region.bottom, size[1] - 1, selector)
                        self.assertLessEqual(region.right, size[0], selector)

    async def test_listing_waits_for_continue_and_separate_payment_approval(self):
        from tui import Approval, GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage") as engine:
                async with app.run_test() as pilot:
                    await pilot.click("#quickstart")
                    engine.assert_called_once_with(1)
                    app._finished(1, LISTED, listing())
                    await pilot.pause()
                    self.assertTrue(app._initial_ready)
                    self.assertTrue(app.query_one("#continue_initial").display)
                    self.assertFalse(app.query_one("#quickstart").display)
                    engine.assert_called_once_with(1)
                    await pilot.click("#continue_initial")
                    self.assertIsInstance(app.screen, Approval)
                    self.assertTrue(app._approval_pending)
                    engine.assert_called_once_with(1)
                    await pilot.press("escape")
                    await pilot.pause()
                    self.assertFalse(app._approval_pending)
                    self.assertFalse(app.busy)
                    await pilot.click("#continue_initial")
                    await pilot.pause()
                    self.assertIsInstance(app.screen, Approval)
                    self.assertTrue(await pilot.click("#approve"))
                    for _ in range(20):
                        await pilot.pause(0.05)
                        if app.busy:
                            break
                    self.assertTrue(app.busy)
                    self.assertTrue(app.sequence)
                    engine.assert_called_with(2)

    async def test_incomplete_checks_never_show_the_12_month_action(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage") as engine:
                async with app.run_test() as pilot:
                    for report in (None, listing(offers=[]), listing(detected_play_account="")):
                        app._finished(1, LISTED, report)
                        await pilot.pause()
                        self.assertFalse(app._initial_ready)
                        self.assertFalse(app.query_one("#continue_initial").display)
                        self.assertIn(app._wizard_blocker, str(app.query_one("#message").render()))
                        app.continue_initial_pressed()
                    engine.assert_not_called()

    async def test_stale_listing_from_a_previous_invocation_never_unlocks_continue(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            reports = repo / "ultra0-report"
            reports.mkdir()
            report = reports / "current.json"
            report.write_text(json.dumps(listing()), encoding="utf-8")
            os.utime(report, (time.time() - 60, time.time() - 60))
            app = GoogleAITUI(repo=repo)
            with patch("tui.needs_setup", return_value=False), \
                 patch("tui.command_for_step", return_value=["mock-engine"]), \
                 patch.object(GoogleAITUI, "_execute", return_value=0):
                async with app.run_test() as pilot:
                    app._start(1, False)
                    for _ in range(40):
                        await pilot.pause(0.05)
                        if not app.busy:
                            break
                    self.assertFalse(app.busy)
                    self.assertEqual(app._last_outcome.code, "missing_report")
                    self.assertFalse(app._initial_ready)
                    self.assertFalse(app.query_one("#continue_initial").display)

    async def test_every_later_checkout_waits_for_google_play_review_and_approval(self):
        from tui import Approval, GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage") as engine:
                async with app.run_test() as pilot:
                    app._start(2, True)
                    app._finished(2, REQUESTED, None)
                    await pilot.pause()
                    engine.assert_called_once_with(2)
                    self.assertTrue(app.query_one("#next").display)
                    self.assertTrue(app.query_one("#finish").display)
                    self.assertFalse(app.query_one("#quickstart").display)
                    app.advanced_pressed()
                    self.assertFalse(app.advanced_visible)
                    app._confirm_stage(4, True)
                    self.assertNotIsInstance(app.screen, Approval)
                    await pilot.click("#next")
                    self.assertIsInstance(app.screen, Approval)
                    message = str(app.screen.query_one("#approval_message").render())
                    self.assertIn("previous stage ACTUALLY changed", message)
                    engine.assert_called_once_with(2)
                    await pilot.click("#cancel")
                    await pilot.pause()
                    self.assertTrue(app.sequence)
                    self.assertTrue(app.query_one("#next").display)

    async def test_optional_step_can_be_declined_without_losing_the_result(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage") as engine:
                async with app.run_test() as pilot:
                    app._start(4, True)
                    app._finished(4, REQUESTED, None)
                    await pilot.pause()
                    self.assertIn("Step 5 is optional", str(app.query_one("#wizard_summary").render()))
                    await pilot.click("#finish")
                    await pilot.pause()
                    self.assertFalse(app.sequence)
                    self.assertFalse(app.query_one("#next").display)
                    self.assertIn("Sequence ended", str(app.query_one("#message").render()))
                    self.assertEqual(app._last_outcome.code, "checkout_requested")
                    app.next_pressed()
                    engine.assert_called_once_with(4)

    async def test_checkout_errors_never_advance_or_claim_completion(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage"):
                async with app.run_test() as pilot:
                    for code in ("missing_report", "already_subscribed", "payment_security_blocked", "checkout_not_confirmed"):
                        app._start(2, True)
                        app._finished(2, Outcome(code, "Review required", "Inspect Google Play."), None)
                        await pilot.pause()
                        self.assertFalse(app.sequence)
                        self.assertFalse(app.query_one("#next").display)
                        self.assertFalse(app._initial_ready)
                        self.assertNotIn("✓", str(app.query_one("#stage_2").render()))

    async def test_other_runs_and_connection_diagnostics_invalidate_previous_readiness(self):
        from tui import GoogleAITUI
        from device_diagnostics import ConnectionDiagnosis
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage"), patch.object(GoogleAITUI, "inspect_android_connection"):
                async with app.run_test() as pilot:
                    app._finished(1, LISTED, listing())
                    self.assertTrue(app._initial_ready)
                    app.diagnose_pressed()
                    self.assertFalse(app._initial_ready)
                    app.continue_initial_pressed()
                    self.assertFalse(app.busy)
                    app._diagnosis_done(ConnectionDiagnosis("connected", "Connection found", (), "Run an offer check."))
                    await pilot.pause()
                    self.assertFalse(app._initial_ready)
                    app._finished(1, LISTED, listing())
                    app._start(0, False)
                    self.assertFalse(app._initial_ready)

    async def test_advanced_is_a_separate_view_with_consistent_mode_choices(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "_confirm_stage") as confirm:
                async with app.run_test(size=(90, 20)) as pilot:
                    await pilot.pause()
                    advanced_x = app.query_one("#advanced_toggle").region.x
                    app._finished(1, LISTED, listing())
                    await pilot.pause()
                    self.assertEqual(app.query_one("#advanced_toggle").region.x, advanced_x)
                    app.action_run_selected()
                    app.selected_pressed()
                    confirm.assert_not_called()
                    await pilot.click("#advanced_toggle")
                    await pilot.pause()
                    self.assertTrue(app.advanced_visible)
                    self.assertEqual(app.query_one("#status_panel").region.height, 0)
                    self.assertFalse(app.query_one("#recheck").display)
                    self.assertFalse(app.query_one("#offers_toggle").display)
                    self.assertGreater(app.query_one("#run").region.height, 0)
                    app.query_one("#mode").value = "from"
                    for _ in range(30):
                        await pilot.pause()
                        if app.query_one("#step").value == 2:
                            break
                    self.assertEqual(app.query_one("#step").value, 2)
                    app.query_one("#step").value = 4
                    app.selected_pressed()
                    confirm.assert_called_with(4, True)
                    app.query_one("#mode").value = "all"
                    for _ in range(30):
                        await pilot.pause()
                        if app.query_one("#step").value == 2:
                            break
                    self.assertEqual(app.query_one("#step").value, 2)
                    self.assertFalse(app.query_one("#step_field").display)
                    app.selected_pressed()
                    confirm.assert_called_with(2, True)

    async def test_help_never_overwrites_a_result_or_verification_instruction(self):
        from tui import GoogleAITUI, HelpScreen
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage"):
                async with app.run_test() as pilot:
                    app._start(2, True)
                    app.help_pressed()
                    await pilot.pause()
                    self.assertIsInstance(app.screen, HelpScreen)
                    app._finished(2, REQUESTED, None)
                    before = str(app.query_one("#message").render())
                    await pilot.click("#close_help")
                    await pilot.pause()
                    self.assertEqual(str(app.query_one("#message").render()), before)
                    self.assertTrue(app.query_one("#next").display)


if __name__ == "__main__":
    unittest.main()
