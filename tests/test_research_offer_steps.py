import unittest
from pathlib import Path
from unittest.mock import patch

import research_offer_runner as runner
from research_offer_catalog import STEP_REFERENCES, research_step_options
from tui_core import command_for_step, parse_research_result, research_result_message


class ResearchStepTests(unittest.TestCase):
    def test_research_status_is_shared_and_platform_specific(self):
        # ultra0.py's per-account Result line is the primary protocol now.
        self.assertEqual(parse_research_result("   Result: manual_confirmation_required", 0),
                         "manual_confirmation_required")
        self.assertEqual(parse_research_result("   Result: offer_not_available", 0),
                         "offer_not_available")
        # The legacy runner protocol remains parseable for compatibility.
        self.assertEqual(parse_research_result("EPLUS_RESEARCH_RESULT:opened", 0), "opened")
        self.assertEqual(parse_research_result("EPLUS_RESEARCH_RESULT:opened", 1), "runner_failed")
        self.assertEqual(parse_research_result("", 0), "runner_failed")
        self.assertIn("ultra0.py", research_result_message("runner_failed", 9, "darwin"))
        self.assertIn("run-all.ps1", research_result_message("runner_failed", 9, "win32"))

    def test_native_command_runs_ultra0_directly_not_review_runner(self):
        with patch("tui_core.sys.platform", "linux"):
            command = command_for_step(9, Path("repo"), device="test")
        self.assertTrue(command[1].endswith("ultra0.py"))
        self.assertEqual(command[2:], ["--step", "9", "--serial", "test"])
        self.assertNotIn("research_offer_runner.py", " ".join(command))

    def test_run_all_research_block_invokes_ultra0(self):
        script = (Path(__file__).resolve().parents[1] / "run-all.ps1").read_text(encoding="utf-8")
        block = script.split("if ($Step -ge 6)")[1][:1500]
        self.assertIn("ultra0.py", block)
        self.assertNotIn("research_offer_runner.py", script)

    def test_stable_step_numbers(self):
        self.assertEqual(list(STEP_REFERENCES), list(range(6, 20)))
        self.assertEqual([step for _, step in research_step_options()], list(range(6, 20)))

    def test_windows_command_uses_existing_entrypoint(self):
        command = command_for_step(8, Path("repo"), shell="powershell.exe", device="test")
        self.assertEqual(command[-4:], ["-Step", "8", "-Serial", "test"])
        self.assertTrue(command[command.index("-File") + 1].endswith("run-all.ps1"))

    def test_research_confirmation_is_required(self):
        with patch.object(runner, "open_google_one_app") as app:
            self.assertEqual(runner.run_step(9, "test"), "not_confirmed")
            app.assert_not_called()

    def test_tui_confirmation_is_forwarded(self):
        command = command_for_step(9, Path("repo"), shell="powershell.exe", device="test",
                                   review_confirmed=True)
        self.assertIn("-ConfirmOfferReview", command)

    def test_offer_step_launches_official_app_only(self):
        with patch.object(runner, "open_google_one_app", return_value="opened") as one, \
             patch.object(runner, "open_youtube_app", return_value="opened") as youtube:
            self.assertEqual(runner.run_step(6, "test", confirmed=True), "opened")
            one.assert_called_once_with("test")
            youtube.assert_not_called()
            self.assertEqual(runner.run_step(19, "test", confirmed=True), "opened")
            youtube.assert_called_once_with("test")
            self.assertEqual(runner.run_step(2), "invalid_step")


if __name__ == "__main__":
    unittest.main()
