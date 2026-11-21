"""Offline tests for non-purchasing connection diagnostics."""
import subprocess
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import device_diagnostics as diag


def result(stdout="", returncode=0):
    return subprocess.CompletedProcess([], returncode, stdout, "")


class ConnectionGuideTests(unittest.TestCase):
    def test_adb_path_configuration_is_used(self):
        with tempfile.TemporaryDirectory() as folder:
            adb = Path(folder) / "adb.exe"
            adb.touch()
            with patch.dict(diag.os.environ, {"ADB_PATH": str(adb)}), \
                 patch.object(diag.shutil, "which", return_value=None):
                self.assertEqual(diag.locate_adb("win32"), str(adb))

    def test_missing_adb_gives_native_macos_guidance(self):
        with patch.object(diag, "locate_adb", return_value=None), \
             patch.object(diag.metadata, "version", side_effect=diag.metadata.PackageNotFoundError):
            found = diag.inspect_connection("darwin")
        self.assertEqual(found.status, "missing_adb")
        self.assertIn("brew install android-platform-tools", found.guidance)
        self.assertNotIn("PowerShell", " ".join(found.details + (found.guidance,)))

    def test_missing_adb_gives_windows_guidance(self):
        with patch.object(diag, "locate_adb", return_value=None), \
             patch.object(diag.metadata, "version", return_value="16.5.9"):
            found = diag.inspect_connection("win32")
        self.assertIn("MuMu", found.guidance)
        self.assertNotIn("brew", found.guidance)

    def test_unauthorized_device_has_actionable_message(self):
        with patch.object(diag, "locate_adb", return_value="adb"), \
             patch.object(diag.metadata, "version", return_value="16.5.9"), \
             patch.object(diag, "_run", return_value=result("List of devices attached\nemulator-5554 unauthorized\n")):
            found = diag.inspect_connection("win32")
        self.assertEqual(found.status, "no_online_device")
        self.assertIn("approve", found.guidance)

    def test_multiple_devices_fail_closed(self):
        with patch.object(diag, "locate_adb", return_value="adb"), \
             patch.object(diag.metadata, "version", return_value="16.5.9"), \
             patch.object(diag, "_run", return_value=result("List of devices attached\nemulator-5554 device\n127.0.0.1:16384 device\n")) as run:
            found = diag.inspect_connection("win32")
        self.assertEqual(found.status, "ambiguous")
        self.assertEqual(run.call_count, 1)

    def test_connected_device_uses_only_inspection_commands(self):
        calls = []
        def fake_run(adb, args):
            calls.append(args)
            if args == ["devices"]:
                return result("List of devices attached\nemulator-5554 device\n")
            if args[-2:] == ["getprop", "ro.product.cpu.abi"]:
                return result("arm64-v8a\n")
            if args[-3:] == ["pm", "path", diag.GOOGLE_ONE]:
                return result("package:/data/app/google-one/base.apk\n")
            if args[-3:] == ["pm", "path", diag.GOOGLE_PLAY]:
                return result("package:/data/app/play/base.apk\n")
            if args[-1:] == ["id"]:
                return result("uid=2000(shell) gid=2000(shell)\n")
            raise AssertionError(args)
        with patch.object(diag, "locate_adb", return_value="adb"), \
             patch.object(diag.metadata, "version", return_value="16.5.9"), \
             patch.object(diag, "_run", side_effect=fake_run):
            found = diag.inspect_connection("darwin")
        self.assertEqual(found.status, "connected")
        self.assertIn("Basic Android", found.headline)
        self.assertIn("unverified", found.guidance)
        self.assertEqual(len(calls), 5)
        flattened = str(calls).lower()
        for unsafe in ("connect", "install", "push", "root", "force-stop", "billing", "frida-server", "tap"):
            self.assertNotIn(unsafe, flattened)

    def test_missing_google_one_does_not_claim_billing_ready(self):
        def fake_run(adb, args):
            if args == ["devices"]:
                return result("List of devices attached\nemulator-5554 device\n")
            if args[-3:] == ["pm", "path", diag.GOOGLE_PLAY]:
                return result("package:/data/app/play/base.apk\n")
            return result("", 1)
        with patch.object(diag, "locate_adb", return_value="adb"), \
             patch.object(diag.metadata, "version", return_value="16.5.9"), \
             patch.object(diag, "_run", side_effect=fake_run):
            found = diag.inspect_connection("win32")
        self.assertEqual(found.status, "missing_google_one")
        self.assertIn("not detected", " ".join(found.details))

    def test_missing_play_store_is_reported(self):
        def fake_run(adb, args):
            if args == ["devices"]:
                return result("List of devices attached\nemulator-5554 device\n")
            if args[-3:] == ["pm", "path", diag.GOOGLE_ONE]:
                return result("package:/data/app/one/base.apk\n")
            return result("", 1)
        with patch.object(diag, "locate_adb", return_value="adb"), \
             patch.object(diag.metadata, "version", return_value="16.5.9"), \
             patch.object(diag, "_run", side_effect=fake_run):
            found = diag.inspect_connection("win32")
        self.assertEqual(found.status, "missing_google_play")

    def test_safe_text_does_not_echo_unsupported_data(self):
        self.assertEqual(diag._clean("secret\nanother"), "unknown")


if __name__ == "__main__":
    unittest.main()
