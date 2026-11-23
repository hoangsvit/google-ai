"""ADB installer checks: no network access, Android device, or real ADB."""
import importlib.util
import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("setup_env", ROOT / "setup_env.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def fake_official_zip():
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as archive:
        archive.writestr("platform-tools/adb.exe", b"test not a real executable")
        archive.writestr("platform-tools/AdbWinApi.dll", b"test")
    return io.BytesIO(data.getvalue())


class AdbSetupTests(unittest.TestCase):
    def test_existing_local_adb_is_reused_without_download(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            adb = root / "platform-tools" / "adb.exe"
            adb.parent.mkdir()
            adb.write_bytes(b"existing in-use adb")
            with patch.object(installer, "BASE", root), \
                 patch.object(installer, "user_platform_tools", return_value=root / "cache"), \
                 patch.object(installer, "adb_is_working", side_effect=lambda p: Path(p) == adb), \
                 patch.object(installer.urllib.request, "urlopen") as download:
                self.assertEqual(installer.find_adb(), str(adb))
                download.assert_not_called()

    def test_invalid_executable_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            adb = Path(temp) / "adb.exe"
            adb.write_bytes(b"not an executable")
            with patch.object(installer.subprocess, "run", side_effect=OSError("invalid")):
                self.assertFalse(installer.adb_is_working(adb))

    def test_locked_project_file_uses_per_user_fallback(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project_dir = root / "platform-tools"
            cache_dir = root / "user" / "platform-tools"
            real_copytree = installer.shutil.copytree
            def copytree(source, dest, **kwargs):
                if Path(dest) == project_dir:
                    raise PermissionError(13, "Permission denied", str(project_dir / "adb.exe"))
                return real_copytree(source, dest, **kwargs)
            def working(adb):
                return Path(adb) == cache_dir / "adb.exe" and Path(adb).exists()
            with patch.object(installer, "BASE", root), \
                 patch.object(installer, "user_platform_tools", return_value=cache_dir), \
                 patch.object(installer, "adb_is_working", side_effect=working), \
                 patch.object(installer.urllib.request, "urlopen", return_value=fake_official_zip()), \
                 patch.object(installer.shutil, "copytree", side_effect=copytree):
                result = installer.download_platform_tools()
                self.assertEqual(result, str(cache_dir / "adb.exe"))
            self.assertTrue((cache_dir / "AdbWinApi.dll").exists())

    def test_preflight_uses_explicit_serial(self):
        class MockResult:
            returncode = 0
            stdout = "Success"
            stderr = ""
        with patch.object(installer.subprocess, "run", return_value=MockResult()) as called:
            self.assertTrue(installer.run_check("C:/adb.exe", "emulator-5554"))
        self.assertIn("--serial", called.call_args.args[0])
        self.assertIn("emulator-5554", called.call_args.args[0])


    def test_preflight_failure_displays_stderr_even_with_stdout(self):
        class MockResult:
            returncode = 1
            stdout = "Starting Android preflight\n"
            stderr = "RuntimeError: Could not make the billing module read-only\n"

        output = io.StringIO()
        errors = io.StringIO()
        with patch.object(installer.subprocess, "run", return_value=MockResult()), \
             redirect_stdout(output), redirect_stderr(errors):
            self.assertFalse(installer.run_check("adb", "emulator-5554"))
        self.assertIn("Starting Android preflight", output.getvalue())
        self.assertIn("billing module read-only", errors.getvalue())

    def test_failed_preflight_returns_nonzero_exit_code(self):
        output = io.StringIO()
        with patch.object(installer, "check_python"), \
             patch.object(installer, "install_frida"), \
             patch.object(installer, "find_adb", return_value="adb"), \
             patch.object(installer, "connect_emulator", return_value="emulator-5554"), \
             patch.object(installer, "run_check", return_value=False), \
             redirect_stdout(output):
            self.assertEqual(installer.main(), 1)
        self.assertIn("Environment check failed", output.getvalue())

    def test_missing_emulator_returns_nonzero_exit_code(self):
        with patch.object(installer, "check_python"), \
             patch.object(installer, "install_frida"), \
             patch.object(installer, "find_adb", return_value="adb"), \
             patch.object(installer, "connect_emulator", return_value=None), \
             patch.object(installer, "run_check") as check, \
             redirect_stdout(io.StringIO()):
            self.assertEqual(installer.main(), 1)
        check.assert_not_called()

    def test_successful_preflight_returns_zero_exit_code(self):
        with patch.object(installer, "check_python"), \
             patch.object(installer, "install_frida"), \
             patch.object(installer, "find_adb", return_value="adb"), \
             patch.object(installer, "connect_emulator", return_value="emulator-5554"), \
             patch.object(installer, "run_check", return_value=True), \
             redirect_stdout(io.StringIO()):
            self.assertEqual(installer.main(), 0)

if __name__ == "__main__":
    unittest.main()
