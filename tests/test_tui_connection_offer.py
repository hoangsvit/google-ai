"""Mock-only regression tests for the TUI's new safe inspection actions."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from device_diagnostics import ConnectionDiagnosis
from tui_core import Outcome


class ConnectionAndOfferUITests(unittest.IsolatedAsyncioTestCase):
    async def test_diagnose_button_shows_guidance_without_checkout(self):
        from tui import GoogleAITUI
        from textual.widgets import Button, Static
        fake = ConnectionDiagnosis(
            "missing_adb", "ADB not found",
            ("Host: macOS Terminal", "Frida host: not installed"),
            "Install Android SDK Platform-Tools, then retry.",
        )
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch("tui.inspect_connection", return_value=fake), \
                 patch("tui.subprocess.Popen") as checkout:
                async with app.run_test(size=(110, 35)) as pilot:
                    self.assertTrue(app.query_one("#diagnose", Button).display)
                    await pilot.click("#diagnose")
                    for _ in range(30):
                        await pilot.pause(0.05)
                        if not app._diagnosing:
                            break
                    self.assertFalse(app._diagnosing)
                    self.assertIn("ADB not found", str(app.query_one("#state", Static).render()))
                    self.assertIn("macOS Terminal", str(app.query_one("#step_result", Static).render()))
                    self.assertFalse(app.busy)
                checkout.assert_not_called()

    async def test_offer_explorer_is_only_shown_after_fresh_listing(self):
        from tui import GoogleAITUI
        from textual.widgets import RichLog, Static
        report = {"status": "listed", "offers": [
            {"product": "g1.2tb.ai.subs_variant", "id": "12months-eft",
             "micros": "0", "period": "P1Y", "token": "MUST_NOT_SHOW"}
        ]}
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch("tui.subprocess.Popen") as checkout:
                async with app.run_test(size=(110, 35)) as pilot:
                    viewer = app.query_one("#offer_view", RichLog)
                    self.assertFalse(viewer.display)
                    app._finished(1, Outcome("listed", "Offers loaded", "Inspect manually."), report)
                    await pilot.pause()
                    self.assertFalse(viewer.display)
                    await pilot.click("#offers_toggle")
                    await pilot.pause()
                    self.assertTrue(viewer.display)
                    self.assertTrue(app.query_one("#offers_title", Static).display)
                    self.assertGreater(len(viewer.lines), 0)
                    self.assertFalse(app.query_one("#next").display)
                checkout.assert_not_called()

    async def test_new_run_hides_old_offer_details(self):
        from tui import GoogleAITUI
        from textual.widgets import RichLog
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage"):
                async with app.run_test(size=(110, 35)):
                    viewer = app.query_one("#offer_view", RichLog)
                    app._finished(1, Outcome("listed", "Offers loaded", "Check"), {
                        "status": "listed", "offers": [{"id": "eft-3mo", "micros": "0"}]})
                    app.offers_pressed()
                    self.assertTrue(viewer.display)
                    app._start(1, False)
                    self.assertFalse(viewer.display)
                    self.assertEqual(len(viewer.lines), 0)

    async def test_diagnosis_blocks_concurrent_paid_stage(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage") as paid:
                async with app.run_test(size=(110, 35)):
                    app._diagnosing = True
                    app._start(2, False)
                    self.assertFalse(app.busy)
                    paid.assert_not_called()


if __name__ == "__main__":
    unittest.main()
