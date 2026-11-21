"""Capture REAL Textual screen renders (not hand-drawn mockups).

Runs the project's GoogleAITUI with Textual's headless terminal renderer.
No ADB, Frida, Google account, external app or checkout is launched.
SVG is the native export; PNG is a direct rasterization of that SVG.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
import sys
from xml.etree import ElementTree as ET

import cairosvg
from PIL import Image
from textual.widgets import Button, Checkbox, Select, Static

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tui import Approval, GoogleAITUI  # noqa: E402


def save_real_render(app: GoogleAITUI, directory: Path, name: str) -> None:
    svg = app.export_screenshot(title=f"ePlus AI Toolkit - {name}")
    if "<svg" not in svg or "</svg>" not in svg:
        raise RuntimeError(f"{name}: Textual did not produce a complete SVG")
    svg_path = directory / f"{name}.svg"
    png_path = directory / f"{name}.png"
    svg_path.write_text(svg, encoding="utf-8")
    ET.fromstring(svg)
    # Real terminal SVG, directly converted into PNG; no repainting or layout edits.
    cairosvg.svg2png(bytestring=svg.encode("utf-8"),
                     write_to=str(png_path), scale=1.5)
    with Image.open(png_path) as picture:
        picture.verify()
    with Image.open(png_path) as picture:
        if picture.width < 750 or picture.height < 400:
            raise RuntimeError(f"{name}: unexpected small image {picture.size}")
        print(f"Captured {png_path} ({picture.width}x{picture.height})", flush=True)


async def capture(directory: Path) -> None:
    app = GoogleAITUI(repo=ROOT)
    async with app.run_test(size=(132, 43)) as pilot:
        await pilot.pause()
        assert not app.busy, "Screenshot runner must never initiate checkout"
        assert "FREE TRIAL" in str(app.query_one("#pro_group", Static).render())
        assert "PAID" in str(app.query_one("#ultra_group", Static).render())
        assert "CLEAN ACCOUNT" in str(app.query_one("#ultra_group", Static).render())
        # New wizard from PR #58, with explicit Pro FREE vs Ultra PAID plan cards.
        assert app.query_one("#start_ultra", Button).display
        save_real_render(app, directory, "01-pro-free-vs-ultra-paid")

        # Capture the new wizard's Advanced view, which also includes Ultra Step 6.
        app.advanced_pressed()
        await pilot.pause()
        assert app.query_one("#workflow_actions").display
        app.query_one("#mode", Select).value = "single"
        app.query_one("#step", Select).value = 6
        await pilot.pause()
        save_real_render(app, directory, "04-new-wizard-advanced-ultra")
        app.advanced_pressed()
        await pilot.pause()
        assert not app.query_one("#workflow_actions").display

        # The same handler is called by the real Ultra button.

        # It only opens the pre-checkout approval modal; NO CLI is run.
        app._confirm_stage(6, False)
        await pilot.pause()
        assert isinstance(app.screen, Approval)
        assert app.screen.query_one("#approve", Button).disabled
        assert not app.screen.query_one("#clean_account_ack", Checkbox).value
        save_real_render(app, directory, "02-ultra-clean-account-confirmation")

        # Verify acknowledgement *only toggles the modal*, without pressing it.
        app.screen.query_one("#clean_account_ack", Checkbox).value = True
        await pilot.pause()
        assert not app.screen.query_one("#approve", Button).disabled
        assert not app.busy
        save_real_render(app, directory, "03-ultra-checkbox-checked")
        await pilot.click("#cancel")
        await pilot.pause()
        assert not app.busy


def main() -> int:
    directory = ROOT / "artifacts" / "tui-screenshots"
    directory.mkdir(parents=True, exist_ok=True)
    asyncio.run(capture(directory))
    (directory / "README.txt").write_text(
        "Actual Textual 8.2.8 headless terminal renders of the app from this commit.\n"
        "01: NEW wizard home shows Pro FREE and Ultra PAID as separate groups.\n"
        "02: Ultra approval modal, clean-account checkbox unchecked.\n"
        "03: same modal, checkbox checked but NO checkout started.\n"
        "04: NEW wizard Advanced view, Ultra paid Step 6 selected.\n"
        "These screenshots do not depict Android / Google Play, eligibility, or billing.\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
