"""Verify translated README files track the canonical English README."""
import hashlib
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("vi", "zh-CN", "ja", "ko", "es", "fr")
MARKER = re.compile(r"<!-- Source README\.md git-blob: ([0-9a-f]{40}) -->")
TECHNICAL = (
    "Diagnose Android connection", "Offer Explorer", "Check Device & Offers",
    "Google Play", "MuMuPlayer", "Windows", "macOS", "ADB", "Frida",
    "g1.2tb.ai.subs_variant", "g1.play.2tb.ai", "g1.2tb.ai",
    "tui_core.py", "macos_runner.py", "ultra0.py",
    "docs/README.md", "docs/MACOS-PREVIEW.md", "docs/INSTALLATION.md",
    "docs/SAFETY.md", "docs/PROJECT.md", "THIRD_PARTY_NOTICES.md",
    "legacy/windows/", "brew install android-platform-tools",
    "adb devices", "sh run-macos.sh", ".\\run-all.ps1",
    "[!CAUTION]", "[!NOTE]", "2–5", "16.5.9",
)

class ReadmeSourceParityTests(unittest.TestCase):
    def test_all_locales_track_exact_source_blob(self):
        source = (ROOT / "README.md").read_bytes()
        # Windows checkouts with core.autocrlf=true convert LF to CRLF, which
        # changes the byte length and hash. Git stores blobs with LF, so
        # normalize before hashing or this gate fails only on Windows.
        source = source.replace(b"\r\n", b"\n")
        payload = ("blob " + str(len(source)) + "\0").encode("ascii") + source
        sha = hashlib.sha1(payload).hexdigest()
        for locale in LOCALES:
            with self.subTest(locale=locale):
                translated = (ROOT / ("README." + locale + ".md")).read_text(encoding="utf-8")
                self.assertEqual(
                    MARKER.findall(translated), [sha],
                    "Translation has not been synchronized with canonical README.md",
                )

    def test_full_major_section_and_technical_coverage(self):
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        expected_count = len(re.findall(r"^## ", english, re.MULTILINE))
        self.assertGreaterEqual(expected_count, 11)
        for locale in LOCALES:
            with self.subTest(locale=locale):
                localized = (ROOT / ("README." + locale + ".md")).read_text(encoding="utf-8")
                self.assertGreaterEqual(len(re.findall(r"^## ", localized, re.MULTILINE)), expected_count)
                self.assertLess(localized.index("Diagnose Android connection"), localized.index("## 3."))
                for detail in TECHNICAL:
                    self.assertIn(detail, localized, "Missing translation detail: " + detail)
                self.assertEqual(localized.count(chr(96) * 3) % 2, 0)

    def test_translation_markdown_is_clean(self):
        """Guard against artifacts from hand-edited translations.

        This is a structural check, not a substitute for review by a
        fluent speaker or an assurance of semantic translation quality.
        """
        for locale in LOCALES:
            with self.subTest(locale=locale):
                localized = (ROOT / ("README." + locale + ".md")).read_text(encoding="utf-8")
                self.assertNotIn("§", localized, "Unconverted Markdown delimiter placeholder")
                self.assertIsNone(
                    re.search(r"^## [^\n]+\*\*[^\n]+$", localized, re.MULTILINE),
                    "Heading is joined to bold body text, likely missing a newline",
                )
                self.assertIn("## 3.", localized)
                self.assertIn("## 4.", localized)
                self.assertIn("## 5.", localized)

    def test_three_separate_one_dollar_transactions_documented(self):
        """Do not regress to calling three $1 events a single $3 charge."""
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("three separate US$1 transactions", english)
        self.assertNotIn("hold of around US$3", english)
        for locale in LOCALES:
            with self.subTest(locale=locale):
                localized = (ROOT / ("README." + locale + ".md")).read_text(encoding="utf-8")
                self.assertIn("3 × US$1 = US$3", localized)
                self.assertIn("24", localized)
                self.assertIn("Step 5", localized)

    def test_english_alias_links_to_root_source(self):
        self.assertIn("(README.md)", (ROOT / "README.en.md").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
