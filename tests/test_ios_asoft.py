import contextlib
import hashlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research.ios_asoft import (
    GIB, execute_command, installer_command, launch_command, prerequisites, verify_archive,
)


class ASoftwareTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "installer").mkdir()
        (self.root / "installer" / "Setup-ASoftware.ps1").touch()
        (self.root / "ASoftware.exe").touch()

    def test_no_wsl_no_auto_approval(self):
        args = installer_command(self.root, self.root / "target", check=True)
        self.assertEqual(args[args.index("-Version") + 1], "ios26")
        self.assertEqual(args[args.index("-Linux") + 1], "helper")
        self.assertEqual(args[args.index("-IfNoWsl") + 1], "nowsl")
        self.assertIn("-Check", args)
        self.assertNotIn("-Yes", args)
        self.assertNotIn("-ExecutionPolicy", args)

    def test_reject_space_in_destination(self):
        with self.assertRaises(ValueError):
            installer_command(self.root, self.root / "with space")

    def test_hash(self):
        archive = self.root / "archive.zip"
        archive.write_bytes(b"mock archive")
        expected = hashlib.sha256(b"mock archive").hexdigest()
        self.assertTrue(verify_archive(archive, expected.upper()))
        self.assertFalse(verify_archive(archive, "0" * 64))
        with self.assertRaises(ValueError):
            verify_archive(archive, "bad")

    def test_diagnostics_do_not_claim_guest_ready(self):
        with patch("research.ios_asoft.platform.system", return_value="Windows"), \
             patch("research.ios_asoft.memory_bytes", return_value=16 * GIB), \
             patch("research.ios_asoft.os.cpu_count", return_value=8):
            result = prerequisites(self.root)
        self.assertTrue(result["launcher_present"])
        self.assertTrue(result["ram_recommended_met"])
        self.assertEqual(result["google_app"], "unverified")
        self.assertFalse(result["checkout_supported"])

    def test_explicit_execution(self):
        args = launch_command(self.root)
        with patch("research.ios_asoft.subprocess.run") as child, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(execute_command(args, self.root, execute=False), 0)
            child.assert_not_called()
        with patch("research.ios_asoft.platform.system", return_value="Windows"), \
             patch("research.ios_asoft.sys.stdin.isatty", return_value=True), \
             patch("research.ios_asoft.subprocess.run", return_value=
                   subprocess.CompletedProcess(args, 7)) as child:
            self.assertEqual(execute_command(args, self.root, execute=True), 7)
            child.assert_called_once_with(args, cwd=self.root.resolve(), check=False)

    def test_non_windows_never_executes(self):
        with patch("research.ios_asoft.platform.system", return_value="Linux"), \
             patch("research.ios_asoft.subprocess.run") as child:
            with self.assertRaises(ValueError):
                execute_command(launch_command(self.root), self.root, execute=True)
            child.assert_not_called()


if __name__ == "__main__":
    unittest.main()
