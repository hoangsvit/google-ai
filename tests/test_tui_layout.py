"""Offline checks for the redesigned dashboard's visible controls and content."""
from pathlib import Path
from html import unescape
import re
import tempfile
import unittest
from unittest.mock import patch

from app_update import UpdateInfo
from tui_core import Outcome


def screen_text(app) -> str:
    """Visible terminal text in reading order, wrapped lines rejoined."""
    svg = unescape(app.export_screenshot()).replace("\xa0", " ")
    cells = re.findall(r'<text[^>]*\bx="([\d.]+)"[^>]*\by="([\d.]+)"[^>]*>([^<>]*)</text>', svg)
    rows: dict[float, list[tuple[float, str]]] = {}
    for x, y, text in cells:
        rows.setdefault(round(float(y)), []).append((float(x), text))
    lines = ["".join(text for _, text in sorted(parts)) for _, parts in sorted(rows.items())]
    plain = re.sub(r"[│─╭╮╰╯┌┐└┘▏▎▍▌▋▊▉█▆▅▄▔▁▂▃▇]+", " ", " ".join(lines))
    return " ".join(plain.split())


class DashboardLayoutTests(unittest.IsolatedAsyncioTestCase):
    async def test_idle_layout_shows_full_cards_warning_and_primary_controls(self):
        from tui import GoogleAITUI
        for size in ((110, 35), (90, 20), (60, 20), (48, 20)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch("tui.check_for_update", return_value=UpdateInfo("current", "Up to date · abcdef12")), \
                     patch.object(GoogleAITUI, "run_stage") as stage:
                    async with app.run_test(size=size) as pilot:
                        await pilot.pause()
                        for selector in ("#device", "#account"):
                            self.assertGreaterEqual(app.query_one(selector).content_region.height, 2)
                        for selector in ("#brand_title", "#quickstart", "#advanced_toggle",
                                         "#payment_notice_compact", "#state", "#message", "#elapsed",
                                         "#nav_help", "#diagnose", "#debug", "#exit", "#update"):
                            region = app.query_one(selector).region
                            self.assertGreater(region.height, 0, selector)
                            self.assertGreaterEqual(region.x, 0, selector)
                            self.assertLessEqual(region.right, size[0], selector)
                            self.assertLessEqual(region.bottom, size[1] - 1, selector)
                        welcome = app.query_one("#welcome_panel")
                        self.assertEqual(welcome.max_scroll_y, 0, "Default warning must not need scrolling")
                        primary = app.query_one("#quickstart")
                        advanced = app.query_one("#advanced_toggle")
                        self.assertEqual(str(advanced.label), "Advanced: Run by step →")
                        self.assertLessEqual(len(str(advanced.label)), advanced.content_region.width)
                        if size[0] >= 90:
                            self.assertEqual(primary.region.y, advanced.region.y)
                            self.assertEqual(primary.region.height, advanced.region.height)
                            self.assertGreaterEqual(advanced.region.x, primary.region.right)
                        else:
                            self.assertGreaterEqual(advanced.region.y, primary.region.bottom)
                            self.assertEqual(primary.region.width, advanced.region.width)
                        advanced.focus()
                        await pilot.pause()
                        self.assertIs(app.focused, advanced)
                        for button in (primary, advanced):
                            button.focus()
                            await pilot.pause()
                            rendered = unescape(app.export_screenshot()).replace("\xa0", " ")
                            self.assertIn(str(button.label), rendered, "Focused action text must remain visible")
                        self.assertFalse(app.ENABLE_COMMAND_PALETTE)
                        self.assertFalse(app.busy)
                        stage.assert_not_called()

    async def test_prominent_advanced_control_is_locked_during_active_work(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage"):
                async with app.run_test(size=(90, 20)) as pilot:
                    app._start(1, False)
                    await pilot.pause()
                    self.assertTrue(app.query_one("#advanced_toggle").disabled)
                    app.advanced_pressed()
                    self.assertFalse(app.advanced_visible)
                    app._finished(1, Outcome("listed", "Offers loaded", "Review account."), None)
                    await pilot.click("#advanced_toggle")
                    await pilot.pause()
                    self.assertTrue(app.advanced_visible)
                    back = app.query_one("#advanced_toggle")
                    self.assertGreater(back.region.height, 0)
                    self.assertLessEqual(back.region.bottom, 19)
                    await pilot.click("#advanced_toggle")
                    self.assertFalse(app.advanced_visible)

    async def test_toolbar_labels_fit_and_remain_accessible_by_keyboard(self):
        from tui import GoogleAITUI
        for size in ((110, 35), (90, 20), (60, 20), (48, 20)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                async with app.run_test(size=size) as pilot:
                    await pilot.pause()
                    for selector in ("#nav_help", "#diagnose", "#debug", "#exit", "#update"):
                        button = app.query_one(selector)
                        self.assertLessEqual(len(str(button.label)), button.content_region.width, selector)
                        button.focus()
                        await pilot.pause()
                        self.assertIs(app.focused, button)

    async def test_stop_and_next_are_visible_without_opening_advanced_settings(self):
        from tui import GoogleAITUI
        for size in ((110, 35), (90, 20), (60, 20)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch.object(GoogleAITUI, "run_stage"):
                    async with app.run_test(size=size) as pilot:
                        app._start(1, False)
                        await pilot.pause()
                        stop = app.query_one("#stop")
                        self.assertTrue(stop.display)
                        self.assertLessEqual(stop.region.bottom, app.query_one("#content").region.bottom)
                        self.assertFalse(app.query_one("#workflow_actions").display)
                        app._finished(1, Outcome("listed", "Offers loaded", "Review the account."), None)
                        app._start(2, True)
                        app._finished(2, Outcome("checkout_requested", "Check Google Play", "Verify manually.", True), None)
                        await pilot.pause()
                        next_button = app.query_one("#next")
                        self.assertTrue(next_button.display)
                        self.assertLessEqual(next_button.region.bottom, app.query_one("#content").region.bottom)
                        app.next_pressed()
                        await pilot.pause()
                        from tui import Approval
                        self.assertIsInstance(app.screen, Approval)
                        for selector in ("#cancel", "#approve"):
                            region = app.screen.query_one(selector).region
                            self.assertGreaterEqual(region.y, 0)
                            self.assertLessEqual(region.bottom, size[1])
                            self.assertLessEqual(region.right, size[0])
                        await pilot.click("#cancel")

    async def test_review_actions_keep_full_labels_and_next_is_clickable(self):
        from tui import GoogleAITUI
        for size in ((110, 35), (90, 20), (80, 24), (60, 20), (48, 20)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch.object(GoogleAITUI, "run_stage"):
                    async with app.run_test(size=size) as pilot:
                        app._start(2, True)
                        app._finished(
                            2, Outcome("checkout_requested", "Check Google Play",
                                       "Verify manually.", True), None
                        )
                        await pilot.pause()
                        advanced = app.query_one("#advanced_toggle")
                        self.assertTrue(advanced.display)
                        self.assertTrue(advanced.disabled, "Advanced stays locked during review")
                        for selector in ("#next", "#finish"):
                            button = app.query_one(selector)
                            self.assertTrue(button.display)
                            self.assertGreaterEqual(button.content_region.width,
                                                    len(str(button.label)), selector)
                            self.assertLessEqual(button.region.right, size[0], selector)
                            self.assertLessEqual(button.region.bottom, size[1] - 1, selector)
                            button.focus()
                            await pilot.pause()
                            rendered = unescape(app.export_screenshot()).replace("\xa0", " ")
                            self.assertIn(str(button.label), rendered,
                                          "Review action must remain readable when focused")
                        await pilot.click("#next")
                        await pilot.pause()
                        from tui import Approval
                        self.assertIsInstance(app.screen, Approval, "Next must be clickable at this width")
                        await pilot.click("#cancel")

    async def test_update_state_is_quiet_for_dev_and_highlights_available_version(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test() as pilot:
                await pilot.pause()
                reason = "Automatic updates require main. Update development branches manually."
                app._update_check_done(UpdateInfo("error", reason))
                self.assertIn("Development build", str(app.query_one("#update_status").render()))
                self.assertEqual(app.query_one("#update_status").tooltip, reason)
                self.assertFalse(app.query_one("#update_bar").has_class("available"))
                app._update_check_done(UpdateInfo("available", "New version · abcdef12 → 12345678"))
                self.assertTrue(app.query_one("#update_bar").has_class("available"))
                self.assertEqual(str(app.query_one("#update").label), "Update & Restart")


class ResponsiveScreenTests(unittest.IsolatedAsyncioTestCase):
    """Exercise the visible layout and mouse controls, never actual Android or billing."""

    SIZES = ((110, 35), (90, 20), (80, 24), (62, 22), (60, 20), (58, 20), (48, 20))

    def assert_onscreen(self, widget, size, *, label=False):
        region = widget.region
        self.assertGreater(region.width, 0, widget.id)
        self.assertGreater(region.height, 0, widget.id)
        self.assertGreaterEqual(region.x, 0, widget.id)
        self.assertGreaterEqual(region.y, 0, widget.id)
        self.assertLessEqual(region.right, size[0], widget.id)
        self.assertLessEqual(region.bottom, size[1] - 1, widget.id)
        if label:
            self.assertGreaterEqual(widget.content_region.width, len(str(widget.label)), widget.id)

    async def test_resizing_live_dashboard_keeps_primary_and_toolbar_controls_in_view(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch.object(GoogleAITUI, "run_stage"):
                async with app.run_test(size=(110, 35)) as pilot:
                    for size in self.SIZES[1:] + self.SIZES[:1]:
                        await pilot.resize_terminal(*size)
                        await pilot.pause()
                        self.assertEqual((app.size.width, app.size.height), size)
                        for selector in ("#quickstart", "#advanced_toggle", "#nav_help",
                                         "#diagnose", "#debug", "#exit", "#update"):
                            self.assert_onscreen(app.query_one(selector), size, label=True)
                        for selector in ("#quickstart", "#advanced_toggle"):
                            button = app.query_one(selector)
                            button.focus()
                            await pilot.pause()
                            screenshot = unescape(app.export_screenshot()).replace("\xa0", " ")
                            self.assertIn(str(button.label), screenshot, selector)

    async def test_help_and_checkout_approval_dialogs_fit_all_responsive_breakpoints(self):
        from tui import Approval, GoogleAITUI, HelpScreen
        for size in self.SIZES:
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch.object(GoogleAITUI, "run_stage") as stage:
                    async with app.run_test(size=size) as pilot:
                        await pilot.click("#nav_help")
                        await pilot.pause()
                        self.assertIsInstance(app.screen, HelpScreen)
                        for selector in ("#help_card", "#help_scroll", "#close_help"):
                            self.assert_onscreen(app.screen.query_one(selector), size,
                                                 label=selector == "#close_help")
                        await pilot.click("#close_help")
                        self.assertNotIsInstance(app.screen, HelpScreen)
                        app._confirm_stage(2, False)
                        await pilot.pause()
                        self.assertIsInstance(app.screen, Approval)
                        for selector in ("#approval_card", "#approval_title", "#approval_scroll",
                                         "#cancel", "#approve"):
                            self.assert_onscreen(app.screen.query_one(selector), size,
                                                 label=selector in ("#cancel", "#approve"))
                        await pilot.click("#cancel")
                        await pilot.pause()
                        self.assertNotIsInstance(app.screen, Approval)
                        self.assertFalse(app._approval_pending)
                    stage.assert_not_called()

    async def test_advanced_selectors_are_visible_or_reachable_by_scrolling(self):
        from tui import GoogleAITUI
        for size in self.SIZES:
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch.object(GoogleAITUI, "run_stage"):
                    async with app.run_test(size=size) as pilot:
                        await pilot.click("#advanced_toggle")
                        await pilot.pause()
                        viewport = app.query_one("#workflow_actions").region
                        for selector in ("#mode", "#step"):
                            region = app.query_one(selector).region
                            self.assertGreaterEqual(region.y, viewport.y, selector)
                            if size[0] >= 52:
                                self.assertLessEqual(region.bottom, viewport.bottom, selector)
                        self.assertIn("One step only", screen_text(app))
                        if size[0] < 52:
                            app.query_one("#step").scroll_visible(animate=False)
                            await pilot.pause()
                        self.assertIn("Available offers", screen_text(app))

    async def test_dialog_warning_text_is_reachable_by_scrolling(self):
        from tui import Approval, GoogleAITUI, HelpScreen
        for size in ((90, 20), (48, 20)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch.object(GoogleAITUI, "run_stage"):
                    async with app.run_test(size=size) as pilot:
                        app._confirm_stage(2, False)
                        await pilot.pause()
                        self.assertIsInstance(app.screen, Approval)
                        self.assertIn("Confirm this Google Play account", screen_text(app))
                        app.screen.query_one("#approval_scroll").scroll_end(animate=False)
                        for _ in range(30):
                            await pilot.pause()
                            if "not guaranteed." in screen_text(app):
                                break
                        self.assertIn("not guaranteed.", screen_text(app))
                        await pilot.click("#cancel")
                        await pilot.pause()
                        await pilot.click("#nav_help")
                        await pilot.pause()
                        self.assertIsInstance(app.screen, HelpScreen)
                        app.screen.query_one("#help_scroll").scroll_end(animate=False)
                        for _ in range(30):
                            await pilot.pause()
                            if "only prevents later steps" in screen_text(app):
                                break
                        self.assertIn("only prevents later steps", screen_text(app))
                        await pilot.click("#close_help")

    async def test_advanced_modes_run_button_and_return_are_accessible(self):
        from tui import Approval, GoogleAITUI
        from textual.widgets import Select
        for size in self.SIZES:
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch.object(GoogleAITUI, "run_stage") as stage:
                    async with app.run_test(size=size) as pilot:
                        await pilot.click("#advanced_toggle")
                        await pilot.pause()
                        self.assertTrue(app.advanced_visible)
                        for selector in ("#mode", "#step", "#run", "#advanced_toggle"):
                            self.assert_onscreen(app.query_one(selector), size,
                                                 label=selector in ("#run", "#advanced_toggle"))
                        for mode, label in (("single", "Run selected step"),
                                            ("from", "Run from selected step"),
                                            ("all", "Run all: Steps 2-5")):
                            app.query_one("#mode", Select).value = mode
                            run_button = app.query_one("#run")
                            for _ in range(20):
                                if str(run_button.label) == label:
                                    break
                                await pilot.pause(0.05)
                            self.assertEqual(str(run_button.label), label)
                            self.assert_onscreen(run_button, size, label=True)
                        # All begins at Step 2 and must still open a separate approval.
                        await pilot.click("#run")
                        await pilot.pause()
                        self.assertIsInstance(app.screen, Approval)
                        await pilot.click("#cancel")
                        for _ in range(20):
                            if not isinstance(app.screen, Approval):
                                break
                            await pilot.pause(0.05)
                        self.assertNotIsInstance(app.screen, Approval)
                        await pilot.click("#advanced_toggle")
                        for _ in range(20):
                            if not app.advanced_visible:
                                break
                            await pilot.pause(0.05)
                        self.assertFalse(app.advanced_visible)
                    stage.assert_not_called()

    async def test_busy_offers_review_next_and_finish_keep_buttons_clickable(self):
        from tui import Approval, GoogleAITUI
        report = {"status": "listed", "detected_play_account": "owner@example.invalid",
                  "offers": [{"id": "12months-eft", "micros": "0", "period": "P1Y"}]}
        for size in self.SIZES:
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch.object(GoogleAITUI, "run_stage") as stage:
                    async with app.run_test(size=size) as pilot:
                        app._start(1, False)
                        await pilot.pause()
                        self.assert_onscreen(app.query_one("#stop"), size, label=True)
                        self.assertTrue(app.query_one("#advanced_toggle").disabled)
                        app._finished(1, Outcome("listed", "Offers loaded", "Review account."), report)
                        await pilot.pause()
                        for selector in ("#continue_initial", "#recheck", "#offers_toggle"):
                            self.assert_onscreen(app.query_one(selector), size, label=True)
                        await pilot.click("#offers_toggle")
                        for _ in range(20):
                            if app._offers_visible:
                                break
                            await pilot.pause(0.05)
                        self.assertTrue(app.query_one("#offer_view").display)
                        # Separate the two clicks so the terminal driver does not group a double-click.
                        await pilot.pause(0.4)
                        await pilot.click("#offers_toggle")
                        for _ in range(20):
                            if not app._offers_visible:
                                break
                            await pilot.pause(0.05)
                        self.assertFalse(app.query_one("#offer_view").display)
                        app._start(2, True)
                        app._finished(
                            2, Outcome("checkout_requested", "Check Google Play",
                                       "Verify manually.", True), None
                        )
                        await pilot.pause()
                        for selector in ("#next", "#finish"):
                            button = app.query_one(selector)
                            self.assert_onscreen(button, size, label=True)
                            button.focus()
                            await pilot.pause()
                            screenshot = unescape(app.export_screenshot()).replace("\xa0", " ")
                            self.assertIn(str(button.label), screenshot, selector)
                        await pilot.click("#next")
                        for _ in range(20):
                            if isinstance(app.screen, Approval):
                                break
                            await pilot.pause(0.05)
                        self.assertIsInstance(app.screen, Approval)
                        await pilot.pause()
                        await pilot.click("#cancel")
                        for _ in range(20):
                            if not isinstance(app.screen, Approval):
                                break
                            await pilot.pause(0.05)
                        self.assertNotIsInstance(app.screen, Approval)
                        await pilot.click("#finish")
                        for _ in range(20):
                            if not app.sequence:
                                break
                            await pilot.pause(0.05)
                        self.assertFalse(app.sequence)
                        self.assertTrue(app.query_one("#quickstart").display)
                    self.assertEqual(stage.call_count, 2, "Only mocked stages 1 and 2 run")
