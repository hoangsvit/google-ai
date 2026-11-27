"""Research Steps 6-19 are integrated directly into ultra0.py.

Offline only: no device, Frida session or checkout is ever started here.
"""
import unittest
from unittest.mock import patch

import ultra0


class Ultra0ResearchStepTests(unittest.TestCase):
    def test_all_steps_6_to_19_are_defined(self):
        self.assertEqual(sorted(ultra0.RESEARCH_STEPS), list(range(6, 20)))
        for step in range(6, 20):
            self.assertEqual(ultra0.plan_for_research_step(step), f"research{step}")
            self.assertEqual(ultra0.research_step_for_plan(f"research{step}"), step)
        self.assertIsNone(ultra0.research_step_for_plan("pro12"))
        self.assertIsNone(ultra0.research_step_for_plan("research5"))
        with self.assertRaises(ValueError):
            ultra0.plan_for_research_step(20)

    def test_match_requires_exact_product_period_and_price(self):
        offers = [
            {"product": "g1.2tb.ai.subs_variant", "id": "a", "micros": "0", "period": "P3M"},
            {"product": "g1.2tb.ai.subs_variant", "id": "b", "micros": "1990000", "period": "P3M"},
            {"product": "g1.play.20tb", "id": "c", "micros": "0", "period": "P3M"},
        ]
        # Step 9 is the free 3-month Pro offer; the paid 3-month one must not match.
        self.assertEqual(ultra0.match_research_offer(9, offers)["id"], "a")
        # Step 7 is the USD 1.99/month 3-month Pro offer.
        self.assertEqual(ultra0.match_research_offer(7, offers)["id"], "b")
        # Wrong price for the same product/period fails closed.
        self.assertIsNone(ultra0.match_research_offer(6, offers))
        # A 12-month reference accepts Google's P12M spelling as well as P1Y.
        yearly = [{"product": "g1.2tb.ai.subs_variant", "id": "y",
                   "micros": "1990000", "period": "P12M"}]
        self.assertEqual(ultra0.match_research_offer(8, yearly)["id"], "y")

    def test_build_js_narrows_products_and_sets_exact_target(self):
        js = ultra0.build_js(plan="research13")
        self.assertIn('var PRODUCTS=["g1.play.20tb", "g1.play.ai.pro"];', js)
        self.assertIn('var TARGET_PERIOD="P3M"; var TARGET_MICROS="9990000";', js)
        js = ultra0.build_js(plan="research9")
        self.assertIn('var PRODUCTS=["g1.2tb.ai.subs_variant"];', js)
        self.assertIn('var TARGET_PERIOD="P3M"; var TARGET_MICROS="0";', js)
        # Existing plans keep their previous behaviour (no target assignment).
        self.assertNotIn('var TARGET_PERIOD="', ultra0.build_js(plan="pro12"))

    def test_unverified_product_steps_fail_closed(self):
        for step in (10, 11, 12, 17, 18, 19):
            with self.assertRaises(ValueError):
                ultra0.build_js(plan=f"research{step}")
            self.assertIsNone(ultra0.match_research_offer(step, [
                {"product": "g1.2tb.ai.subs_variant", "id": "x",
                 "micros": "0", "period": "P1M"}]))
        with patch.object(ultra0, "add_account") as add:
            rec = ultra0.process("current@device", plan="research19",
                                 add=False, no_switch=True)
        self.assertEqual(rec["status"], "research_product_unverified")
        self.assertEqual(rec["research_step"], 19)
        add.assert_not_called()

    def test_billing_js_has_target_selection_branch(self):
        self.assertIn('TARGET_PERIOD==="P1Y" && period==="P12M"', ultra0.FRIDA_JS)
        self.assertIn("best.target", ultra0.FRIDA_JS)

    def test_free_research_step_checkout_terms_use_reference_duration(self):
        text = "Google AI Pro Subscribe Today US$0 3 months free trial"
        result = ultra0.assess_checkout_terms(text, expected_plan="research9")
        self.assertEqual(result["reason"], "zero_today_and_duration_verified")
        # A paid research step can never pass the $0-today gate.
        paid = ultra0.assess_checkout_terms(
            "Google AI Pro Subscribe Today $0.99 1 month offer",
            expected_plan="research6")
        self.assertEqual(paid["reason"], "today_price_unverified")


if __name__ == "__main__":
    unittest.main()
