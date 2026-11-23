"""Offline regressions for the billing DEX permissions on Android 10+.

Android refuses to load a world-writable DEX host file. `adb push` creates it
with mode 0666, so the billing module must be tightened to 0644 before the
offer query injects it. Otherwise the failure surfaces only as a generic
"no offers returned" result instead of a setup error.
"""
import base64
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

script = Path(__file__).resolve().parents[1] / "ultra0.py"
spec = importlib.util.spec_from_file_location("ai_billing_module", script)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class BillingModulePermissionTests(unittest.TestCase):
    def _run(self, existing: bool, chmod_output: str = "ok"):
        calls = []

        def shell(*args, **kwargs):
            # sh() is called either as sh("shell", "<command>") or as
            # sh("push", <local>, <remote>); join the operands for readability.
            command = " ".join(str(a) for a in args)
            calls.append(command)
            if "chmod" in command:
                return chmod_output
            if command.startswith("shell ls "):
                return mod.MODULE_REMOTE if existing else ""
            return ""

        with patch.object(mod, "sh", side_effect=shell), \
             patch.object(mod, "MODULE_B64", base64.b64encode(b"dex").decode("ascii")), \
             patch.object(tempfile, "gettempdir", return_value="/tmp"):
            mod.ensure_module_apk()
        return calls

    def test_existing_module_is_made_read_only(self):
        commands = self._run(existing=True)
        self.assertTrue(
            any(c.startswith("shell chmod 644 ") and mod.MODULE_REMOTE in c for c in commands),
            commands)
        self.assertFalse(any(c.startswith("push ") for c in commands))

    def test_fresh_install_is_pushed_then_made_read_only(self):
        commands = self._run(existing=False)
        push_index = next(i for i, c in enumerate(commands) if c.startswith("push "))
        chmod_index = next(i for i, c in enumerate(commands) if c.startswith("shell chmod 644 "))
        self.assertLess(push_index, chmod_index, commands)

    def test_chmod_failure_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "read-only"):
            self._run(existing=True, chmod_output="")

    def test_chmod_targets_the_remote_dex(self):
        commands = self._run(existing=True)
        chmods = [c for c in commands if "chmod" in c]
        self.assertEqual(len(chmods), 1)
        self.assertIn(mod.MODULE_REMOTE, chmods[0])


if __name__ == "__main__":
    unittest.main()
