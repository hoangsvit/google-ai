#!/usr/bin/env python3
"""Render real TUI screens with synthetic, non-transactional fixture states."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tui import GoogleAITUI  # noqa: E402
from tui_core import Outcome  # noqa: E402
from device_diagnostics import ConnectionStatus  # noqa: E402
from textual.widgets import Button, Select, Static  # noqa: E402
from offer_discovery import parse_step1  # noqa: E402
from sku_check_core import sanitize_offers  # noqa: E402

SCENARIOS = {"startup", "disconnected", "offer_found", "step_picker", "approval", "review",
             "linux_startup", "linux_step_picker", "sku_offers", "sku_missing",
             "sku_extra_steps",
             "environment_ready", "adb_missing", "account_picker", "offer_error", "offer_running", "approval_3", "approval_4", "approval_5", "review_3", "review_4", "review_5", "retry_3", "account_unverified", "approval_2", "optional_picker"}
scenario = os.environ.get("PREVIEW_SCENARIO", "")
if scenario not in SCENARIOS:
    raise SystemExit("Invalid preview scenario")


class PreviewApp(GoogleAITUI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Synthetic states; never invoke real Android/Google Play operations.
        # Linux scenarios explicitly activate the native Linux UI path.
        self.linux_mode = scenario.startswith("linux_")
        self.macos_mode = False
        self.native_mode = self.linux_mode

    def _poll_connection(self):
        pass  # Never probe host devices from a screenshot run.

    def run_stage(self, step):
        raise RuntimeError("Real stages are disabled in terminal previews")

    def _start(self, step, sequence):
        raise RuntimeError("Real operations are disabled in terminal previews")

    def scan_known_skus(self, *args, **kwargs):
        raise RuntimeError("Real SKU scans are disabled in terminal previews")

    def _save_history(self, account, step, status):
        pass  # Do not persist fixture accounts or history.

    def _preview_ready(self, optional=False):
        self._checked_device = "emulator-5554"
        self._connection_state = ConnectionStatus("connected", ("emulator-5554",))
        self._selected_account = self._verified_account = "preview.one@example.invalid"
        self._offer_ready_account = self._verified_account
        self._offer_ready_device = self._checked_device
        self._offer_check_ready = True
        self.query_one("#device", Static).update("Device  •  Android connected (ADB)")
        self.query_one("#account", Static).update("Account  •  p***@example.invalid (SIMULATED)")
        self._set_workflow(0, "done")
        self._set_workflow(1, "done")
        if optional:
            self._update_discovered(parse_step1({"offers": [
                {"product": "g1.2tb.ai.subs_variant", "id": "6months-eft-ss-2026",
                 "micros": "0", "period": "P6M"},
            ]}), replace=True)

    def on_mount(self):
        super().on_mount()
        self.set_timer(0.5, self.prepare_scenario)

    def prepare_scenario(self):
        if scenario in {"startup", "linux_startup"}:
            return
        if scenario == "environment_ready":
            self._connection_polled(ConnectionStatus("connected", ("emulator-5554",)))
            self._finished(0, Outcome("environment_ok", "Environment ready (SIMULATED)",
                                      "Android environment checked. Run Step 1 next."), {})
            return
        if scenario == "adb_missing":
            self._connection_polled(ConnectionStatus("missing_adb"))
            return
        if scenario == "account_picker":
            self._account_candidates_loaded(["preview.one@example.invalid",
                                             "preview.two@example.invalid"], "emulator-5554")
            return
        if scenario == "offer_error":
            self._finished(1, Outcome("tool_error", "Offer check failed (SIMULATED)",
                                      "Check Android connection and retry Step 1."), {})
            return
        if scenario == "account_unverified":
            self._finished(1, Outcome("listed", "Offers loaded", "Review offers."), {
                "offers": [{"product": "g1.2tb.ai.subs_variant", "id": "12months-eft",
                            "micros": "0", "period": "P1Y"}],
            })
            return
        if scenario == "offer_running":
            # UI-only snapshot; do not call _start or launch a worker.
            self.busy = True
            self.current_step = 1
            self._set_workflow(1, "running")
            self._set_status("Checking device and offers (SIMULATED)")
            self.query_one("#quickstart", Button).label = "Checking offers… 4s"
            self.query_one("#quickstart", Button).disabled = True
            self.query_one("#stop", Button).display = True
            self.query_one("#stop", Button).disabled = False
            return
        if scenario.startswith("approval_"):
            step = int(scenario.rsplit("_", 1)[1])
            self._preview_ready(optional=step == 5)
            self._confirm_stage(step, False)
            return
        if scenario.startswith("review_"):
            step = int(scenario.rsplit("_", 1)[1])
            self._preview_ready(optional=step == 5)
            self.current_step = step
            self.sequence = step == 3
            self._finished(step, Outcome("checkout_requested", f"Step {step} submitted (SIMULATED)",
                                         "Review the actual subscription in Google Play.", True), {})
            return
        if scenario == "retry_3":
            self._preview_ready()
            self.current_step = 3
            self._last_outcome = Outcome("tool_error", "Synthetic previous failure", "Review Google Play.")
            self._confirm_stage(3, False)
            return
        if scenario == "optional_picker":
            self._preview_ready(optional=True)
            self.advanced_pressed()
            self.query_one("#step", Select).value = 5
            self._update_run_mode()
            # Display the real advanced hint in the same screenshot as Run.
            self.call_after_refresh(lambda: self._reveal_step_control("#mode_hint"))
            return
        if scenario in ("sku_offers", "sku_missing", "sku_extra_steps"):
            # Real dashboard widgets, simulated ProductDetails, no Android.
            primary = [
                {"product": "g1.2tb.ai.subs_variant", "id": "12months-eft",
                 "micros": "0", "period": "P1Y"},
            ]
            if scenario == "sku_missing":
                primary = []
            if scenario == "sku_extra_steps":
                primary += [
                    {"product": "g1.2tb.ai.subs_variant", "id": "6months-eft-ss-2026",
                     "micros": "0", "period": "P6M"},
                    {"product": "g1.play.20tb", "id": "promo-2026",
                     "micros": "19990000", "period": "P1M"},
                ]
            self._offer_report = {"status": "listed", "offers": primary}
            requested = ["g1.2tb.ai.subs_variant", "g1.play.20tb",
                         "g1.play.ai.pro", "g1.30tb"]
            if scenario == "sku_missing":
                rows = [
                    {"sku": "g1.2tb.ai.subs_variant", "no_offers": True},
                    {"sku": "g1.play.20tb", "no_offers": True},
                ]
            else:
                rows = [
                    {"sku": "g1.2tb.ai.subs_variant",
                     "offer_id": "12months-eft", "base_plan_id": "annual",
                     "phases": [{"price_amount_micros": "0", "currency": "USD",
                                 "billing_period": "P1Y"}]},
                    {"sku": "g1.play.20tb",
                     "offer_id": "promo-2026", "base_plan_id": "monthly",
                     "phases": [{"price_amount_micros": "19990000",
                                 "currency": "USD", "billing_period": "P1M"}]},
                ]
            self._sku_report = sanitize_offers(rows, requested)
            self._update_discovered(parse_step1(self._offer_report))
            self.query_one("#offer_view").styles.height = 24
            self._render_offer_catalog()
            self.query_one("#state", Static).update(
                "Step 1 complete · SKU scan results (SIMULATED)")
            self.query_one("#activity", Static).update(
                "Synthetic scan complete; review supported offers below.")
            self.query_one("#status_panel").scroll_end(animate=False)
            view = self.query_one("#offer_view")
            if scenario == "sku_extra_steps":
                view.call_after_refresh(lambda: view.scroll_home(animate=False))
            else:
                view.call_after_refresh(lambda: view.scroll_end(animate=False))
            return
        if scenario == "disconnected":
            self._connection_polled(ConnectionStatus("disconnected"))
        elif scenario == "offer_found":
            # The synthetic successful check needs the same device identity
            # that the real Step 1 status output supplies.
            self._received("Device emulator-5554")
            self._verified_account = "preview@example.invalid"
            self._finished(1, Outcome("listed", "Offers loaded", "Review offers"), {
                "status": "listed", "detected_play_account": "preview@example.invalid",
                "offers": [{"id": "12months-eft", "micros": "0", "period": "P1Y"}],
            })
        elif scenario in {"step_picker", "linux_step_picker"}:
            self.advanced_pressed()
        elif scenario == "approval":
            self._offer_check_ready = True
            self._confirm_stage(2, True)
        elif scenario == "review":
            self._offer_check_ready = True
            self.sequence = True
            self.current_step = 2
            self._finished(2, Outcome("checkout_requested", "Checkout submitted - not yet verified",
                                     "Check Google Play subscriptions and renewal date.", True), {})


PreviewApp(repo=Path(__file__).resolve().parents[2]).run()
