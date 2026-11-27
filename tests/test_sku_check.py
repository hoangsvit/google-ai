"""SKU Explorer safety and offline regression tests; no Android/emulator needed."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

import sku_check_core as core
import sku_check_runner as runner

ROOT = Path(__file__).resolve().parents[1]


class SKUMetadataTests(unittest.TestCase):
    def test_requires_explicit_bounded_skus(self):
        self.assertEqual(
            core.validate_skus(["g1.2tb.ai.subs_variant", "g1.2tb.ai.subs_variant"]),
            ["g1.2tb.ai.subs_variant"])
        for invalid in ([], ["not-sku"], ["g1.x;rm -rf"], ["g1.2tb"] * 11):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                core.validate_skus(invalid)

    def test_ordered_phases_and_token_stripping(self):
        payload = [{
            "sku": "g1.2tb.ai.subs_variant",
            "offer_id": "test-offer",
            "base_plan_id": "yearly",
            "token": "SECRET-DO-NOT-STORE",
            "email": "secret@example.com",
            "phases": [
                {
                    "price_amount_micros": "0",
                    "currency": "USD", "billing_period": "P1M",
                    "billing_cycle_count": 1, "recurrence_mode": 2,
                    "purchaseToken": "VERY-SECRET",
                },
                {
                    "price_amount_micros": "19990000",
                    "currency": "USD", "billing_period": "P1M",
                    "billing_cycle_count": 0, "recurrence_mode": 1,
                },
            ],
        }]
        got = core.sanitize_offers(payload, ["g1.2tb.ai.subs_variant"])
        self.assertEqual(got["status"], "observed")
        self.assertEqual(len(got["items"][0]["phases"]), 2)
        self.assertFalse(got["account_binding_verified"])
        self.assertFalse(got["eligibility_verified"])
        self.assertFalse(got["subscription_active_verified"])
        self.assertNotIn("SECRET", str(got))
        self.assertNotIn("secret@example.com", str(got))
        text = core.render_result(got)
        self.assertIn("Phase 1: 0.00 USD / P1M (1 cycle(s))", text)
        self.assertIn("Phase 2: 19.99 USD / P1M (ongoing)", text)
        self.assertLess(text.index("Phase 1:"), text.index("Phase 2:"))
        self.assertIn("PLAY ACCOUNT UNVERIFIED", text.splitlines()[0])
        self.assertIn("UNVERIFIED", text)
        self.assertNotIn("token", text.lower())

    def test_pricing_phase_review_flags_inconsistent_currency_and_cycles(self):
        row = {"sku": "g1.example", "offer_id": "fixture", "base_plan_id": "monthly",
               "phases": [
                   {"price_amount_micros": "1000000", "currency": "USD",
                    "billing_period": "P1M", "recurrence_mode": 1, "billing_cycle_count": 2},
                   {"price_amount_micros": "2000000", "currency": "EUR",
                    "billing_period": "P1M", "recurrence_mode": 2, "billing_cycle_count": 0},
               ]}
        result = core.sanitize_offers([row], ["g1.example"])
        warnings = result["items"][0]["pricing_phase_warnings"]
        self.assertEqual(len(warnings), 4)
        output = core.render_result(result)
        self.assertIn("Currency changes across phases", output)
        self.assertIn("ongoing phase is not last", output)
        self.assertIn("finite billing cycle count missing or zero", output)
        self.assertFalse(result["eligibility_verified"])
        self.assertFalse(result["account_binding_verified"])

    def test_complete_phases_do_not_verify_account_or_eligibility(self):
        phases = [
            {"price_amount_micros": "1990000", "currency": "USD",
             "billing_period": "P1M", "billing_cycle_count": 3, "recurrence_mode": 2},
            {"price_amount_micros": "19990000", "currency": "USD",
             "billing_period": "P1M", "billing_cycle_count": 0, "recurrence_mode": 1},
        ]
        row = {"sku": "g1.example", "offer_id": "fixture",
               "base_plan_id": "monthly", "phases": phases}
        result = core.sanitize_offers([row], ["g1.example"])
        self.assertEqual(result["items"][0]["pricing_phase_warnings"], [])
        self.assertIn("3 cycle(s)", core.render_result(result))
        self.assertIn("ongoing", core.render_result(result))
        self.assertFalse(result["eligibility_verified"])
        self.assertFalse(result["subscription_active_verified"])

    def test_rejects_missing_currency_and_malformed_phases(self):
        result = core.sanitize_offers([{
            "sku": "g1.play.20tb", "offer_id": "example",
            "base_plan_id": "monthly", "phases": [{
                "price_amount_micros": "19990000",
                "billing_period": "P1M", "currency": "UNKNOWN"
            }]
        }], ["g1.play.20tb"])
        self.assertEqual(result["status"], "unusable_metadata")
        self.assertEqual(result["items"], [])
        self.assertEqual(result["unusable_skus"], ["g1.play.20tb"])
        self.assertEqual(result["missing_skus"], [])

    def test_invalid_first_phase_never_relabels_renewal(self):
        row = {"sku": "g1.example", "offer_id": "fixture", "base_plan_id": "monthly",
               "phases": [{"price_amount_micros": "0", "currency": "invalid",
                           "billing_period": "P1M"},
                          {"price_amount_micros": "1234000", "currency": "KWD",
                           "billing_period": "P1M"}]}
        result = core.sanitize_offers([row], ["g1.example"])
        self.assertEqual(result["status"], "unusable_metadata")
        self.assertNotIn("Phase 1:", core.render_result(result))
        row["phases"] = row["phases"][1:]
        result = core.sanitize_offers([row], ["g1.example"])
        self.assertIn("1.234 KWD / P1M (recurrence unknown)", core.render_result(result))

    def test_truncated_product_observation_not_reported_missing(self):
        result = core.sanitize_offers([], ["g1.example", "g1.other"],
                                      returned_skus=("g1.example",),
                                      no_offer_skus=("g1.example",), truncated=True)
        self.assertEqual(result["no_offer_skus"], ["g1.example"])
        self.assertEqual(result["missing_skus"], ["g1.other"])
        self.assertIn("truncated locally", core.render_result(result))

    def test_missing_and_no_offers_are_distinct(self):
        self.assertEqual(
            core.sanitize_offers([], ["g1.play.20tb"])["status"], "not_returned")
        self.assertEqual(
            core.sanitize_offers([{"sku": "g1.play.20tb", "no_offers": True}],
                                 ["g1.play.20tb"])["status"],
            "no_offers")

    def test_cleanup_wait_is_bounded(self):
        import threading
        blocked = threading.Event()
        try:
            self.assertFalse(runner._bounded_cleanup(blocked.wait, timeout=0.01))
        finally:
            blocked.set()
        self.assertTrue(runner._bounded_cleanup(lambda: None, timeout=1))

    def test_runner_reuses_noninstalling_adb_locator(self):
        with patch.object(runner, "locate_adb", return_value="fixture-adb") as locate:
            self.assertEqual(runner.find_adb(), "fixture-adb")
            locate.assert_called_once_with()

    def test_runner_fails_closed_without_adb(self):
        with patch.object(runner, "find_adb", return_value=None):
            out = runner.check_skus("emulator-5554", ["g1.play.20tb"])
        self.assertEqual(out["status"], "device_not_ready")
        self.assertEqual(out["items"], [])

    def test_runner_fails_closed_for_invalid_serial(self):
        with patch.object(runner, "find_adb", side_effect=RuntimeError("must not be called")) as find:
            out = runner.check_skus("../../bad", ["g1.play.20tb"])
            find.assert_not_called()
        self.assertEqual(out["status"], "device_not_ready")

    def test_runner_delegates_device_mapping_to_shared_engine(self):
        import ultra0
        from unittest.mock import sentinel

        original = ultra0.ADB
        with patch.object(ultra0, "get_target_frida_device",
                          return_value=sentinel.device) as shared:
            self.assertIs(runner._frida_device("mock-adb", "fixture-device", 123),
                          sentinel.device)
            shared.assert_called_once_with(123, "fixture-device")
        self.assertIs(ultra0.ADB, original)
        self.assertNotIn("enumerate_devices", (ROOT / "sku_check_runner.py").read_text(encoding="utf-8"))

    def test_query_javascript_has_no_checkout_path(self):
        js = (ROOT / "assets/frida/sku_query_readonly.js").read_text(encoding="utf-8")
        for forbidden in (
            "launchBillingFlow", "BillingFlowParams", "setOfferToken",
            "getOfferToken", "getPurchaseToken", "queryPurchasesAsync",
            "setOldPurchaseToken", "input tap"
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, js)
        self.assertIn("queryProductDetailsAsync", js)

    def test_step_one_uses_one_button_and_sku_runner_never_starts_checkout(self):
        ui = (ROOT / "tui.py").read_text(encoding="utf-8")
        runner = (ROOT / "sku_check_runner.py").read_text(encoding="utf-8")
        self.assertIn("sku_check_runner.py", ui)
        self.assertIn("SUPPORTED OFFERS", ui)
        self.assertNotIn('id="sku_explorer"', ui)
        self.assertNotIn("SKUExplorer(", ui)
        self.assertNotIn("launchBillingFlow", runner)

    def test_result_lists_skus_base_plans_offers_and_missing_candidates(self):
        raw = [{"sku": "g1.play.20tb", "offer_id": "intro",
                "base_plan_id": "monthly", "phases": [{
                    "price_amount_micros": "19990000", "currency": "USD",
                    "billing_period": "P1M"
                }]}]
        parsed = core.sanitize_offers(raw, ["g1.play.20tb", "g1.30tb"])
        output = core.render_result(parsed)
        self.assertIn("SKU: g1.play.20tb", output)
        self.assertIn("Offer: intro", output)
        self.assertIn("19.99 USD / P1M", output)
        self.assertIn("SKU: g1.30tb", output)
        self.assertIn("Not returned", output)
        self.assertNotIn("SECRET", output)
        self.assertEqual(parsed["missing_skus"], ["g1.30tb"])


@unittest.skipUnless(importlib.util.find_spec("textual") is not None,
                     "Textual is tested in Terminal UI previews with dependencies installed")
class StepOneSKUUITests(unittest.IsolatedAsyncioTestCase):
    async def test_one_step_one_button_and_supported_offer_list(self):
        from tempfile import TemporaryDirectory
        from textual.widgets import Button, Select, Static, RichLog
        from tui import GoogleAITUI

        with TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                self.assertEqual(app.query_one("#step", Select).value, 1)
                self.assertEqual(len(app.query("#sku_explorer")), 0)
                self.assertGreater(app.query_one("#quickstart", Button).region.width, 25)
                from research_offer_catalog import STEP_REFERENCES
                self.assertEqual(len(app.query("#workflow .workflow-step")), 6 + len(STEP_REFERENCES))
                self.assertEqual(len(app.query("#workflow .research-step")), len(STEP_REFERENCES))
                self.assertFalse(app.query_one("#stage_5", Static).display)
                app._offer_report = {"offers": [
                    {"id": "12months-eft", "product": "g1.2tb.ai.subs_variant",
                     "micros": "0", "period": "P1Y"}
                ]}
                app._sku_report = core.sanitize_offers([{
                    "sku": "g1.play.20tb", "offer_id": "promo-2026",
                    "base_plan_id": "monthly", "phases": [{
                        "price_amount_micros": "19990000",
                        "currency": "USD", "billing_period": "P1M"
                    }]
                }], ["g1.play.20tb", "g1.30tb"])
                app._render_offer_catalog()
                await pilot.pause()
                self.assertTrue(app.query_one("#offer_view", RichLog).display)
                self.assertTrue(app.query_one("#offers_title", Static).display)
                rendered = "\n".join(segment.text for strip in
                                     app.query_one("#offer_view", RichLog).lines
                                     for segment in strip)
                self.assertIn("g1.play.20tb", rendered)
                self.assertIn("promo-2026", rendered)
                self.assertIn("g1.30tb", rendered)
                self.assertIn("UNVERIFIED", rendered)
                self.assertIn("12months-eft", rendered)

    async def test_offer_catalog_starts_at_top_even_when_overflowing(self):
        from tempfile import TemporaryDirectory
        from textual.widgets import RichLog
        from tui import GoogleAITUI

        with TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(120, 55)) as pilot:
                app._offer_report = {"status": "listed", "offers": [
                    {"product": "g1.2tb.ai.subs_variant", "id": "12months-eft",
                     "micros": "0", "period": "P1Y"},
                    *({"product": "g1.example", "id": f"fixture-{i}",
                       "micros": "0", "period": "P1M"} for i in range(5)),
                ]}
                view = app.query_one("#offer_view", RichLog)
                view.styles.height = 8
                app._render_offer_catalog()
                await pilot.pause()
                self.assertFalse(view.auto_scroll)
                self.assertGreater(view.max_scroll_y, 0)
                self.assertEqual(view.scroll_y, 0)
                view.scroll_end(animate=False)
                await pilot.pause()
                self.assertGreater(view.scroll_y, 0)
                app._render_offer_catalog()
                await pilot.pause()
                self.assertEqual(view.scroll_y, 0)
                self.assertIn("PRODUCT / OFFER", "".join(
                    segment.text for segment in view.lines[0]))

    async def test_real_step_one_launches_automatic_sku_scan(self):
        from tempfile import TemporaryDirectory
        from tui import GoogleAITUI
        from tui_core import Outcome

        with TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                from device_diagnostics import ConnectionStatus
                app._checked_device = "emulator-5554"
                app._selected_account = "verified@example.test"
                app._verified_account = "verified@example.test"
                app._connection_state = ConnectionStatus(
                    "connected", ("emulator-5554",))
                app._real_step1_run = True
                with patch.object(app, "scan_known_skus") as scan:
                    app._finished(1, Outcome("listed", "Offers listed",
                                             "Review the available offers."), {
                        "status": "listed",
                        "detected_play_account": "verified@example.test",
                        "offers": [{"id": "12months-eft", "micros": "0",
                                    "product": "g1.2tb.ai.subs_variant"}],
                    })
                    self.assertTrue(app._offer_check_ready)
                    scan.assert_called_once_with("emulator-5554",
                                                 "verified@example.test",
                                                 app._extra_scan_generation)
                await pilot.pause()
                self.assertEqual(len(app.query("#sku_explorer")), 0)

    async def test_only_supported_optional_offer_appears_in_step_picker(self):
        from tempfile import TemporaryDirectory
        from textual.widgets import Button, Select, Static
        from offer_discovery import parse_step1
        from tui import GoogleAITUI, ResearchOffers
        from device_diagnostics import ConnectionStatus

        with TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                self.assertFalse(app.query_one("#stage_5", Static).display)
                app._offer_check_ready = True
                app._offer_ready_device = "emulator-5554"
                app._offer_ready_account = "fixture@example.invalid"
                app._connection_state = ConnectionStatus("connected", ("emulator-5554",))
                app._update_discovered(parse_step1({"offers": [
                    {"product": "g1.play.20tb", "id": "offer-a"},
                    {"product": "g1.30tb", "id": "offer-b"},
                ]}))
                await pilot.pause()
                self.assertFalse(app._extra_offers)
                self.assertFalse(app.query_one("#stage_5", Static).display)
                app._update_discovered(parse_step1({"offers": [
                    {"product": "g1.2tb.ai.subs_variant", "id": "6months-eft-ss-2026", "micros": "0"},
                ]}))
                await pilot.pause()
                self.assertTrue(app.query_one("#stage_5", Static).display)
                # Static research references must not become executable
                # checkout offers merely because metadata was observed.
                self.assertEqual(len(app._extra_offers), 1)
                self.assertTrue(app._extra_offers[0].legacy_checkout_supported)
                self.assertTrue(app.query_one("#stage_6", Static).has_class("research-step"))
                app.query_one("#step", Select).value = 6
                await pilot.pause()
                self.assertEqual(str(app.query_one("#run", Button).label), "Review selected offer")
                with patch.object(app, "_start") as start:
                    app._confirm_stage(6, False)
                    await pilot.pause()
                    self.assertIsInstance(app.screen, ResearchOffers)
                    start.assert_not_called()
                    with patch.object(app.screen, "open_app") as launch:
                        app.screen.open_pressed()
                        launch.assert_called_once()
                        start.assert_not_called()
                    app.screen.dismiss(False)
                    await pilot.pause()
                app.query_one("#step", Select).value = 1
                await pilot.pause()
                app._update_discovered([], replace=True)
                await pilot.pause()
                self.assertFalse(app.query_one("#stage_5", Static).display)
                self.assertEqual(app.query_one("#step", Select).value, 1)

    async def test_secondary_sku_metadata_never_unlocks_optional_step(self):
        from tempfile import TemporaryDirectory
        from offer_discovery import parse_sku_check, parse_step1
        from textual.widgets import RichLog, Static
        from tui import GoogleAITUI

        # The same exact offer identifier in a secondary scan must not
        # authorize anything, even when its metadata appears complete.
        with TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(120, 55)) as pilot:
                app._offer_check_ready = True
                app._offer_ready_device = "fixture-device"
                app._offer_ready_account = "fixture@example.invalid"
                app._offer_report = {"offers": []}
                metadata = core.sanitize_offers([{
                    "sku": "g1.2tb.ai.subs_variant",
                    "offer_id": "6months-eft-ss-2026",
                    "base_plan_id": "fixture-plan",
                    "phases": [{"price_amount_micros": "0", "currency": "USD",
                                "billing_period": "P6M"}],
                }], ["g1.2tb.ai.subs_variant"])
                app._update_discovered(parse_sku_check(metadata))
                app._known_skus_finished(metadata, "fixture-device",
                                         "fixture@example.invalid", app._extra_scan_generation)
                await pilot.pause()
                self.assertFalse(app._extra_offers)
                self.assertFalse(app.query_one("#stage_5", Static).display)
                rendered = "\\n".join(segment.text for strip in
                                      app.query_one("#offer_view", RichLog).lines
                                      for segment in strip)
                self.assertIn("PLAY ACCOUNT UNVERIFIED", rendered)
                self.assertIn("6months-eft-ss-2026", rendered)
                self.assertFalse(metadata["account_binding_verified"])
                # The pre-existing primary-report logic remains intact.
                app._update_discovered(parse_step1({"offers": [{
                    "product": "g1.2tb.ai.subs_variant",
                    "id": "6months-eft-ss-2026", "micros": "0",
                }]}))
                self.assertTrue(app.query_one("#stage_5", Static).display)
                app._update_discovered(parse_sku_check(metadata))
                self.assertEqual(app._extra_offers[0].source, "step1")

    async def test_sku_scan_requires_same_verified_step_one_identity(self):
        from tempfile import TemporaryDirectory
        from textual.widgets import RichLog
        from tui import GoogleAITUI

        with TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)):
                app._offer_report = {"offers": [
                    {"id": "12months-eft", "product": "g1.2tb.ai.subs_variant",
                     "micros": "0", "period": "P1Y"}
                ]}
                app._offer_check_ready = True
                app._offer_ready_device = "emulator-5554"
                app._offer_ready_account = "verified@example.test"
                result = core.sanitize_offers([{
                    "sku": "g1.play.20tb", "offer_id": "extra",
                    "base_plan_id": "monthly", "phases": [{
                        "price_amount_micros": "0", "currency": "USD",
                        "billing_period": "P1M",
                    }]
                }], ["g1.play.20tb"])
                app._known_skus_finished(result, "other-device",
                                         "verified@example.test", app._extra_scan_generation)
                self.assertIsNone(app._sku_report)
                app._known_skus_finished(result, "emulator-5554",
                                         "verified@example.test", app._extra_scan_generation)
                self.assertEqual(app._sku_report["status"], "observed")
                self.assertFalse(app._extra_offers)
                self.assertTrue(app.query_one("#offer_view", RichLog).display)
                previous = app._sku_report
                app._extra_scan_generation += 1
                app._known_skus_finished({"status": "timeout"},
                                         "emulator-5554", "verified@example.test",
                                         app._extra_scan_generation - 1)
                self.assertIs(app._sku_report, previous)

    async def test_late_scan_cannot_mutate_running_stage(self):
        from tempfile import TemporaryDirectory
        from textual.widgets import Button, Select
        from tui import GoogleAITUI

        with TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)):
                app._offer_check_ready = True
                app._offer_ready_device = "emulator-5554"
                app._offer_ready_account = "preview@example.invalid"
                app.busy = True
                app._update_run_mode()
                self.assertTrue(app.query_one("#step", Select).disabled)
                self.assertTrue(app.query_one("#run", Button).disabled)
                app._known_skus_finished({"status": "observed"}, "emulator-5554",
                                         "preview@example.invalid", app._extra_scan_generation)
                self.assertIsNone(app._sku_report)
                app.busy = False
                app._sku_pending = True
                app.stop_pressed()
                self.assertTrue(app._sku_cancel.is_set())
                app._start(2, False)
                self.assertFalse(app.busy)

    def test_scan_process_requests_graceful_cleanup_before_force(self):
        from unittest.mock import Mock
        from tui import GoogleAITUI

        child = Mock()
        child.poll.return_value = None
        child.pid = 98765
        with patch("tui.os.name", "posix"), patch("tui.os.killpg", create=True) as kill:
            GoogleAITUI._stop_sku_process(child)
        import signal
        kill.assert_called_once_with(98765, signal.SIGTERM)
        child.communicate.assert_called_once_with(timeout=5)
        child.kill.assert_not_called()

    async def test_linux_transport_binding_rejects_device_replacement(self):
        import hashlib
        from tempfile import TemporaryDirectory
        from device_diagnostics import ConnectionStatus
        from tui import GoogleAITUI
        with TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)):
                binding = hashlib.sha256(b"fixture-a").hexdigest()
                app._remember_linux_transport(ConnectionStatus("connected", ("fixture-b",)), binding)
                self.assertIsNone(app._checked_device)
                app._remember_linux_transport(ConnectionStatus("connected", ("fixture-a",)), binding)
                self.assertEqual(app._checked_device, "fixture-a")

    async def test_cancelled_scan_discards_valid_late_result(self):
        from tempfile import TemporaryDirectory
        from tui import GoogleAITUI
        with TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)):
                app._offer_check_ready = True
                app._offer_ready_device = "fixture-device"
                app._offer_ready_account = "preview@example.invalid"
                app._sku_pending = True
                app._sku_cancel.set()
                app._known_skus_finished({"status": "observed", "items": []},
                                         "fixture-device", "preview@example.invalid", app._extra_scan_generation)
                self.assertEqual(app._sku_report, {"status": "cancelled"})
                self.assertFalse(app._sku_pending)

    async def test_optional_step_five_survives_retry_with_same_verified_identity(self):
        from tempfile import TemporaryDirectory
        from device_diagnostics import ConnectionStatus
        from textual.widgets import Button, Select
        from tui import Approval, GoogleAITUI
        from tui_core import Outcome

        with TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                app._checked_device = "fixture-device"
                app._selected_account = "preview@example.invalid"
                app._verified_account = "preview@example.invalid"
                app._connection_state = ConnectionStatus("connected", ("fixture-device",))
                app._finished(1, Outcome("listed", "Offers loaded", "Review"), {
                    "status": "listed",
                    "detected_play_account": "preview@example.invalid",
                    "offers": [
                        {"product": "g1.2tb.ai.subs_variant", "id": "12months-eft", "micros": "0"},
                        {"product": "g1.2tb.ai.subs_variant", "id": "6months-eft-ss-2026", "micros": "0"},
                    ],
                })
                await pilot.pause()
                app.screen.dismiss(False)
                await pilot.pause()
                self.assertTrue(app._offer_check_ready)
                for step in (2, 3, 4, 5):
                    app.query_one("#step", Select).value = step
                    app._update_run_mode()
                    self.assertFalse(app.query_one("#run", Button).disabled)
                app.current_step = 5
                app._checked_device = "fixture-device"
                app._selected_account = "preview@example.invalid"
                app._verified_account = "preview@example.invalid"
                app._finished(5, Outcome("purchase_unavailable", "Unavailable", "Review Google Play"), None)
                await pilot.pause()
                self.assertTrue(app._offer_check_ready)
                self.assertFalse(app.query_one("#run", Button).disabled)
                with patch.object(app, "run_stage") as run:
                    app._confirm_stage(5, False)
                    await pilot.pause()
                    self.assertIsInstance(app.screen, Approval)
                    self.assertIn("RETRY SAFETY", app.screen.message_text)
                    run.assert_not_called()
                    app.screen.dismiss(False)
                    await pilot.pause()
                    run.assert_not_called()

    async def test_sku_query_failure_does_not_revoke_primary_step_one(self):
        from tempfile import TemporaryDirectory
        from device_diagnostics import ConnectionStatus
        from textual.widgets import Button, Select
        from tui import GoogleAITUI
        from tui_core import Outcome

        with TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)) as pilot:
                app._checked_device = "fixture-device"
                app._selected_account = "preview@example.invalid"
                app._verified_account = "preview@example.invalid"
                app._connection_state = ConnectionStatus("connected", ("fixture-device",))
                app._real_step1_run = True
                report = {"status": "listed", "detected_play_account": "preview@example.invalid",
                          "offers": [
                              {"product": "g1.2tb.ai.subs_variant", "id": "12months-eft", "micros": "0"},
                              {"product": "g1.2tb.ai.subs_variant", "id": "6months-eft-ss-2026", "micros": "0"},
                          ]}
                with patch.object(app, "scan_known_skus") as scan:
                    app._finished(1, Outcome("listed", "Offers loaded", "Review"), report)
                    scan.assert_called_once_with("fixture-device", "preview@example.invalid",
                                                 app._extra_scan_generation)
                self.assertTrue(app._sku_pending)
                self.assertTrue(app.query_one("#run", Button).disabled)
                app._known_skus_finished({"status": "timeout"}, "fixture-device",
                                         "preview@example.invalid", app._extra_scan_generation)
                await pilot.pause()
                app.screen.dismiss(False)
                await pilot.pause()
                self.assertIs(app._offer_report, report)
                self.assertEqual(app._sku_report["status"], "timeout")
                self.assertTrue(app._offer_check_ready)
                for step in (2, 3, 4, 5):
                    app.query_one("#step", Select).value = step
                    app._update_run_mode()
                    self.assertFalse(app.query_one("#run", Button).disabled)
                app._connection_polled(ConnectionStatus("disconnected"), startup=True)
                self.assertFalse(app._offer_check_ready)
                self.assertFalse(app._extra_offers)
                self.assertIsNone(app._offer_report)
                self.assertIsNone(app._sku_report)

    async def test_no_unobserved_step_five_execution(self):
        from tempfile import TemporaryDirectory
        from tui import GoogleAITUI

        with TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            async with app.run_test(size=(110, 35)):
                app._start(5, False)
                app._start(6, False)
                self.assertFalse(app.busy)
                self.assertIsNone(app.current_step)


if __name__ == "__main__":
    unittest.main()
