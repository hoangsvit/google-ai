import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research.ios_automation import MAX_BYTES, load_report, normalize_report, readiness


def sample(rows):
    return {"schemaVersion": 1, "scan": {"skus": rows}}


class IOSResearchTests(unittest.TestCase):
    def test_only_observed_identifiers_are_exported(self):
        report = sample([
            {"id": "g1.example.product", "token": "secret"},
            {"id": "g1.example.product"},
            {"id": "com.google.one.example"},
            {"id": "com.google.gemini.example"},
            {"id": "name@example.com"},
            {"id": "g1.invalid."},
        ])
        report["mappingConfig"] = {"rules": [{"to": "g1.unobserved.product"}]}
        report["test"] = {"status": "rewritten"}
        result = normalize_report(report)
        self.assertEqual([row["sku"] for row in result["items"]],
                         ["g1.example.product", "com.google.one.example", "com.google.gemini.example"])
        self.assertNotIn("secret", json.dumps(result))
        self.assertNotIn("unobserved", json.dumps(result))
        self.assertFalse(result["eligibility_verified"])
        self.assertFalse(result["checkout_supported"])

    def test_invalid_schema(self):
        for value in ([], {}, {"schemaVersion": 2}, {"schemaVersion": 1, "scan": {}}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_report(value)

    def test_bounded_rows(self):
        result = normalize_report(sample([{"id": f"g1.example.{i}"} for i in range(301)]))
        self.assertEqual(len(result["items"]), 300)
        self.assertTrue(result["truncated"])

    def test_size_limit_and_local_import(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "report.json"
            path.write_text(json.dumps(sample([])), encoding="utf-8")
            self.assertEqual(load_report(path)["status"], "no_identifiers")
            path.write_bytes(b"x" * (MAX_BYTES + 1))
            with self.assertRaises(ValueError):
                load_report(path)

    def test_readiness_never_claims_device_verified(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "setup").mkdir()
            for name in ("setup.sh", "create-vm.sh", "start-vm.sh"):
                (root / "setup" / name).touch()
            with patch("research.ios_automation.shutil.which", return_value=None):
                result = readiness(root)
            self.assertTrue(result["vphone_scripts_present"])
            self.assertFalse(result["git_available"])
            self.assertEqual(result["storekit"], "unverified")
            self.assertFalse(result["checkout_supported"])


if __name__ == "__main__":
    unittest.main()
