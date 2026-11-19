"""Validate the Markdown documentation hub and repository overview layout."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LOCALIZED = ("vi", "zh-CN", "ja", "ko", "es", "fr")
TOPIC_PAGES = (
    "docs/README.md", "docs/SAFETY.md", "docs/INSTALLATION.md",
    "docs/USAGE.md", "docs/TROUBLESHOOTING.md", "docs/PROJECT.md",
    "docs/MACOS-PREVIEW.md", "docs/DETAILED-GUIDE.md",
    "docs/ORIGINAL-STEPS.md", "docs/AUTHOR-NOTES.md",
    "docs/WINDOWS-SMOKE-TEST.md",
)
MD_LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")


class DocumentationNavigationTests(unittest.TestCase):
    def test_readme_is_short_and_docs_have_detail(self):
        english = ROOT / "README.md"
        self.assertLess(english.stat().st_size, 4500)
        for lang in LOCALIZED:
            with self.subTest(locale=lang):
                short = ROOT / f"README.{lang}.md"
                detailed = DOCS / "i18n" / f"README.{lang}.md"
                # UTF-8 translated text uses more bytes than English for the same length.
                # Keep practical installation steps visible while preventing README bloat.
                self.assertLess(short.stat().st_size, 4000)
                self.assertGreater(detailed.stat().st_size, short.stat().st_size)
                self.assertIn(
                    f"(docs/i18n/README.{lang}.md)",
                    short.read_text(encoding="utf-8"),
                )
        self.assertGreater((DOCS / "USAGE.md").stat().st_size, english.stat().st_size)

    def test_documentation_hub_references_every_topic(self):
        hub = (DOCS / "README.md").read_text(encoding="utf-8")
        self.assertIn("[!CAUTION]", hub)
        self.assertIn("2–5", hub)
        self.assertIn("macOS", hub)
        for target in TOPIC_PAGES:
            with self.subTest(page=target):
                self.assertTrue((ROOT / target).is_file())
                if target != "docs/README.md":
                    self.assertIn(f"({Path(target).name})", hub)
        for lang in LOCALIZED:
            self.assertIn(f"(i18n/README.{lang}.md)", hub)

    def test_all_local_markdown_links_point_to_existing_files(self):
        locations = [ROOT / "README.md", ROOT / "README.en.md"]
        locations.extend(ROOT / f"README.{lang}.md" for lang in LOCALIZED)
        locations.extend(sorted(DOCS.rglob("*.md")))
        locations.extend((ROOT / "CONTRIBUTING.md", ROOT / "AGENTS.md"))
        for source in locations:
            text = source.read_text(encoding="utf-8")
            for target in MD_LINK.findall(text):
                if target.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                relative = target.partition("#")[0]
                if not relative:
                    continue
                with self.subTest(source=str(source.relative_to(ROOT)), link=relative):
                    self.assertTrue((source.parent / relative).is_file())

    def test_windows_and_mac_installation_both_work_from_project_root(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("### Windows", readme)
        self.assertIn("### macOS", readme)
        self.assertEqual(readme.count("git clone https://github.com/hoangsvit/google-ai.git"), 2)
        self.assertIn(".\\run-all.ps1", readme)
        self.assertIn("sh run-macos.sh", readme)
        self.assertIn("brew install android-platform-tools", readme)
        self.assertIn("MuMuPlayer Pro", readme)
        self.assertNotIn("git switch dev", readme)
        mac = (DOCS / "MACOS-PREVIEW.md").read_text(encoding="utf-8")
        self.assertNotIn("git switch dev", mac)
        self.assertIn("Version availability", mac)
        self.assertIn("run-macos.sh", mac)
        for lang in LOCALIZED:
            with self.subTest(locale=lang):
                text = (ROOT / f"README.{lang}.md").read_text(encoding="utf-8")
                self.assertIn("Windows", text)
                self.assertIn("macOS", text)
                self.assertIn("sh run-macos.sh", text)
                self.assertIn(".\\run-all.ps1", text)
                self.assertEqual(text.count("git clone https://github.com/hoangsvit/google-ai.git"), 2)
                self.assertNotIn("git switch dev", text)

    def test_user_install_guides_never_require_switching_to_dev(self):
        pages = [
            ROOT / "README.md", ROOT / "README.en.md",
            DOCS / "README.md", DOCS / "INSTALLATION.md",
            DOCS / "MACOS-PREVIEW.md", DOCS / "TROUBLESHOOTING.md",
        ]
        pages.extend(ROOT / f"README.{lang}.md" for lang in LOCALIZED)
        pages.extend(DOCS / "i18n" / f"README.{lang}.md" for lang in LOCALIZED)
        for page in pages:
            with self.subTest(page=str(page.relative_to(ROOT))):
                text = page.read_text(encoding="utf-8")
                self.assertNotIn("git switch dev", text)
                self.assertNotIn("checkout dev", text)
                if page.name.startswith("README") and page.parent == ROOT:
                    self.assertNotIn("`dev`", text)
        project = (DOCS / "PROJECT.md").read_text(encoding="utf-8")
        self.assertIn("run-macos.sh", project)
        self.assertIn("run-all.ps1", project)

    def test_no_duplicate_full_guides_in_root(self):
        overview = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("(docs/README.md)", overview)
        self.assertIn("(docs/SAFETY.md)", overview)
        self.assertIn("(docs/USAGE.md)", overview)
        self.assertIn("sh run-macos.sh", overview)
        self.assertNotIn("## PowerShell CLI (advanced)", overview)
        self.assertNotIn("## Troubleshooting and results", overview)


if __name__ == "__main__":
    unittest.main()
