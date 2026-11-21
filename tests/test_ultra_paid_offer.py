"""Offline Ultra 20x paid offer checks. No Android purchases are initiated."""
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "ultra_paid_guardrails", Path(__file__).resolve().parents[1] / "ultra0.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class UltraPaidOfferTests(unittest.TestCase):
    def test_checkout_js_uses_exact_sku_and_price_gate(self):
        script = app.build_js(plan="ultra19")
        self.assertIn('var PAID_ULTRA_19=true;', script)
        self.assertIn('var PRODUCTS=["g1.ai.ultra.3months_ip_90p.acq"];', script)
        self.assertIn('micros!=="19990000"', script)
        self.assertIn('renewalMicros!=="199990000"', script)
        self.assertIn('currency!=="USD"', script)
        self.assertIn('cycles!==3', script)
        self.assertNotIn('var STACK=true;', script)

    def test_paid_plan_rejects_stacking(self):
        for kwargs in ({"stack": True}, {"old_token": "secret"},
                       {"stack_mode": 5}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    app.build_js(plan="ultra19", **kwargs)

    def test_existing_pro_stage_does_not_enable_paid_selection(self):
        for plan in ("pro12", "pro6", "pro6b", "pro6c"):
            self.assertIn('var PAID_ULTRA_19=false;', app.build_js(plan=plan))

    def test_checkout_terms_are_never_auto_approved(self):
        visible = ("Google AI Ultra Subscribe Today US$19.99/month "
                   "for 3 months then US$199.99/month")
        result = app.assess_ultra_paid_terms(visible)
        self.assertEqual(result["reason"], "paid_terms_visible_manual_review")
        self.assertFalse(result["confirmed"])

    def test_wrong_paid_amount_or_renewal_does_not_verify(self):
        for screen in (
            "Google AI Ultra Subscribe Today US$49.99 for 3 months then US$199.99/month",
            "Google AI Ultra Subscribe Today US$19.99 for 3 months then US$99.99/month",
            "Google AI Ultra Subscribe Today EUR 19.99 for 3 months then EUR 199.99",
            "Google AI Ultra Subscribe Today US$19.99 for 1 month then US$199.99",
        ):
            with self.subTest(screen=screen):
                self.assertEqual(
                    app.assess_ultra_paid_terms(screen)["reason"], "paid_terms_unverified")

    def test_paid_security_block_does_not_confirm(self):
        result = app.assess_ultra_paid_terms(
            "Google AI Ultra Subscribe US$19.99 for 3 months then "
            "US$199.99 OR-REH-04")
        self.assertEqual(result["reason"], "payment_security_blocked")
        self.assertFalse(result["confirmed"])

    def test_ultra_checkout_never_auto_taps_subscribe(self):
        with patch.object(app, "current_play_account", return_value="test@example.com"), \
             patch.object(app, "launch_app", return_value=123), \
             patch.object(app, "run_trial", return_value={
                 "offers": [{"product": app.ULTRA_19_SKU,
                             "micros": app.ULTRA_19_PRICE_MICROS}],
                 "launched": {"code": 0}, "errors": [],
             }), \
             patch.object(app, "inspect_ultra_paid_checkout",
                          return_value={"reason": "paid_terms_visible_manual_review",
                                        "confirmed": False}) as inspect, \
             patch.object(app, "confirm_zero") as auto_tap, \
             patch.object(app, "verify") as verify:
            outcome = app.process("test@example.com", add=False, no_switch=True,
                                  plan="ultra19")
        self.assertEqual(outcome["status"], "paid_checkout_review_required")
        inspect.assert_called_once()
        auto_tap.assert_not_called()
        verify.assert_not_called()

    def test_paid_ultra_needs_clean_account_confirmation_before_device_setup(self):
        with patch.object(sys, "argv", [
                "ultra0.py", "--plan", "ultra19", "--account", "test@example.com",
                "--no-add", "--no-switch"]), patch.object(app, "find_adb") as adb:
            with self.assertRaises(SystemExit) as raised:
                app.main()
        self.assertEqual(raised.exception.code, 2)
        adb.assert_not_called()

    def test_pro_cannot_inherit_clean_account_flag(self):
        with patch.object(sys, "argv", [
                "ultra0.py", "--plan", "pro12", "--account", "test@example.com",
                "--clean-account-confirmed"]), patch.object(app, "find_adb") as adb:
            with self.assertRaises(SystemExit):
                app.main()
        adb.assert_not_called()

    def test_direct_cli_refuses_force_before_device_setup(self):
        with patch.object(sys, "argv", ["ultra0.py", "--plan", "ultra19",
                                       "--account", "test@example.com",
                                       "--no-add", "--no-switch", "--force"]), \
             patch.object(app, "find_adb") as adb:
            with self.assertRaises(SystemExit) as raised:
                app.main()
        self.assertEqual(raised.exception.code, 2)
        adb.assert_not_called()

    def test_direct_cli_requires_account_and_no_switch(self):
        with patch.object(sys, "argv", ["ultra0.py", "--plan", "ultra19",
                                       "--account", "test@example.com",
                                       "--no-add"]), \
             patch.object(app, "find_adb") as adb:
            with self.assertRaises(SystemExit):
                app.main()
        adb.assert_not_called()


if __name__ == "__main__":
    unittest.main()
