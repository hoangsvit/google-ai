"""Offline checks for cloud PoC deploy scripts; no GCP, Android or purchase calls."""
from pathlib import Path
import unittest
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1] / "cloud" / "gcp"


class CloudDeploymentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.deploy = (ROOT / "deploy.sh").read_text(encoding="utf-8")
        cls.startup = (ROOT / "startup.sh").read_text(encoding="utf-8")
        cls.check = (ROOT / "check.sh").read_text(encoding="utf-8")
        cls.destroy = (ROOT / "destroy.sh").read_text(encoding="utf-8")

    @unittest.skipUnless(shutil.which('bash'), 'bash not available on this CI host')
    def test_shell_syntax(self):
        for name in ('deploy.sh', 'startup.sh', 'check.sh', 'destroy.sh'):
            subprocess.run(['bash', '-n', str(ROOT / name)], check=True)

    def test_nested_virtualization_and_cost_consent(self):
        self.assertIn("--enable-nested-virtualization", self.deploy)
        self.assertIn("CONFIRM_COST", self.deploy)
        self.assertIn("n2-standard-4", self.deploy)

    def test_only_iap_ssh_rule(self):
        self.assertIn("--source-ranges=35.235.240.0/20", self.deploy)
        self.assertIn("--rules=tcp:22", self.deploy)
        self.assertNotIn("--rules=tcp:5555", self.deploy)
        self.assertNotIn("--rules=tcp:8554", self.deploy)

    def test_emulator_ports_are_loopback_only(self):
        self.assertIn("127.0.0.1:5555:5555", self.startup)
        self.assertIn("127.0.0.1:8554:8554", self.startup)
        self.assertNotIn("--publish 0.0.0.0:", self.startup)

    def test_no_checkout_automation(self):
        for content in (self.deploy, self.startup, self.check):
            self.assertNotIn(" -Step 2", content)
            self.assertNotIn(" -Step 3", content)
            self.assertNotIn(" -Step 4", content)
            self.assertNotIn(" -Step 5", content)
            self.assertNotIn(" --force", content.lower())
            self.assertNotIn(" --all-stages", content.lower())

    def test_deletion_needs_explicit_opt_in(self):
        self.assertIn("CONFIRM_DESTROY", self.destroy)


if __name__ == "__main__":
    unittest.main()
