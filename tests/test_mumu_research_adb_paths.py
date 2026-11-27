"""Offline regression checks for consistent MuMuPlayer ADB discovery."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = (
    "C:/Program Files/Netease/MuMuPlayer/nx_main/adb.exe",
    "C:/Program Files/Netease/MuMuPlayer/nx_device/12.0/shell/adb.exe",
    "D:/Program Files/Netease/MuMuPlayer/nx_main/adb.exe",
    "D:/Program Files/Netease/MuMuPlayer/nx_device/12.0/shell/adb.exe",
)

class MuMuResearchAdbPathsTests(unittest.TestCase):
    def test_all_three_runtime_locators_cover_mumu_player_layouts(self):
        for filename in ("setup_env.py", "device_diagnostics.py", "ultra0.py"):
            source = (ROOT / filename).read_text(encoding="utf-8").replace(chr(92), "/")
            for path in EXPECTED:
                with self.subTest(filename=filename, path=path):
                    self.assertIn(path, source)

if __name__ == "__main__":
    unittest.main()
