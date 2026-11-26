import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research.ios_status import health_command, status
from research.ios_menu import choose


class StatusTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "tools").mkdir()
        (self.root / "tools" / "vphoned.sh").touch()
        for name, value in (("platform.system", "Linux"), ("shutil.which", "/bin/tool")):
            p = patch("research.ios_status." + name, return_value=value)
            p.start()
            self.addCleanup(p.stop)

    def test_only_health_endpoint(self):
        self.assertEqual(health_command(self.root, 3)[-4:],
                         ["-c", "3", "GET", "/v1/health"])
        for cid in (0, -1, True, "3"):
            with self.subTest(cid=cid), self.assertRaises(ValueError):
                health_command(self.root, cid)

    def test_response_does_not_verify_other_gates(self):
        with patch("research.ios_status.subprocess.run", return_value=
                   subprocess.CompletedProcess([], 0, b'{"status":"ok","secret":"x"}')):
            result = status(self.root, 3)
        self.assertEqual(result["daemon"], "daemon_responding")
        self.assertEqual(result["storekit"], "unverified")
        self.assertEqual(result["vm_boot"], "unverified")
        self.assertNotIn("secret", result)
        self.assertFalse(result["checkout_supported"])

    def test_invalid_and_unreachable(self):
        for rc, raw, expected in ((0, b'{}', "invalid_response"),
                                  (0, b'not-json', "invalid_response"),
                                  (0, b'x' * 65537, "invalid_response"),
                                  (1, b'', "unreachable")):
            with self.subTest(expected=expected), patch(
                "research.ios_status.subprocess.run", return_value=
                subprocess.CompletedProcess([], rc, raw)
            ):
                self.assertEqual(status(self.root, 3)["daemon"], expected)

    def test_timeout(self):
        with patch("research.ios_status.subprocess.run",
                   side_effect=subprocess.TimeoutExpired("health", 20)):
            self.assertEqual(status(self.root, 3)["daemon"], "timeout")


class MenuTests(unittest.TestCase):
    def test_cancel_does_not_execute(self):
        root = Path("mock-root")
        with patch("research.ios_menu.run") as run, patch("builtins.input", return_value="n"), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(choose(root, "2"))
            run.assert_called_once_with(root, "setup", vm=None)

    def test_explicit_confirmation(self):
        root = Path("mock-root")
        with patch("research.ios_menu.run", return_value=0) as run, \
             patch("builtins.input", side_effect=["test-vm", "y"]), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(choose(root, "5"))
            self.assertEqual(run.call_count, 2)
            run.assert_called_with(root, "start", vm="test-vm", execute=True)

    def test_exit(self):
        self.assertFalse(choose(Path("mock-root"), "0"))


if __name__ == "__main__":
    unittest.main()
