"""No-device Frida target selection and subscription state regression tests."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

source = Path(__file__).resolve().parents[1] / "ultra0.py"
spec = importlib.util.spec_from_file_location("original_flow_guardrails", source)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def mock_dev(device_id, name="com.google.android.apps.subscriptions.red"):
    device = MagicMock()
    device.id = device_id
    device.type = "usb"
    device.get_process.return_value = types.SimpleNamespace(name=name)
    return device


class OriginalFlowGuardrails(unittest.TestCase):
    def test_read_only_transient_frida_failure_restarts_once(self):
        class TransportError(Exception):
            pass
        frida = types.SimpleNamespace(TransportError=TransportError)
        expected = {"offers": [{"id": "test"}]}
        with patch.dict(sys.modules, {"frida": frida}), \
             patch.object(mod, "run_trial", side_effect=[TransportError(), expected]) as run, \
             patch.object(mod, "ensure_frida_server") as server, \
             patch.object(mod, "launch_app", return_value=456):
            self.assertEqual(mod.query_offers_with_recovery(123, plan="pro12"), expected)
        server.assert_called_once()
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args.args[0], 456)
        self.assertTrue(run.call_args.kwargs["list_only"])

    def test_unknown_failure_is_not_retried(self):
        with patch.dict(sys.modules, {"frida": types.SimpleNamespace()}), \
             patch.object(mod, "run_trial", side_effect=RuntimeError("wrong device")) as run, \
             patch.object(mod, "ensure_frida_server") as server:
            with self.assertRaisesRegex(RuntimeError, "wrong device"):
                mod.query_offers_with_recovery(123)
        run.assert_called_once()
        server.assert_not_called()

    def test_google_play_unavailable_is_not_eligibility_proof(self):
        result = mod.assess_checkout_terms("Error The item you requested is not available for purchase. Got it")
        self.assertEqual(result["reason"], "purchase_unavailable")

    def test_paid_stage_does_not_use_read_only_recovery(self):
        with patch.object(mod, "current_play_account", return_value="test@example.com"), \
             patch.object(mod, "launch_app", return_value=123), \
             patch.object(mod, "query_offers_with_recovery") as recover, \
             patch.object(mod, "run_trial", side_effect=RuntimeError("connection lost")) as run:
            with self.assertRaisesRegex(RuntimeError, "connection lost"):
                mod.process("test@example.com", add=False, no_switch=True)
        run.assert_called_once()
        recover.assert_not_called()

    def test_session_is_detached_on_script_failure(self):
        session = MagicMock()
        session.create_script.side_effect = RuntimeError("script failure")
        device = MagicMock()
        device.attach.return_value = session
        with patch.object(mod, "get_target_frida_device", return_value=device):
            with self.assertRaisesRegex(RuntimeError, "script failure"):
                mod.run_trial(123, list_only=True)
        session.detach.assert_called_once()

    def test_serial_match_takes_precedence(self):
        devices = [mock_dev("127.0.0.1:16384"), mock_dev("emulator-5554")]
        module = types.SimpleNamespace(get_device_manager=lambda: types.SimpleNamespace(
            enumerate_devices=lambda: devices))
        with patch.dict(sys.modules, {"frida": module}), \
             patch.object(mod, "verify_adb_target_pid", return_value=mod.PKG):
            self.assertIs(mod.get_target_frida_device(123, "emulator-5554"), devices[1])

    def test_different_frida_devices_do_not_default_to_first(self):
        devices = [mock_dev("device-a"), mock_dev("device-b")]
        module = types.SimpleNamespace(get_device_manager=lambda: types.SimpleNamespace(
            enumerate_devices=lambda: devices))
        with patch.dict(sys.modules, {"frida": module}):
            with self.assertRaisesRegex(RuntimeError, "Cannot map ADB serial"):
                mod.get_target_frida_device(123, "emulator-5554")

    def test_frida_process_enumeration_failure_does_not_block_valid_adb_pid(self):
        device = mock_dev("emulator-5554")
        device.get_process.side_effect = RuntimeError("Android 15 process enumeration unavailable")
        module = types.SimpleNamespace(get_device_manager=lambda: types.SimpleNamespace(
            enumerate_devices=lambda: [device]))
        with patch.dict(sys.modules, {"frida": module}), \
             patch.object(mod, "verify_adb_target_pid", return_value=mod.PKG):
            self.assertIs(mod.get_target_frida_device(11004, "emulator-5554"), device)
        device.get_process.assert_not_called()

    def test_unrelated_adb_process_is_rejected(self):
        from unittest.mock import patch as mock_patch
        device = mock_dev("emulator-5554")
        module = types.SimpleNamespace(get_device_manager=lambda: types.SimpleNamespace(
            enumerate_devices=lambda: [device]))
        with patch.dict(sys.modules, {"frida": module}), \
             mock_patch.object(mod, "verify_adb_target_pid",
                               side_effect=RuntimeError("ADB PID 123 is unrelated")):
            with self.assertRaisesRegex(RuntimeError, "unrelated"):
                mod.get_target_frida_device(123, "emulator-5554")

    def test_missing_purchase_token_has_distinct_failure(self):
        s, message = mod.diagnose_launch_failure(
            {"launched": None, "errors": [{"ev": "no_purchase"}]})
        self.assertEqual(s, "subscription_update_unavailable")
        self.assertIn("token", message)

    def test_read_only_listing_saves_verified_play_account(self):
        with patch.dict(sys.modules, {"frida": types.SimpleNamespace()}), \
             patch.object(mod, "current_play_account", return_value="test@example.com"), \
             patch.object(mod, "launch_app", return_value=123), \
             patch.object(mod, "run_trial", return_value={
                 "offers": [{"id": "12months-eft", "micros": "0"}],
                 "launched": None, "errors": []}):
            result = mod.process("current@device", add=False, list_only=True, plan="pro12")
        self.assertEqual(result["status"], "listed")
        self.assertEqual(result["detected_play_account"], "test@example.com")

    def test_checkout_launch_is_not_subscription_activation(self):
        with patch.dict(sys.modules, {"frida": types.SimpleNamespace()}), \
             patch.object(mod, "current_play_account", return_value=""), \
             patch.object(mod, "launch_app", return_value=123), \
             patch.object(mod, "run_trial", return_value={
                 "offers": [{"id": "12months-eft", "micros": "0"}], "launched": {"code": 0}, "errors": [],
                 "purchase": None}), \
             patch.object(mod, "confirm_zero", return_value={"confirmed": True}), \
             patch.object(mod, "verify", return_value="Google AI Pro subscription"):
            result = mod.process("current@device", add=False, list_only=True)
            self.assertEqual(result["status"], "listed")
        with patch.object(mod, "current_play_account", return_value="test@example.com"), \
             patch.object(mod, "launch_app", return_value=123), \
             patch.object(mod, "run_trial", return_value={
                 "offers": [{"id": "12months-eft", "micros": "0"}], "launched": {"code": 0}, "errors": [],
                 "purchase": None}), \
             patch.object(mod, "confirm_zero", return_value={"confirmed": True}), \
             patch.object(mod, "verify", return_value="Google AI Pro subscription"):
            result = mod.process("test@example.com", add=False, no_switch=True)
        self.assertEqual(result["status"], "checkout_requested")


if __name__ == "__main__":
    unittest.main()
