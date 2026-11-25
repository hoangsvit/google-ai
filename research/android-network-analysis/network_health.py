"""Offline network-health research; accepts synthetic, sanitized observations only."""
import argparse
import json
from pathlib import Path
from collections import Counter
import unittest

OUTCOMES = {"ok", "timeout", "dns_error", "tls_error", "http_error"}
MAX_RECORDS = 10000

def summarize(records):
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError("Expected a list of at most 10000 observations")
    counts = Counter()
    durations = []
    for record in records:
        if not isinstance(record, dict) or set(record) != {"outcome", "duration_ms"}:
            raise ValueError("Only outcome and duration_ms are accepted")
        outcome = record["outcome"]
        duration = record["duration_ms"]
        if not isinstance(outcome, str) or outcome not in OUTCOMES:
            raise ValueError("Unknown outcome")
        if type(duration) is not int or not 0 <= duration <= 3600000:
            raise ValueError("Invalid duration_ms")
        counts[outcome] += 1
        durations.append(duration)
    return {"observations": len(records), "outcomes": dict(sorted(counts.items())),
            "mean_duration_ms": round(sum(durations) / len(durations), 2) if durations else None}

DEMO = [{"outcome": "ok", "duration_ms": 100},
        {"outcome": "tls_error", "duration_ms": 250},
        {"outcome": "timeout", "duration_ms": 1000}]

class Tests(unittest.TestCase):
    def test_demo(self):
        report = summarize(DEMO)
        self.assertEqual(report["observations"], 3)
        self.assertEqual(report["outcomes"]["tls_error"], 1)
        self.assertEqual(report["mean_duration_ms"], 450)
    def test_empty(self):
        self.assertIsNone(summarize([])["mean_duration_ms"])
    def test_reject_extra_fields(self):
        with self.assertRaises(ValueError):
            summarize([{"outcome": "ok", "duration_ms": 5, "headers": {}}])
    def test_reject_invalid_duration(self):
        for invalid in (-1, True, "5"):
            with self.assertRaises(ValueError):
                summarize([{"outcome": "ok", "duration_ms": invalid}])
    def test_invalid_outcome(self):
        with self.assertRaises(ValueError):
            summarize([{"outcome": "unknown", "duration_ms": 5}])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--demo", action="store_true")
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--input", type=Path, help="Sanitized synthetic JSON only")
    args = parser.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        return 0 if result.wasSuccessful() else 1
    try:
        if args.input and args.input.stat().st_size > 2_000_000:
            raise ValueError("Input exceeds size limit")
        records = DEMO if args.demo else json.loads(args.input.read_text(encoding="utf-8"))
        print(json.dumps(summarize(records), indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(2, "Invalid or unreadable sanitized input.\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
