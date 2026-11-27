"""Offline regression: unverified research references never launch billing."""
import unittest
from unittest.mock import patch

import ultra0


class Ultra0ResearchStepTests(unittest.TestCase):
    def test_all_steps_6_to_19_are_defined(self):
        self.assertEqual(sorted(ultra0.RESEARCH_STEPS), list(range(6, 20)))

    def test_research_cannot_build_billing_script(self):
        for step in range(6, 20):
            with self.subTest(step=step), self.assertRaises(ValueError):
                ultra0.build_js(plan=f"research{step}")

    def test_research_process_stops_before_device_changes(self):
        with patch.object(ultra0, "add_account") as add, patch.object(ultra0, "run_trial") as trial:
            for step in range(6, 20):
                rec = ultra0.process("fixture@example.invalid", plan=f"research{step}")
                self.assertIn(rec["status"], ("research_review_only", "research_product_unverified"))
            add.assert_not_called()
            trial.assert_not_called()

    def test_cli_rejects_direct_research_before_adb(self):
        for args in (["--step", "9"], ["--plan", "research6"]):
            with patch("sys.argv", ["ultra0.py", *args]), patch.object(ultra0, "find_adb") as adb:
                with self.assertRaises(SystemExit) as exc:
                    ultra0.main()
                self.assertNotEqual(exc.exception.code, 0)
                adb.assert_not_called()


if __name__ == "__main__":
    unittest.main()
