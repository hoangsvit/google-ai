"""Offline guardrails for inspecting unverified third-party promotion SKUs."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

source = Path(__file__).resolve().parents[1] / "ultra0.py"
spec = importlib.util.spec_from_file_location("promo_inspection", source)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class PromotionSkuInspectionTests(unittest.TestCase):
    def test_candidate_skus_are_fixed_and_unique(self):
        self.assertEqual(app.READ_ONLY_PROMO_SKUS, (app.ULTRA_19_SKU,))
        self.assertEqual(len(set(app.READ_ONLY_PROMO_SKUS)), 5)

    def test_exact_sku_is_queried_only_in_list_mode(self):
        for sku in app.READ_ONLY_PROMO_SKUS:
            with self.subTest(sku=sku):
                js = app.build_js(list_only=True, inspect_sku=sku)
                self.assertIn('var PRODUCTS=["' + sku + '"];', js)
                self.assertIn("var LIST_ONLY=true;", js)
                self.assertNotIn('var PRODUCTS=["g1.play.20tb","g1.play.ai.pro","g1.30tb"];', js)

    def test_unknown_or_checkout_sku_requests_fail_closed(self):
        sku = app.READ_ONLY_PROMO_SKUS[0]
        for options in (
            {"inspect_sku": sku},
            {"list_only": True, "inspect_sku": sku, "stack": True},
            {"list_only": True, "inspect_sku": sku, "old_token": "token"},
            {"list_only": True, "inspect_sku": sku, "stack_mode": 5},
            {"list_only": True, "inspect_sku": sku, "plan": "pro12"},
            {"list_only": True, "inspect_sku": "unknown.product"},
        ):
            with self.subTest(options=options):
                with self.assertRaises(ValueError):
                    app.build_js(**options)

    def test_cli_disallows_force_before_environment_changes(self):
        with patch.object(sys, "argv", ["ultra0.py", "--inspect-sku",
                                       app.READ_ONLY_PROMO_SKUS[0], "--force"]), \
             patch.object(app, "find_adb") as find_adb:
            with self.assertRaises(SystemExit) as raised:
                app.main()
        self.assertEqual(raised.exception.code, 2)
        find_adb.assert_not_called()

    def test_cli_inspection_never_calls_checkout(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(sys, "argv", ["ultra0.py", "--inspect-sku",
                                       app.READ_ONLY_PROMO_SKUS[0]]), \
             patch.object(app, "REPORT_DIR", Path(directory)), \
             patch.object(app, "find_adb", return_value="adb"), \
             patch.object(app, "pick_device"), \
             patch.object(app, "ensure_root"), \
             patch.object(app, "ensure_network"), \
             patch.object(app, "ensure_frida_server"), \
             patch.object(app, "ensure_module_apk"), \
             patch.object(app, "ensure_vending"), \
             patch.object(app, "current_play_account", return_value="sample@example.com"), \
             patch.object(app, "launch_app", return_value=123), \
             patch.object(app, "run_trial", return_value={
                 "offers": [{"product": "test", "id": "trial", "micros": "0"}],
                 "launched": None, "errors": []}) as query, \
             patch.object(app, "confirm_zero") as checkout, \
             patch.object(app, "verify") as verify:
            self.assertEqual(app.main(), 0)
            self.assertTrue(query.call_args.kwargs["list_only"])
            self.assertEqual(query.call_args.kwargs["inspect_sku"],
                             app.READ_ONLY_PROMO_SKUS[0])
            checkout.assert_not_called()
            verify.assert_not_called()


if __name__ == "__main__":
    unittest.main()
