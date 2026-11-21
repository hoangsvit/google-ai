"""Interactive Textual frontend for ePlus AI Toolkit (Windows + macOS preview).

UI-only orchestration: the original run-all.ps1 and ultra0.py still own all
Android, Frida, Google Play, payment and account validation. The TUI never
declares an activated subscription from launchBillingFlow or a Subscribe tap.
"""
from __future__ import annotations

import argparse
import os
import signal
from collections import deque
from pathlib import Path
import re
import subprocess
import sys
import time

from rich.markup import escape
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Footer, Link, RichLog, Select, Static

from tui_core import STAGES, Outcome, command_for_step, mask_email, \
    initial_checkout_blocker, needs_setup, offer_explorer_lines, outcome_for_stage, read_fresh_report, \
    report_summary, validate_step
from device_diagnostics import ConnectionDiagnosis, inspect_connection
from app_update import UpdateError, UpdateInfo, check_for_update, install_update, restart_command


class Approval(ModalScreen[bool]):
    """Clickable approval without long typed phrases."""
    BINDINGS = [("escape", "cancel", "Cancel"),
                ("pageup", "scroll_message(-5)", "Scroll warning up"),
                ("pagedown", "scroll_message(5)", "Scroll warning down")]

    CSS = """
    Approval { align: center middle; background: #070d19 75%; }
    #approval_card {
        width: 72; max-width: 94%; height: 24; max-height: 96%;
        padding: 1 2; background: #17212e; border: round #806542;
    }
    #approval_title { text-style: bold; color: #ebf5ff; margin-bottom: 1; }
    #approval_scroll { height: 1fr; min-height: 2; margin-bottom: 1; scrollbar-size: 1 1; }
    #approval_message { height: auto; color: #c9d8e8; }
    #approval_actions { height: 3; align-horizontal: right; }
    #approval_actions Button { margin-left: 1; }
    #clean_account_ack { height: auto; margin-bottom: 1; }
    """

    def __init__(self, title: str, message: str, clean_account_ack: bool = False) -> None:
        super().__init__()
        self.title_text, self.message_text = title, message
        self.clean_account_ack = clean_account_ack

    def compose(self) -> ComposeResult:
        with Vertical(id="approval_card"):
            yield Static(self.title_text, id="approval_title")
            with VerticalScroll(id="approval_scroll"):
                yield Static(self.message_text, id="approval_message")
            if self.clean_account_ack:
                yield Checkbox("Clean account: never used a trial or intro offer",
                               value=False, id="clean_account_ack")
            with Horizontal(id="approval_actions"):
                yield Button("Cancel", id="cancel")
                yield Button("Continue", id="approve", variant="warning",
                             disabled=self.clean_account_ack)

    def action_scroll_message(self, delta: int) -> None:
        self.query_one("#approval_scroll", VerticalScroll).scroll_relative(y=delta, animate=False)

    @on(Checkbox.Changed, "#clean_account_ack")
    def clean_account_changed(self, event: Checkbox.Changed) -> None:
        self.query_one("#approve", Button).disabled = not event.value

    @on(Button.Pressed, "#approval_actions Button")
    def approve(self, event: Button.Pressed) -> None:
        if event.button.id == "approve" and self.clean_account_ack:
            if not self.query_one("#clean_account_ack", Checkbox).value:
                return
        self.dismiss(event.button.id == "approve")

    def action_cancel(self) -> None:
        self.dismiss(False)


class HelpScreen(ModalScreen[None]):
    """Keep help separate from the current result and payment instructions."""
    BINDINGS = [("escape", "close", "Close"),
                ("pageup", "scroll_help(-5)", "Scroll help up"),
                ("pagedown", "scroll_help(5)", "Scroll help down")]
    CSS = """
    HelpScreen { align: center middle; background: #070d19 75%; }
    #help_card { width: 72; max-width: 94%; height: 22; max-height: 96%; padding: 1 2; border: round #2d3e52; background: #17212e; }
    #help_scroll { height: 1fr; scrollbar-size: 1 1; }
    #help_body { height: auto; }
    #close_help { height: 3; width: 100%; }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="help_card"):
            with VerticalScroll(id="help_scroll"):
                yield Static("[bold]Guided flow[/bold]\n\n"
                         "1. Run Check Device & Offers. Setup may change the Android environment.\n"
                         "2. A fresh matching offer and identified account show the 12-month action. "
                         "This does not prove eligibility or free months.\n"
                         "3. Approve each checkout separately. Verify the actual subscription, charges "
                         "and renewal date in Google Play before Next. Step 5 is optional.\n\n"
                         "Ultra paid ($19.99/month x 3) is a separate group requiring a "
                         "clean account (no previous Google One/AI trial or intro offer). "
                         "It never joins the Pro 24-month sequence.\n\n"
                         "Advanced: Run by step opens separate controls for one step or a guided sequence.\n"
                         "Stop on Steps 0–1 cancels the local check; on paid steps it only prevents later steps.", id="help_body")
            yield Link("Usage & safety guide", url="https://github.com/hoangsvit/google-ai/blob/main/docs/USAGE.md")
            yield Button("Close help", id="close_help")

    @on(Button.Pressed, "#close_help")
    def action_close(self) -> None:
        self.dismiss(None)

    def action_scroll_help(self, delta: int) -> None:
        self.query_one("#help_scroll", VerticalScroll).scroll_relative(y=delta, animate=False)


def is_macos_platform() -> bool:
    return sys.platform == "darwin"


class GoogleAITUI(App[None]):
    TITLE = "ePlus AI Toolkit"
    SUB_TITLE = "ePlus.DEV"
    BINDINGS = [
        ("d", "toggle_debug", "Debug"),
        ("r", "run_selected", "Run step"),
        ("q", "quit_safely", "Quit"),
    ]
    ENABLE_COMMAND_PALETTE = False
    CSS = """
    Screen { background: #0e141d; color: #dce4ef; }
    Footer { background: #151e29; color: #8fa1b8; }
    Button {
        height: 3; min-width: 0; padding: 0 1; border: none;
        background: #202c3a; color: #d1dbe8; text-style: none;
    }
    Button:hover { background: #2c3d50; }
    Button:focus { text-style: bold; outline: solid #67d6b2; }
    Button:disabled { background: #18222e; color: #65758a; }
    #screen { height: 1fr; min-height: 0; padding: 0 2; }
    #brand { height: 3; align: left middle; }
    #brand_title { width: 1fr; height: 1; color: #f0f4fa; }
    #support_label, #support_link { width: auto; height: 1; color: #83b8d9; }
    Link:hover { color: #a3e8d3; text-style: underline; }
    #controls { height: 3; }
    .workflow-step { width: 1fr; height: 2; color: #687d97; border-bottom: solid #253345; }
    .workflow-step.running, .workflow-step.current { color: #72e0bd; text-style: bold; border-bottom: solid #64d6b0; }
    .workflow-step.done { color: #72e0bd; }
    .workflow-step.reviewed { color: #95a9c2; }
    .workflow-step.review { color: #e4bd7c; }
    #stage_6 { color: #f2c48a; }
    #stage_0, #stage_5 { display: none; }
    #details { height: 3; margin-bottom: 1; }
    #device, #account { width: 1fr; height: 3; padding: 0 1; background: #17212e; color: #bdcbdc; }
    #account { margin-left: 1; }
    #content, #results { height: 1fr; width: 100%; min-height: 0; }
    #welcome_panel { height: auto; margin-bottom: 1; }
    #welcome { height: auto; color: #edf4fc; text-style: bold; }
    #quick_hint, #wizard_summary { height: auto; color: #95a9c2; }
    #plan_groups { height: auto; margin: 1 0; }
    #pro_group, #ultra_group {
        width: 1fr; min-height: 3; height: auto; padding: 0 1;
        background: #183328; color: #b5e9d4; border-left: solid #64d6b0;
    }
    #ultra_group { margin-left: 1; background: #38291c; color: #f5d3a0; border-left: solid #dca55f; }
    #payment_notice_compact { height: auto; color: #d0b58c; }
    #status_panel {
        height: 1fr; min-height: 4; padding: 0 1; border: round #2d3e52;
        background: #131d29; overflow-y: auto; scrollbar-size: 1 1;
    }
    #status_heading { height: 1; }
    .section { height: 1; color: #71d9ba; text-style: bold; }
    #status_heading .section { width: 1fr; }
    #elapsed { width: auto; height: 1; color: #758ba5; }
    #state { height: auto; margin-top: 1; color: #f0f4fa; text-style: bold; }
    #message { height: auto; color: #acbed3; }
    #step_result { height: auto; color: #9cd3b9; }
    #review_checklist { display: none; height: auto; margin-top: 1; color: #d0b58c; }
    #activity { height: auto; color: #758ba5; }
    #offers_title { display: none; color: #95a9c2; text-style: bold; margin-top: 1; }
    #offer_view { display: none; height: 8; min-height: 4; margin-top: 1; border: round #2d3e52; background: #0e1722; }
    #debug_log { display: none; height: 8; min-height: 3; margin-top: 1; border: round #253345; background: #0b121b; }
    #manual { display: none; width: 100%; height: 3; }
    #hint { display: none; }
    #action_bar { height: 3; margin-top: 1; }
    #main_actions { width: 2fr; height: 3; }
    #main_actions Button { width: 1fr; height: 3; }
    #quickstart, #continue_initial, #next { background: #64d6b0; color: #0b2620; text-style: bold; }
    #start_ultra { background: #b68447; color: #21180c; text-style: bold; }
    #start_ultra:hover { background: #d5a368; }
    #start_ultra:disabled { background: #3a3025; color: #92806b; }
    #quickstart:disabled, #continue_initial:disabled, #next:disabled { background: #233d37; color: #80958e; }
    #continue_initial, #next, #stop, #finish { display: none; }
    #main_actions #finish { width: 20; margin-right: 1; }
    #stop { color: #e4bd7c; }
    #secondary_actions { height: 1; margin-top: 1; }
    #secondary_actions Button { width: auto; height: 1; min-height: 1; background: transparent; color: #9aadc5; }
    #recheck, #offers_toggle { display: none; margin-right: 2; }
    #advanced_toggle {
        width: 1fr; min-width: 28; height: 3; margin-left: 2;
        border: solid #55738e; background: #1b3043; color: #d8e9f7; text-style: bold;
    }
    #action_bar Button:focus { outline: none; text-style: bold underline; }
    #advanced_toggle:hover { background: #29465e; border: solid #85b5d9; }
    #advanced_toggle:disabled { background: #18222e; border: solid #2d3e52; color: #65758a; }
    #workflow_actions { display: none; height: 1fr; min-height: 0; overflow-y: auto; scrollbar-size: 1 1; }
    #advanced_title { height: 1; text-style: bold; color: #edf4fc; margin-bottom: 1; }
    #form_row { height: auto; }
    .field { width: 1fr; min-width: 12; height: auto; }
    #step_field { margin-left: 1; }
    #mode_label, #advanced_label { height: 1; margin-bottom: 1; color: #95a9c2; }
    #mode, #step { width: 100%; margin: 0; }
    SelectCurrent { background: #17212e; border: tall #253345; }
    #sequence_preview { display: none; height: auto; margin-top: 1; color: #95a9c2; }
    #mode_hint, #read_only, #payment_notice { height: auto; margin-top: 1; color: #d0b58c; }
    #advanced_run_actions { display: none; height: 3; margin-top: 1; }
    #run { width: 100%; height: 3; background: #244d65; color: #e5f3ff; }
    #sequence, #run_all { display: none; }
    Screen.advanced-view #workflow_actions, Screen.advanced-view #advanced_run_actions { display: block; }
    Screen.advanced-view #welcome_panel, Screen.advanced-view #status_panel,
    Screen.advanced-view #main_actions, Screen.advanced-view #recheck, Screen.advanced-view #offers_toggle { display: none; }
    Screen.advanced-view #advanced_toggle { width: 100%; margin-left: 0; }
    #toolbar { height: 1; margin-top: 1; layout: grid; grid-size: 4; grid-columns: 15 29 26 1fr; grid-rows: 1; }
    #toolbar Button { width: 100%; height: 1; min-height: 1; border: none; padding: 0; background: transparent; color: #9aadc5; }
    #toolbar Button:hover, #toolbar Button:focus { background: #243247; color: #e3edf8; }
    #toolbar Button:disabled { color: #52647c; }
    #update_bar { height: 1; margin-top: 1; }
    #update_status { width: 1fr; height: 1; color: #758ba5; }
    #update { width: 22; height: 1; min-height: 1; background: #202c3a; color: #a8bed4; }
    #update_bar.available #update { background: #244d44; color: #8ee8c7; }
    #update_bar.available #update_status { color: #8ee8c7; }
    #credit { height: 1; margin-top: 1; }
    #credit Static, #credit Link { width: auto; height: 1; color: #8ca1bb; }
    Screen.compact #screen { padding: 0 1; }
    Screen.compact #brand, Screen.compact #controls, Screen.compact .workflow-step { height: 1; }
    Screen.compact .workflow-step { border: none; }
    Screen.compact #details { height: 2; margin: 0; }
    Screen.compact #device, Screen.compact #account { height: 2; }
    Screen.compact #quick_hint { display: none; }
    /* Preserve actionable controls on small terminals; plan choice remains
       explicit in the Pro and Ultra buttons, not in tall marketing cards. */
    Screen.compact #plan_groups, Screen.narrow #plan_groups { display: none; }
    Screen.session-active #plan_groups, Screen.session-active #payment_notice_compact { display: none; }
    Screen.compact #welcome_panel { margin-bottom: 0; }
    Screen.compact #state { margin-top: 0; }
    Screen.compact #toolbar, Screen.compact #update_bar, Screen.compact #credit,
    Screen.compact #action_bar, Screen.compact #secondary_actions { margin: 0; }
    Screen.narrow #action_bar { height: auto; layout: vertical; }
    Screen.narrow #main_actions { width: 100%; height: auto; layout: vertical; }
    Screen.narrow #main_actions Button { width: 100%; height: 2; }
    Screen.narrow #advanced_toggle { width: 100%; min-width: 0; height: 2; min-height: 1; margin: 0; border: none; }
    Screen.narrow #action_bar Button:focus { outline: none; text-style: bold underline; }
    Screen.narrow #toolbar { grid-size: 2; grid-columns: 1fr 1fr; grid-rows: 1 1; height: 2; }
    Screen.tiny #support_label, Screen.tiny #credit { display: none; }
    Screen.form-stacked #form_row { layout: vertical; }
    Screen.form-stacked #step_field { margin: 1 0 0 0; }
    Screen.compact.advanced-view #credit { display: none; }
    Screen.compact #advanced_title { margin-bottom: 0; }
    Screen.compact #mode_label, Screen.compact #advanced_label { margin-bottom: 0; }
    Screen.micro #controls { display: none; }
    Screen.micro #main_actions { height: auto; layout: vertical; }
    Screen.micro #main_actions Button { height: 1; min-height: 1; width: 100%; margin: 0; }
    Screen.micro #advanced_toggle { height: 1; }
    """

    def __init__(self, *, repo: Path, selected_step: int = 1,
                 start_sequence: bool = False, initial_debug: bool = False) -> None:
        super().__init__()
        self.repo = repo.resolve()
        self.initial_step = validate_step(selected_step)
        self.macos_mode = is_macos_platform()
        self.start_sequence = start_sequence
        self.debug_visible = initial_debug
        self.busy = False
        self._diagnosing = False
        self._checking_update = False
        self._updating = False
        self._approval_pending = False
        self._update_info: UpdateInfo | None = None
        self.restart_requested = False
        self.sequence = False
        self.current_step: int | None = None
        self._child: subprocess.Popen[str] | None = None
        self._last_output: deque[str] = deque(maxlen=350)
        self._run_output: deque[str] = deque(maxlen=35)
        self._stop_after_step = False
        self._cancel_requested = False
        self._exit_after_step = False
        self._last_outcome: Outcome | None = None
        self._verified_account: str | None = None
        self._started_at: float | None = None
        self._last_activity_at: float | None = None
        self.advanced_visible = False
        self._last_mode = ""
        self._initial_ready = False
        self._check_listed = False
        self._offers_visible = False
        self._wizard_blocker = ""

    def compose(self) -> ComposeResult:
        with Vertical(id="screen"):
            with Horizontal(id="brand"):
                yield Static("[bold]ePlus AI Toolkit[/bold]  [dim]/ ePlus.DEV[/dim]", id="brand_title")
                yield Static("Support: ", id="support_label")
                yield Link("Telegram ↗", url="https://t.me/eplus_news", tooltip="Telegram support channel", id="support_link")
            with Horizontal(id="controls"):
                for stage in STAGES:
                    yield Static(f"○ {self._stage_label(stage.number)}", id=f"stage_{stage.number}", classes="workflow-step")
            with Horizontal(id="details"):
                yield Static("ANDROID DEVICE\nNot checked · MuMu", id="device")
                yield Static("GOOGLE ACCOUNT\nNot checked", id="account")
            with Vertical(id="content"):
                with Vertical(id="results"):
                    with Vertical(id="welcome_panel"):
                        yield Static("Start: check your device & offers", id="welcome")
                        yield Static("One step at a time. Begin with the check below; no checkout is opened.", id="quick_hint")
                        yield Static("", id="wizard_summary", markup=False)
                        with Horizontal(id="plan_groups"):
                            yield Static("PRO FREE TRIAL\nUp to 24 months · Steps 2–5", id="pro_group")
                            yield Static("ULTRA PAID · CLEAN ACCOUNT\nUS$19.99/month × 3 · Step 6", id="ultra_group")
                        yield Static("Pro FREE · Ultra PAID · Check Google Play.", id="payment_notice_compact")
                    with Vertical(id="workflow_actions"):
                        yield Static("Advanced: Run by step", id="advanced_title")
                        with Horizontal(id="form_row"):
                            with Vertical(classes="field", id="mode_field"):
                                yield Static("Run mode", id="mode_label")
                                yield Select([("One step only", "single"), ("From selected step", "from"),
                                              ("All: Steps 2–5", "all")], value="single", id="mode", allow_blank=False)
                            with Vertical(classes="field", id="step_field"):
                                yield Static("Step", id="advanced_label")
                                yield Select([
                                    (f"{stage.number}. {stage.label}", stage.number)
                                    if stage.number < 2 else
                                    (f"PRO FREE | {stage.number}. {stage.label}", stage.number)
                                    if stage.number < 6 else
                                    (f"ULTRA PAID | {stage.number}. {stage.label}", stage.number)
                                    for stage in STAGES], value=self.initial_step, id="step", allow_blank=False)
                        yield Static("", id="sequence_preview")
                        yield Static("Runs one step; no next step is automatic.", id="mode_hint")
                        yield Static("PRO FREE: Steps 2–5 (guided). ULTRA PAID: Step 6 (single only, clean account).", id="read_only")
                        yield Static(
                            "PRO FREE, up to 24 months (not guaranteed): Step 2 (12) + Step 3 (6) + Step 4 (6). "
                            "Three separate US$1 checks may be temporary holds, not one US$3 payment.\n"
                            "ULTRA PAID: Step 6, US$19.99/month for 3 months (then claimed US$199.99/month). "
                            "Use a clean account that never used a Google One/AI trial or intro offer. "
                            "Verify eligibility, charges and renewal on Google Play.",
                            id="payment_notice")
                        yield Button("Run sequence from step", id="sequence")
                        yield Button("Run all", id="run_all")
                    with Horizontal(id="advanced_run_actions"):
                        yield Button("Run selected step", id="run", variant="primary")
                    with Vertical(id="status_panel"):
                        with Horizontal(id="status_heading"):
                            yield Static("LIVE STATUS", classes="section")
                            yield Static("Elapsed: --", id="elapsed")
                        yield Static("Ready — no check started", id="state")
                        yield Static("Press Check Device & Offers to begin.", id="message")
                        yield Static("", id="step_result")
                        yield Static("Verify in Google Play: account, charges/holds, subscription and renewal date.\n"
                                     "A submitted checkout is not a verified activation or extension.", id="review_checklist")
                        yield Static("AVAILABLE OFFERS · FIRST PHASE ONLY", id="offers_title")
                        yield RichLog(id="offer_view", wrap=True, highlight=False, markup=False)
                        yield Static("Waiting for your action.", id="activity")
                        yield Button("Completed action on Android", id="manual", disabled=True)
                        yield RichLog(id="debug_log", wrap=True, highlight=False, markup=False)
                        yield Static("", id="hint")
                    with Horizontal(id="action_bar"):
                        with Horizontal(id="main_actions"):
                            yield Button("Check Device & Offers", id="quickstart", variant="success")
                            yield Button("Continue: 12-month stage →", id="continue_initial", disabled=True)
                            yield Button("Ultra Paid · $19.99/mo →", id="start_ultra")
                            yield Button("Finish here", id="finish", disabled=True)
                            yield Button("Verified in Google Play → Next", id="next", disabled=True)
                            yield Button("Stop after current step", id="stop", disabled=True)
                        yield Button("Advanced: Run by step →", id="advanced_toggle")
            with Horizontal(id="secondary_actions"):
                yield Button("Check again", id="recheck")
                yield Button("View offers", id="offers_toggle")
            with Horizontal(id="toolbar"):
                yield Button("Help & Guide", id="nav_help")
                yield Button("Diagnose Android connection", id="diagnose")
                yield Button("Show technical details", id="debug")
                yield Button("Exit toolkit", id="exit")
            with Horizontal(id="update_bar"):
                yield Static("Checking for updates...", id="update_status", markup=False)
                yield Button("Check for updates", id="update", disabled=True)
            with Horizontal(id="credit"):
                yield Static("Original ")
                yield Link("@gylive", url="https://github.com/gylive", tooltip="Original author on GitHub", id="original_author")
                yield Static("   ·   Maintained ")
                yield Link("@hoangsvit", url="https://github.com/hoangsvit", tooltip="Maintainer on GitHub", id="maintainer")
        yield Footer()

    @staticmethod
    def _stage_label(step: int) -> str:
        return {0: "Environment", 1: "Check", 2: "12 months", 3: "+6 months",
                4: "+6 #2", 5: "Optional +6", 6: "Ultra Paid"}[step]

    def on_resize(self, event) -> None:
        self.screen_stack[0].set_class(event.size.height < 27, "compact")
        self.screen_stack[0].set_class(event.size.width < 90, "narrow")
        self.screen_stack[0].set_class(event.size.width < 62, "tiny")
        self.screen_stack[0].set_class(event.size.width < 58, "micro")
        self.screen_stack[0].set_class(event.size.width < 52, "form-stacked")
        self._refresh_toolbar_labels()
        if self.is_mounted and self.query("#main_actions"):
            self._render_wizard()

    def _refresh_toolbar_labels(self) -> None:
        if not self.is_mounted or not self.query("#diagnose"):
            return
        self.query_one("#diagnose", Button).label = (
            "Diagnose Android" if self.size.width < 62 else "Diagnose Android connection"
        )
        self.query_one("#debug", Button).label = (
            ("Hide details" if self.debug_visible else "Show details") if self.size.width < 58
            else ("Hide technical details" if self.debug_visible else "Show technical details")
        )
        self.query_one("#advanced_toggle", Button).label = (
            "← Back to guided flow" if self.advanced_visible else "Advanced: Run by step →"
        )
        self.query_one("#offers_toggle", Button).label = (
            "Hide offers" if self._offers_visible else ("Offers" if self.size.width < 62 else "View offers")
        )

    def _render_wizard(self) -> None:
        """Present the one meaningful next action; never run it automatically."""
        locked = self.busy or self._diagnosing or self._updating or self._approval_pending
        review = bool(self.sequence and self.current_step is not None and self.current_step < 5
                      and self._last_outcome and self._last_outcome.can_review and not self._stop_after_step)
        paid_result = bool(self.current_step is not None and self.current_step >= 2 and self._last_outcome)
        self.query_one("#quickstart", Button).display = not self.busy and not review and not self._initial_ready
        self.query_one("#start_ultra", Button).display = not self.busy and not review
        self.query_one("#start_ultra", Button).disabled = locked or self.sequence
        self.query_one("#continue_initial", Button).display = self._initial_ready and not self.busy and not review
        self.query_one("#continue_initial", Button).disabled = locked or not self._initial_ready or self.sequence
        self.query_one("#quickstart", Button).disabled = locked or self.sequence
        self.query_one("#next", Button).display = review and not self.busy
        self.query_one("#next", Button).disabled = locked or not review
        self.query_one("#finish", Button).display = review and not self.busy
        self.query_one("#finish", Button).disabled = locked or not review
        self.query_one("#recheck", Button).display = self._check_listed and not review and not self.advanced_visible
        self.query_one("#recheck", Button).disabled = locked or self.sequence
        self.query_one("#offers_toggle", Button).display = self._check_listed and not review and not self.advanced_visible
        self.query_one("#offers_toggle", Button).disabled = locked or self.sequence
        self.query_one("#advanced_toggle", Button).disabled = locked or self.sequence
        self.query_one("#diagnose", Button).disabled = locked or self.sequence
        for selector in ("#run", "#sequence", "#run_all", "#mode"):
            self.query_one(selector).disabled = locked or self.sequence
        self.query_one("#step", Select).disabled = locked or self.sequence or self.query_one("#mode", Select).value == "all"
        self.query_one("#review_checklist", Static).display = paid_result and not self.busy
        title, summary = "Start: check your device & offers", self._wizard_blocker
        if self.busy and self.current_step is not None:
            title = f"Running Step {self.current_step} · {STAGES[self.current_step].label}"
            summary = "Wait for the current step. No later stage starts automatically."
        elif review:
            next_step = self.current_step + 1
            title = ("Review Step 4 · Step 5 is optional" if next_step == 5
                     else f"Verify Step {self.current_step} in Google Play → Next: Step {next_step}")
            summary = ("Step 5 is optional. Finish here, or verify and review Step 5."
                       if next_step == 5 else f"Next after your verification: Step {next_step} · {STAGES[next_step].label}.")
        elif self._initial_ready:
            title = "Check complete · next: the 12-month stage"
            summary = "Matching Pro trial offer found and Play account identified. Ultra paid is a separate group. Google Play still decides eligibility."
            self._set_workflow(2, "current")
        elif paid_result:
            title = "Review the actual outcome in Google Play"
        self.query_one("#welcome", Static).update(title)
        if self.busy:
            hint = "Follow any Android prompts. No later stage starts automatically."
        elif paid_result:
            hint = "Review the actual subscription, charges and renewal date in Google Play."
        elif self._initial_ready:
            hint = "Review the initial stage before any checkout. You will approve it separately."
        else:
            hint = "One step at a time. Start with the check; verify each later checkout in Google Play."
        self.query_one("#quick_hint", Static).update(hint)
        self.query_one("#wizard_summary", Static).update(summary)
        self.query_one("#wizard_summary", Static).display = bool(summary) and not (
            self.size.height < 27 or self.size.width < 62
        )
        self.refresh_bindings()

    @on(Button.Pressed, "#continue_initial")
    def continue_initial_pressed(self) -> None:
        if (not self._initial_ready or self.busy or self._diagnosing or self._updating
                or self._approval_pending or self.sequence or self.advanced_visible):
            return
        self._confirm_stage(2, True)

    @on(Button.Pressed, "#recheck")
    def recheck_pressed(self) -> None:
        if self.busy or self._diagnosing or self._updating or self._approval_pending or self.sequence or self.advanced_visible:
            return
        self._confirm_stage(1, False)

    @on(Button.Pressed, "#offers_toggle")
    def offers_pressed(self) -> None:
        if not self._check_listed or self.busy or self.advanced_visible:
            return
        self._offers_visible = not self._offers_visible
        self.query_one("#offers_title", Static).display = self._offers_visible
        self.query_one("#offer_view", RichLog).display = self._offers_visible
        self._refresh_toolbar_labels()

    @on(Button.Pressed, "#finish")
    def finish_pressed(self) -> None:
        if self.busy or self._diagnosing or self._updating or self._approval_pending or not self.sequence:
            return
        self.sequence = False
        self._stop_after_step = True
        self._initial_ready = False
        self._set_message("Sequence ended here. No later stage was started. Verify the actual subscription and charges in Google Play.")
        self.screen_stack[0].remove_class("session-active")
        self._render_wizard()
        self._refresh_update_controls()

    @on(Button.Pressed, "#nav_home")
    def home_pressed(self) -> None:
        if not self.busy:
            self._set_message("Select Check Device & Offers to begin.")

    @on(Button.Pressed, "#nav_quick")
    def quick_pressed(self) -> None:
        self.quickstart_pressed()

    @on(Button.Pressed, "#nav_help")
    def help_pressed(self) -> None:
        if isinstance(self.screen, HelpScreen):
            return
        self.push_screen(HelpScreen())

    @on(Button.Pressed, "#diagnose")
    def diagnose_pressed(self) -> None:
        if self.busy or self._diagnosing or self._updating or self._approval_pending or self.sequence:
            return
        self._diagnosing = True
        if self._initial_ready:
            self._set_workflow(2, "pending")
        self._initial_ready = False
        self._check_listed = False
        self._offers_visible = False
        self.query_one("#offers_title", Static).display = False
        self.query_one("#offer_view", RichLog).display = False
        self._wizard_blocker = "Run a fresh offer check after connection diagnostics."
        self.current_step = None
        self._last_outcome = None
        self._show_advanced(False)
        self._render_wizard()
        self._refresh_update_controls()
        self.query_one("#diagnose", Button).disabled = True
        self.query_one("#quickstart", Button).disabled = True
        self.query_one("#run", Button).disabled = True
        self._set_status("Inspecting Android connection...")
        self._set_message(
            "Checking local ADB, Android transport and Google One. No checkout, "
            "installation or emulator reset; adb devices may start the local ADB server."
        )
        self.inspect_android_connection()

    @work(thread=True, exclusive=True, group="android-connection")
    def inspect_android_connection(self) -> None:
        try:
            diagnosis = inspect_connection()
        except Exception:
            diagnosis = ConnectionDiagnosis(
                "error", "Connection check could not complete", (),
                "Check the ADB installation and try again. No checkout was started.",
            )
        self.call_from_thread(self._diagnosis_done, diagnosis)

    def _diagnosis_done(self, diagnosis: ConnectionDiagnosis) -> None:
        self._diagnosing = False
        self._refresh_update_controls()
        self.query_one("#diagnose", Button).disabled = False
        self.query_one("#quickstart", Button).disabled = False
        self.query_one("#run", Button).disabled = False
        self._set_status(diagnosis.headline)
        self._set_message(diagnosis.guidance)
        self.query_one("#step_result", Static).update("\n".join(diagnosis.details))
        self.query_one("#offers_title", Static).display = False
        self.query_one("#offer_view", RichLog).display = False
        self._render_wizard()

    def on_mount(self) -> None:
        self.set_interval(1, self._refresh_elapsed)
        self._begin_update_check()
        if self.macos_mode:
            self.query_one("#device", Static).update("ANDROID DEVICE\nADB • Auto-detect")
            self.query_one("#quick_hint", Static).update(
                "Check Android and Google AI offers before any subscription step."
            )
            self.query_one("#read_only", Static).update(
                "Steps 2–5 can charge money. Confirm account, future price and renewal date."
            )
        self.query_one("#debug_log", RichLog).display = self.debug_visible
        self._refresh_toolbar_labels()
        if self.start_sequence:
            self.query_one("#mode", Select).value = "from"
        self._update_run_mode()
        self._set_workflow(1, "current")
        self._render_wizard()
        self.query_one("#quickstart", Button).focus()

    def _refresh_update_controls(self) -> None:
        button = self.query_one("#update", Button)
        available = self._update_info is not None and self._update_info.state == "available"
        button.label = "Update & Restart" if available else "Check for updates"
        button.disabled = (self.busy or self._diagnosing or self._updating
                           or self._checking_update or self._approval_pending or self.sequence)

    def _begin_update_check(self) -> None:
        if self._checking_update or self._updating:
            return
        self._checking_update = True
        self.query_one("#update_status", Static).update("Checking for updates...")
        self._refresh_update_controls()
        self.check_app_update()

    @work(thread=True, exclusive=True, group="app-update-check")
    def check_app_update(self) -> None:
        info = check_for_update(self.repo)
        self.call_from_thread(self._update_check_done, info)

    def _update_check_done(self, info: UpdateInfo) -> None:
        self._checking_update = False
        self._update_info = info
        status = self.query_one("#update_status", Static)
        message = info.message
        if message == "Automatic updates require main. Update development branches manually.":
            message = "Development build · Git"
        status.update(message)
        self.query_one("#update_bar").set_class(info.state == "available", "available")
        status.tooltip = info.message
        self._refresh_update_controls()

    @on(Button.Pressed, "#update")
    def update_pressed(self) -> None:
        if (self.busy or self._diagnosing or self._updating or self._checking_update
                or self._approval_pending or self.sequence):
            return
        if self._update_info is None or self._update_info.state != "available":
            self._begin_update_check()
            return
        self._updating = True
        self._render_wizard()
        self._refresh_update_controls()
        for selector in ("#quickstart", "#diagnose", "#run", "#sequence", "#run_all",
                         "#mode", "#step", "#advanced_toggle", "#exit"):
            self.query_one(selector).disabled = True
        self.query_one("#update_status", Static).update("Updating... Please wait.")
        self._set_message("Installing the displayed version. The dashboard will reopen; no step will resume.")
        self.apply_app_update(self._update_info)

    @work(thread=True, exclusive=True, group="app-update-install")
    def apply_app_update(self, info: UpdateInfo) -> None:
        try:
            # Ensure a native restart is possible before changing source files.
            restart_command(self.repo)
            install_update(self.repo, info)
        except UpdateError as error:
            self.call_from_thread(self._app_update_done, str(error))
        else:
            self.call_from_thread(self._app_update_done, None)

    def _app_update_done(self, error: str | None) -> None:
        self._updating = False
        if error is None:
            self.restart_requested = True
            self.exit()
            return
        self._update_check_done(UpdateInfo("error", error))
        for selector in ("#quickstart", "#diagnose", "#run", "#sequence", "#run_all",
                         "#mode", "#step", "#advanced_toggle", "#exit"):
            self.query_one(selector).disabled = False
        self._update_run_mode()
        self._set_message(error)
        self._render_wizard()

    @on(Button.Pressed, "#advanced_toggle")
    def advanced_pressed(self) -> None:
        if self.busy or self._diagnosing or self._updating or self._approval_pending or self.sequence:
            return
        self._show_advanced(not self.advanced_visible)
        self._update_run_mode()
        if self.advanced_visible:
            self.query_one("#mode", Select).focus()
        else:
            self.query_one("#continue_initial" if self._initial_ready else "#quickstart", Button).focus()

    def _show_advanced(self, visible: bool) -> None:
        self.advanced_visible = visible
        self.screen_stack[0].set_class(visible, "advanced-view")
        self.query_one("#workflow_actions").display = visible
        self.query_one("#advanced_toggle", Button).label = (
            "← Back to guided flow" if visible else "Advanced: Run by step →"
        )
        self._refresh_toolbar_labels()
        self.refresh_bindings()
        self._render_wizard()

    @on(Select.Changed, "#mode")
    def mode_changed(self, event: Select.Changed) -> None:
        self._update_run_mode()

    @on(Select.Changed, "#step")
    def step_changed(self, event: Select.Changed) -> None:
        self._update_run_mode()

    def _update_run_mode(self) -> None:
        if self.busy or self._diagnosing or self._updating or not self.query("#mode"):
            return
        mode = self.query_one("#mode", Select).value
        selector = self.query_one("#step", Select)
        step = selector.value
        if mode != self._last_mode:
            self._last_mode = str(mode)
            stages = STAGES if mode == "single" else STAGES[2:6]
            selector.set_options([
                (f"{stage.number}. {stage.label}", stage.number)
                if stage.number < 2 else
                (f"PRO FREE | {stage.number}. {stage.label}", stage.number)
                if stage.number < 6 else
                (f"ULTRA PAID | {stage.number}. {stage.label}", stage.number)
                for stage in stages])
            selector.value = step if step in [stage.number for stage in stages] else stages[0].number
        if mode == "all":
            selector.value = 2
        step = selector.value
        self.query_one("#step_field").display = mode != "all"
        self.query_one("#sequence_preview", Static).display = mode != "single"
        if mode == "all":
            selector.disabled = True
            self.query_one("#run", Button).label = "Run all: Steps 2-5"
            hint = "Starts Step 2; requires review before every later checkout."
        elif mode == "from":
            selector.disabled = False
            self.query_one("#run", Button).label = "Run from selected step"
            hint = ("Choose Step 2-5. Each later checkout requires verification."
                    if step in (0, 1) else "Continue from this step; verify each checkout before Next.")
        else:
            selector.disabled = False
            self.query_one("#run", Button).label = "Run selected step"
            hint = ("Step 6 is separate PAID Ultra; requires clean account and manual Google Play approval."
                    if step == 6 else
                    f"Run only Step {step}. No later step is automatic. Pro Steps 2–5 may charge money.")
        self.query_one("#mode_hint", Static).update(hint)
        if mode != "single" and isinstance(step, int):
            path = " → ".join(str(number) for number in range(step, 5))
            self.query_one("#sequence_preview", Static).update(
                f"Planned stages: {path + ' → ' if path else ''}5 (optional). Confirm and verify each stage separately."
            )

    def action_toggle_advanced(self) -> None:
        self.advanced_pressed()

    def _refresh_elapsed(self) -> None:
        if not self.busy or self._started_at is None or not self.is_running or not self.query("#elapsed"):
            return
        elapsed = int(time.monotonic() - self._started_at)
        self.query_one("#elapsed", Static).update(f"Elapsed: {elapsed // 60:02d}:{elapsed % 60:02d}")
        if self._last_activity_at is not None:
            idle = int(time.monotonic() - self._last_activity_at)
            if idle >= 30:
                self.query_one("#activity", Static).update(
                    f"No new output for {idle}s. Check MuMu or technical details."
                )

    def _set_workflow(self, step: int, state: str) -> None:
        marker = {"running": "●", "done": "✓", "review": "!", "reviewed": "·"}.get(state, "○")
        widget = self.query_one(f"#stage_{step}", Static)
        widget.set_classes(f"workflow-step {state}")
        widget.tooltip = ("Reviewed in Google Play by you; outcome not independently verified."
                          if state == "reviewed" else STAGES[step].label)
        widget.update(
            f"{marker} {self._stage_label(step)}"
        )

    def _set_message(self, value: str) -> None:
        self.query_one("#message", Static).update(value)

    def _set_status(self, value: str) -> None:
        self.query_one("#state", Static).update(value)

    def _selected(self) -> int:
        return validate_step(int(self.query_one("#step", Select).value))

    def _confirm_stage(self, step: int, sequence: bool,
                       previous_verified: bool = False) -> None:
        if self.busy or self._diagnosing or self._updating or self._approval_pending:
            return
        if self.sequence and self._last_outcome and self._last_outcome.can_review and not previous_verified:
            return
        if step == 6:
            if sequence:
                self._set_message("Ultra PAID is separate: choose one step only, not the Pro sequence.")
                return
            title = "ULTRA PAID · US$19.99/month x 3 · clean account"
            message = (
                "SEPARATE PAID GROUP; NOT part of the Pro 24-month free trial.\n\n"
                "The original source requires a CLEAN account that has NEVER used any "
                "Google One/AI trial or introductory promotion. Self-attest using the checkbox; "
                "the toolkit cannot check past trial history. Google Play decides eligibility.\n\n"
                "Source claims US$19.99/month for 3 months, then US$199.99/month. "
                "Check the actual amount, currency, renewal terms and account in Google Play. "
                "The toolkit does NOT auto-tap Subscribe for Ultra. "
                "No specific MuMu 12 / Android 12 requirement."
            )
        elif step == 2:
            title = "Start initial 12-month checkout?"
            message = ("Confirm this Google Play account has NO active Google One subscription. "
                       "This step can automatically press Subscribe and create real charges.")
        elif step >= 3:
            title = f"Start Step {step} (+6 months)?"
            message = ("Google AI Pro must already be active. Verify the previous "
                       "subscription and renewal date in Google Play. Google may reject "
                       "additional free offers or apply paid renewal terms.")
        else:
            self._start(step, sequence)
            return
        if step in (2, 3, 4):
            number = step - 1
            message += (
                f"\n\nCard check {number} of 3 in the reported example: "
                "about US$1 each, NOT one US$3 payment. "
                "It may be a temporary hold, not a final charge. "
                "Verify the amount and renewal date in Google Play. "
                "24 months is not guaranteed."
            )
        elif step == 5:
            message += (
                "\n\nStep 5 is optional, outside the 3 x US$1 / 24-month example. "
                "Check the actual amount and renewal terms in Google Play."
            )
        if previous_verified:
            message = ("Confirm the previous stage ACTUALLY changed the Google Play "
                       "subscription/renewal date. " + message)
        self._approval_pending = True
        self._refresh_update_controls()
        self._render_wizard()

        def confirmed(approved: bool) -> None:
            self._approval_pending = False
            self._refresh_update_controls()
            self._render_wizard()
            if approved:
                if previous_verified and self.current_step is not None:
                    self._set_workflow(self.current_step, "reviewed")
                self._start(step, sequence)

        self.push_screen(Approval(title, message, clean_account_ack=(step == 6)), confirmed)

    @on(Button.Pressed, "#quickstart")
    def quickstart_pressed(self) -> None:
        if self.advanced_visible or self._initial_ready or self.sequence:
            return
        self._confirm_stage(1, False)

    @on(Button.Pressed, "#start_ultra")
    def ultra_pressed(self) -> None:
        if (self.advanced_visible or self.busy or self._diagnosing or self._updating
                or self._approval_pending or self.sequence):
            return
        self._confirm_stage(6, False)

    @on(Button.Pressed, "#run")
    def selected_pressed(self) -> None:
        if (not self.advanced_visible or self.busy or self._diagnosing or self._updating
                or self._approval_pending or self.sequence):
            return
        mode = self.query_one("#mode", Select).value
        if mode == "all":
            self._confirm_stage(2, True)
        elif mode == "from":
            step = self._selected()
            if step < 2:
                self._set_message("Choose Step 2-5 to start a guided checkout sequence.")
                return
            self._confirm_stage(step, True)
        else:
            self._confirm_stage(self._selected(), False)

    @on(Button.Pressed, "#sequence")
    def sequence_pressed(self) -> None:
        if not self.advanced_visible or self.busy or self._diagnosing or self._updating or self._approval_pending or self.sequence:
            return
        step = self._selected()
        if step < 2 or step > 5:
            self._set_message("Only Pro Steps 2–5 can form a sequence. Ultra Step 6 is separate.")
            return
        self._confirm_stage(step, True)

    @on(Button.Pressed, "#next")
    def next_pressed(self) -> None:
        if (self.busy or self._diagnosing or self._updating or self._approval_pending
                or not self.sequence or self.current_step is None):
            return
        if self._last_outcome is None or not self._last_outcome.can_review:
            return
        next_step = self.current_step + 1
        if next_step > 5:
            return
        self._confirm_stage(next_step, True, previous_verified=True)

    @on(Button.Pressed, "#stop")
    def stop_pressed(self) -> None:
        if not self.busy:
            return
        if self.current_step in (0, 1):
            self._cancel_readonly()
        else:
            self._stop_after_step = True
            self._set_message("No later step will run. Finish or review the checkout on Android; the current transaction cannot be force-stopped.")
            self.query_one("#stop", Button).disabled = True

    def _cancel_readonly(self) -> None:
        if not self.busy or self.current_step not in (0, 1) or self._cancel_requested:
            return
        self._cancel_requested = True
        self._stop_after_step = True
        self._set_status("Stopping read-only check...")
        self._set_message("Stopping the local check; no checkout was started.")
        self.query_one("#stop", Button).disabled = True
        self.terminate_readonly_child()

    @work(thread=True, exclusive=True, group="read-only-cancel")
    def terminate_readonly_child(self) -> None:
        child = self._child
        if child is None or child.poll() is not None:
            return
        try:
            if os.name == "nt":
                result = subprocess.run(["taskkill", "/PID", str(child.pid), "/T", "/F"],
                                        capture_output=True, text=True, timeout=8, check=False)
                if result.returncode != 0 and child.poll() is None:
                    raise OSError("taskkill failed")
            else:
                os.killpg(child.pid, signal.SIGTERM)
        except (OSError, subprocess.TimeoutExpired) as error:
            self.call_from_thread(self._set_message,
                                  f"Cannot stop the check: {error}. Open technical details.")

    @on(Button.Pressed, "#exit")
    def exit_pressed(self) -> None:
        self.action_quit_safely()

    @on(Button.Pressed, "#manual")
    def manual_pressed(self) -> None:
        child = self._child
        if child and child.stdin:
            try:
                child.stdin.write("\n")
                child.stdin.flush()
                self.query_one("#manual", Button).disabled = True
                self.query_one("#manual", Button).display = False
            except (OSError, ValueError):
                self._set_message("Could not continue the Android prompt. See Debug.")

    @on(Button.Pressed, "#debug")
    def debug_pressed(self) -> None:
        self.action_toggle_debug()

    def action_toggle_debug(self) -> None:
        self.debug_visible = not self.debug_visible
        log = self.query_one("#debug_log", RichLog)
        if self.debug_visible:
            # Rebuild from the bounded current-run buffer: lines received while
            # details were hidden must not disappear or be duplicated.
            log.clear()
            for line in self._last_output:
                log.write(line)
        log.display = self.debug_visible
        self._refresh_toolbar_labels()

    def action_run_selected(self) -> None:
        if self.advanced_visible and self.screen is self.screen_stack[0]:
            self.selected_pressed()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "run_selected":
            return (self.advanced_visible and not self.busy and not self._diagnosing
                    and not self._updating and not self._approval_pending and not self.sequence
                    and self.screen is self.screen_stack[0])
        return super().check_action(action, parameters)

    def action_quit(self) -> None:
        self.action_quit_safely()

    def action_quit_safely(self) -> None:
        if self._updating:
            self._set_message("Updating source files. Please wait for the update to finish before exiting.")
            return
        if not self.busy:
            self.exit()
            return
        self._exit_after_step = True
        if self.current_step in (0, 1):
            self._cancel_readonly()
            self._set_message("Stopping read-only check; toolkit will exit when it stops.")
        else:
            self._stop_after_step = True
            self._set_message("Exit queued after the current checkout. Review Google Play on Android; no later step will start.")
            self.query_one("#stop", Button).disabled = True
            self.query_one("#exit", Button).disabled = True

    def _start(self, step: int, sequence: bool) -> None:
        if self.busy or self._diagnosing or self._updating or self._approval_pending:
            return
        self.busy = True
        self.sequence = sequence
        if self._initial_ready:
            self._set_workflow(2, "pending")
        self._initial_ready = False
        self._check_listed = False
        self._offers_visible = False
        self._wizard_blocker = ""
        self._show_advanced(False)
        self.screen_stack[0].add_class("session-active")
        self._refresh_update_controls()
        self.current_step = step
        self._stop_after_step = False
        self._cancel_requested = False
        self._exit_after_step = False
        self._last_outcome = None
        self._verified_account = None
        self._last_output.clear()
        self._run_output.clear()
        self.query_one("#debug_log", RichLog).clear()
        self.query_one("#offer_view", RichLog).clear()
        self.query_one("#offer_view", RichLog).display = False
        self.query_one("#offers_title", Static).display = False
        self.query_one("#device", Static).update(
            "ANDROID DEVICE\nADB • Auto-detect" if self.macos_mode
            else "ANDROID DEVICE\nMuMu • Auto-detect"
        )
        self.query_one("#account", Static).update("GOOGLE ACCOUNT\nNot checked")
        self.query_one("#manual", Button).display = False
        self.query_one("#manual", Button).disabled = True
        self._started_at = time.monotonic()
        self._last_activity_at = self._started_at
        self.query_one("#elapsed", Static).update("Elapsed: 00:00")
        self.query_one("#activity", Static).update(
            "Connecting to Android diagnostics..." if self.macos_mode
            else "Connecting to MuMu and preparing tools..."
        )
        self.query_one("#quickstart", Button).disabled = True
        self.query_one("#start_ultra", Button).disabled = True
        self.query_one("#diagnose", Button).disabled = True
        self.query_one("#run", Button).disabled = True
        self.query_one("#sequence", Button).disabled = True
        self.query_one("#mode", Select).disabled = True
        self.query_one("#step", Select).disabled = True
        self.query_one("#next", Button).disabled = True
        self.query_one("#stop", Button).disabled = False
        self.query_one("#stop", Button).label = "Stop check" if step <= 1 else "Stop after this step"
        self.query_one("#stop", Button).display = True
        self.query_one("#next", Button).display = False
        self.query_one("#step_result", Static).update(f"Step {step} · {STAGES[step].label}")
        self._set_workflow(step, "running")
        self._set_status(
            "Running — check Android if prompted" if self.macos_mode
            else "Running — check MuMu if prompted"
        )
        self._set_message("Preparing tools and checking Google Play. Missing dependencies are installed automatically.")
        if step == 1:
            for number in range(2, 6):
                self._set_workflow(number, "pending")
        self._render_wizard()
        self.run_stage(step)

    def _execute(self, command: list[str]) -> int:
        """Run the existing engine and send output to the TUI without blocking it."""
        # Windows Python defaults to a locale code page when stdout is piped.
        # Force UTF-8 for nested setup/CLI Python processes without changing billing logic.
        child_env = os.environ.copy()
        child_env["PYTHONIOENCODING"] = "utf-8"
        child_env["PYTHONUTF8"] = "1"
        if self._cancel_requested:
            return -1
        options = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
                   if os.name == "nt" else {"start_new_session": True})
        with subprocess.Popen(
            command, cwd=self.repo, env=child_env, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, stdin=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace", bufsize=1, **options
        ) as child:
            self._child = child
            if child.stdout:
                for line in child.stdout:
                    try:
                        self.call_from_thread(self._received, line.rstrip("\r\n"))
                    except RuntimeError:
                        return -1
            return child.wait()

    @work(thread=True, exclusive=True)
    def run_stage(self, step: int) -> None:
        try:
            if not self.macos_mode and needs_setup():
                self.call_from_thread(self._set_status, "Setting up...")
                self.call_from_thread(self._set_message,
                                      "Preparing Frida and ADB. You do not need a separate setup command.")
                setup = self.repo / "setup_env.py"
                if not setup.is_file():
                    raise FileNotFoundError("setup_env.py is missing from the project directory")
                setup_code = self._execute([sys.executable, str(setup)])
                if self._cancel_requested:
                    self.call_from_thread(self._finished, step, Outcome("cancelled", "Check stopped", "Cancelled read-only check."), None)
                    return
                if setup_code != 0:
                    self.call_from_thread(
                        self._finished, step,
                        Outcome("setup_failed", "Setup did not finish",
                                "Open Debug, check the setup issue, then retry. No checkout was started."),
                        None)
                    return

            # Never treat a report from setup or a previous invocation as the
            # outcome of the selected step.
            if self._cancel_requested:
                self.call_from_thread(self._finished, step, Outcome("cancelled", "Check stopped", "Cancelled read-only check."), None)
                return
            started = time.time()
            command = command_for_step(step, self.repo)
            return_code = self._execute(command)
            if self._cancel_requested:
                self.call_from_thread(self._finished, step, Outcome("cancelled", "Check stopped", "Cancelled read-only check."), None)
                return
            report = read_fresh_report(self.repo / "ultra0-report", step, started,
                                       expected_account=self._verified_account)
            result = outcome_for_stage(step, return_code, report)
            self.call_from_thread(self._finished, step, result, report)
        except Exception as error:
            result = Outcome("exception", "Could not start the tool",
                             f"{type(error).__name__}: {error}. See Debug and verify Google Play.")
            self.call_from_thread(self._finished, step, result, None)
        finally:
            self._child = None

    def _received(self, line: str) -> None:
        if not line:
            return
        self._last_output.append(line)
        self._run_output.append(line)
        self._last_activity_at = time.monotonic()
        lower = line.lower()
        if "frida" in lower or "setup" in lower:
            phase = "Preparing Android tools..."
        elif "adb" in lower or "device" in lower:
            phase = "Checking Android device..."
        elif "offer" in lower or "billing" in lower or "google one" in lower:
            phase = "Checking available offers..."
        elif "account" in lower or "play store" in lower:
            phase = "Checking Google Play account..."
        else:
            phase = "Process responding. Details available in technical log."
        self.query_one("#activity", Static).update(phase)
        if self.debug_visible:
            self.query_one("#debug_log", RichLog).write(line)
        if re.search(r"Action required:|Press Enter to continue", line, re.I):
            btn = self.query_one("#manual", Button)
            btn.display = True
            btn.disabled = False
            self._set_message("Complete the requested action on Android, then click Completed.")
        if re.search(r"\bDevice\s+(emulator-\d+|[0-9.]+:\d+)\s*$", line):
            self.query_one("#device", Static).update("Device  •  " + escape(line.split()[-1]))
        # Trust only the structured PowerShell "Account <email>" status line,
        # not arbitrary log messages containing an email address.
        account = re.match(
            r"^\s*Account\s+([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})\s*$",
            line,
        )
        if account:
            self._verified_account = account.group(1).lower()
            self.query_one("#account", Static).update(
                "Account  •  " + escape(mask_email(self._verified_account))
            )

    def _visible_failure(self) -> str:
        """Show a concise CLI error without exposing account emails."""
        for raw in reversed(self._run_output):
            line = re.sub(r"\x1b\[[0-9;]*m", "", raw).strip()
            if not line:
                continue
            if re.search(r"error|failed|missing|not found|cannot|unable|offline|unauthorized|issue|stopped|device", line, re.I):
                line = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[account hidden]", line)
                return line[:220]
        return ""

    def _finished(self, step: int, outcome: Outcome, report: dict | None) -> None:
        self.busy = False
        self._last_outcome = outcome
        self.query_one("#manual", Button).display = False
        self.query_one("#manual", Button).disabled = True
        self.query_one("#quickstart", Button).disabled = False
        self.query_one("#diagnose", Button).disabled = False
        self.query_one("#run", Button).disabled = False
        self.query_one("#sequence", Button).disabled = False
        self.query_one("#mode", Select).disabled = False
        self.query_one("#step", Select).disabled = False
        self._update_run_mode()
        self.query_one("#stop", Button).disabled = True
        self.query_one("#stop", Button).display = False
        self.query_one("#exit", Button).disabled = False
        self._started_at = None
        self.query_one("#activity", Static).update("Step finished. Review the result above.")
        self._set_workflow(step, "done" if outcome.code in ("listed", "environment_ok") else "review")
        self._set_status(outcome.title)
        instruction = outcome.instruction
        if outcome.code in ("tool_error", "exception", "missing_report", "setup_failed"):
            diagnostic = self._visible_failure()
            if diagnostic:
                instruction = f"{instruction}  Last CLI message: {diagnostic}"
        self._set_message(instruction)
        if step == 1:
            self._wizard_blocker = initial_checkout_blocker(outcome, report, self._verified_account)
            self._initial_ready = not self._wizard_blocker
            self._check_listed = bool(outcome.code == "listed" and isinstance(report, dict) and report.get("status") == "listed")
            self._set_workflow(1, "done" if self._initial_ready else "review")
            if outcome.code == "listed" and self._wizard_blocker:
                self._set_status("Offer check needs attention")
                self._set_message(self._wizard_blocker)
            self.query_one("#step_result", Static).update(report_summary(report))
            if self._check_listed:
                self.query_one("#device", Static).update("ANDROID DEVICE\nQueried for this offer check")
                offer_view = self.query_one("#offer_view", RichLog)
                offer_view.clear()
                for item in offer_explorer_lines(report):
                    offer_view.write(item)
                offer_view.display = False
                self.query_one("#offers_title", Static).display = False
            if isinstance(report, dict):
                detected = report.get("detected_play_account")
                if isinstance(detected, str) and detected:
                    self.query_one("#account", Static).update(
                        "Account  •  " + escape(mask_email(detected))
                    )
        if outcome.can_review and self.sequence and step < 5 and not self._stop_after_step:
            self.query_one("#next", Button).disabled = False
            self.query_one("#next", Button).display = True
        else:
            self.query_one("#next", Button).disabled = True
            self.query_one("#next", Button).display = False
            self.sequence = False
        self.screen_stack[0].set_class(self.sequence, "session-active")
        self._render_wizard()
        self._refresh_update_controls()
        if not self._exit_after_step and self.screen is self.screen_stack[0]:
            target = "#finish" if self.sequence else ("#continue_initial" if self._initial_ready else "#quickstart")
            self.query_one(target, Button).focus()
        if self._exit_after_step:
            self.exit()
            return
        if outcome.code == "checkout_requested":
            self.notify("Review the actual subscription in Google Play.", severity="warning")
        elif outcome.code not in ("listed", "environment_ok", "cancelled"):
            self.notify("Step stopped; check the result before another attempt.", severity="warning")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ePlus AI Toolkit Textual frontend")
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument("--sequence", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(argv)
    try:
        selected = validate_step(args.step)
    except ValueError as exc:
        parser.error(str(exc))
    repo = Path(__file__).resolve().parent
    app = GoogleAITUI(repo=repo, selected_step=selected,
                      start_sequence=args.sequence, initial_debug=args.debug)
    app.run()
    if app.restart_requested:
        try:
            return subprocess.call(restart_command(repo), cwd=repo)
        except (OSError, UpdateError):
            print("Update installed. Could not reopen the dashboard; run the native launcher manually.", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
