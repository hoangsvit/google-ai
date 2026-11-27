import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "legacy/windows"
NEW = (
    "00_Environment_Self_Check.bat",
    "One_Click_Environment_Setup.bat",
    "03_List_Available_Free_And_Discounted_Offers.bat",
    "01_Pro5TB_Free_12_Months.bat",
    "02_Pro5TB_Free_6_Month_Extension.bat",
    "Pro5TB_1.99_Per_Month_12_Months.bat",
    "Pro5TB_1.99_Per_Month_3_Months.bat",
    "Pro5TB_0.99_For_1_Month.bat",
)

class ResearchBatchTests(unittest.TestCase):
    def test_launchers_exist_and_do_not_invoke_billing_engine(self):
        for path in [ROOT / name for name in NEW] + list(ROOT.glob("*.bat")):
            with self.subTest(path=path.name):
                content = path.read_text(encoding="utf-8").lower()
                for forbidden in ("--force", "--stack", "ultra0.py", "frida", "purchase_token"):
                    self.assertNotIn(forbidden, content)

    def test_offer_review_launches_google_one(self):
        content = (ROOT / NEW[2]).read_text(encoding="utf-8")
        self.assertIn("from device_diagnostics import open_google_one_app", content)
        self.assertIn("s == 'opened' else 3", content)

    def test_environment_check_requires_python_and_shared_diagnostics(self):
        content = (ROOT.parents[1] / "research/g1-acq-plus-android-batch/check-device.bat").read_text(encoding="utf-8")
        self.assertIn("where python", content)
        self.assertIn("exit /b 1", content)
        self.assertIn("from device_diagnostics import inspect_connection", content)
        self.assertIn("exit /b %errorlevel%", content)

if __name__ == "__main__":
    unittest.main()
