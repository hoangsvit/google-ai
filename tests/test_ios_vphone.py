import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research.ios_vphone import command, run


class VPhoneTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "setup").mkdir()
        for name in ("setup.sh", "create-vm.sh", "start-vm.sh"):
            (self.root / "setup" / name).touch()

    def test_start_requires_named_vm_and_does_not_unlock(self):
        for name in (None, "", "../vm", "-x", "vm;echo"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                command(self.root, "start", vm=name)
        self.assertEqual(command(self.root, "start", vm="test-vm")[-2:],
                         ["--no-unlock", "test-vm"])

    def test_plan_does_not_execute(self):
        with patch("research.ios_vphone.subprocess.run") as child:
            with contextlib.redirect_stdout(io.StringIO()):
                for action in ("setup", "create", "start", "stop"):
                    vm = "test-vm" if action in ("start", "stop") else None
                    self.assertEqual(run(self.root, action, vm=vm), 0)
            child.assert_not_called()

    def test_linux_explicit_start(self):
        with patch("research.ios_vphone.platform.system", return_value="Linux"), \
             patch("research.ios_vphone.shutil.which", return_value="/bin/bash"), \
             patch("research.ios_vphone.subprocess.run",
                   return_value=subprocess.CompletedProcess([], 0)) as child, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(run(self.root, "start", vm="test-vm", execute=True), 0)
            child.assert_called_once_with(command(self.root, "start", vm="test-vm"),
                                          cwd=self.root.resolve(), check=False)
            self.assertIn("still unverified", output.getvalue())

    def test_unsupported_host_and_noninteractive_setup(self):
        with patch("research.ios_vphone.platform.system", return_value="Windows"), \
             patch("research.ios_vphone.subprocess.run") as child:
            with self.assertRaises(ValueError):
                run(self.root, "list")
            child.assert_not_called()
        with patch("research.ios_vphone.platform.system", return_value="Linux"), \
             patch("research.ios_vphone.shutil.which", return_value="/bin/bash"), \
             patch("research.ios_vphone.sys.stdin.isatty", return_value=False), \
             patch("research.ios_vphone.subprocess.run") as child:
            with self.assertRaises(ValueError):
                run(self.root, "setup", execute=True)
            child.assert_not_called()

    def test_list_failure_propagates(self):
        with patch("research.ios_vphone.platform.system", return_value="Linux"), \
             patch("research.ios_vphone.shutil.which", return_value="/bin/bash"), \
             patch("research.ios_vphone.subprocess.run",
                   return_value=subprocess.CompletedProcess([], 7)) as child:
            self.assertEqual(run(self.root, "list"), 7)
            child.assert_called_once_with(command(self.root, "list"),
                                          cwd=self.root.resolve(), check=False)


if __name__ == "__main__":
    unittest.main()
