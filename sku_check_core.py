"""Strict, token-free model for explicit read-only SKU inspection.

This module never touches Android, Frida, billing or user accounts.
"""
from __future__ import annotations

import re
from decimal import Decimal

SKU_RE = re.compile(r"^g1\.[a-z0-9][a-z0-9._-]{2,127}$")
ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
PERIOD_RE = re.compile(r"^P(?:\d+[YMWD]){1,4}$")
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
MAX_SKUS = 10
MAX_OFFERS = 100
MAX_PHASES = 12


def validate_skus(values: list[str]) -> list[str]:
    if not values or len(values) > MAX_SKUS:
        raise ValueError("Select between 1 and 10 explicit product IDs")
    checked = []
    for value in values:
        if not isinstance(value, str) or not SKU_RE.fullmatch(value):
            raise ValueError("Invalid product ID: use g1. followed by letters, digits, dots, _ or -")
        if value not in checked:
            checked.append(value)
    return checked


def _id(value: object) -> str:
    return value if isinstance(value, str) and ID_RE.fullmatch(value) else ""


def _price(value: object) -> str | None:
    if isinstance(value, bool):
        return None
    value = str(value)
    if not value.isascii() or not value.isdecimal() or len(value) > 18:
        return None
    return str(int(value))


def _number(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    value = str(value)
    if not value.isascii() or not value.isdecimal() or len(value) > 5:
        return None
    return int(value)


def pricing_phase_warnings(phases: list[dict]) -> list[str]:
    """Describe incomplete or inconsistent pricing metadata for manual review.

    This is a display-only audit. A clean result does not establish account
    eligibility, the amount due today, or permission to open checkout.
    """
    warnings = []
    if not phases:
        return ["No pricing phases returned"]
    if len({phase.get("currency") for phase in phases}) != 1:
        warnings.append("Currency changes across phases")
    for index, phase in enumerate(phases, 1):
        mode = _number(phase.get("recurrence_mode"))
        cycles = _number(phase.get("billing_cycle_count"))
        if mode not in (1, 2, 3):
            warnings.append(f"Phase {index}: recurrence mode unknown")
        elif mode == 2 and not cycles:
            warnings.append(f"Phase {index}: finite billing cycle count missing or zero")
        elif mode == 1:
            if cycles != 0:
                warnings.append(f"Phase {index}: ongoing billing cycle count is not zero")
            if index != len(phases):
                warnings.append(f"Phase {index}: ongoing phase is not last")
        elif mode == 3 and cycles not in (0, 1):
            warnings.append(f"Phase {index}: one-time billing cycle count is unknown or inconsistent")
    return warnings


def sanitize_offers(raw: object, requested: list[str], *,
                    returned_skus: tuple[str, ...] = (),
                    no_offer_skus: tuple[str, ...] = (),
                    truncated: bool = False) -> dict:
    """Only allow safe IDs and complete phases; drop any token/account fields."""
    requested = validate_skus(requested)
    if not isinstance(raw, list):
        raise ValueError("Invalid offer response")
    offers = []
    seen = set()
    observed_products = set(requested).intersection(returned_skus)
    products_without_offers = set(requested).intersection(no_offer_skus)
    observed_products.update(products_without_offers)
    rejected_products = set()
    for row in raw[:MAX_OFFERS]:
        if not isinstance(row, dict):
            continue
        product = row.get("sku")
        if product not in requested:
            continue
        observed_products.add(product)
        if row.get("no_offers") is True:
            products_without_offers.add(product)
            continue
        offer = _id(row.get("offer_id"))
        base_plan = _id(row.get("base_plan_id"))
        # Subscription offers may have an empty offer ID for base plans.
        if not base_plan or (row.get("offer_id") not in ("", None) and not offer):
            rejected_products.add(product)
            continue
        phases = []
        supplied = row.get("phases")
        if not isinstance(supplied, list) or not 1 <= len(supplied) <= MAX_PHASES:
            rejected_products.add(product)
            continue
        for ph in supplied:
            if not isinstance(ph, dict):
                continue
            micros = _price(ph.get("price_amount_micros"))
            currency = ph.get("currency")
            period = ph.get("billing_period")
            if (micros is None or not isinstance(currency, str) or
                    not CURRENCY_RE.fullmatch(currency) or
                    not isinstance(period, str) or not PERIOD_RE.fullmatch(period)):
                continue
            phases.append({
                "price_amount_micros": micros,
                "currency": currency,
                "billing_period": period,
                "billing_cycle_count": _number(ph.get("billing_cycle_count")),
                "recurrence_mode": _number(ph.get("recurrence_mode")),
            })
        if len(phases) != len(supplied):
            rejected_products.add(product)
            continue
        key = (product, base_plan, offer)
        if key in seen:
            continue
        seen.add(key)
        offers.append({
            "sku": product, "offer_id": offer, "base_plan_id": base_plan,
            "phases": phases,
            "pricing_phase_warnings": pricing_phase_warnings(phases),
            "eligibility_verified": False, "subscription_active_verified": False,
        })
    valid_products = {row["sku"] for row in offers}
    unusable = rejected_products | (observed_products - valid_products - products_without_offers)
    return {
        "status": ("observed" if offers else "unusable_metadata" if unusable
                   else "no_offers" if products_without_offers else "not_returned"),
        "items": offers,
        "requested_skus": requested,
        "missing_skus": [sku for sku in requested if sku not in observed_products],
        "no_offer_skus": [sku for sku in requested if sku in products_without_offers],
        "unusable_skus": [sku for sku in requested if sku in unusable],
        "truncated": truncated or len(raw) > MAX_OFFERS,
        # Device-bound metadata is not proof of the active Play profile.
        "account_binding_verified": False,
        "eligibility_verified": False,
        "subscription_active_verified": False,
    }


def render_result(result: dict) -> str:
    """Readable SKU + offer catalogue; never infer eligibility or expose tokens."""
    status = result.get("status", "query_error")
    messages = {
        "not_returned": "Google Play returned no matching product metadata.",
        "no_offers": "Product details returned without available subscription offers.",
        "unusable_metadata": "Product metadata returned, but pricing could not be validated.",
        "account_unverified": "Play account not verified. Recheck Step 1.",
        "device_not_ready": "Device/Google One/Frida is not ready. Recheck Step 1.",
        "billing_unavailable": "BillingClient did not return data.",
        "timeout": "SKU scan timed out; results are not complete.",
        "cancelled": "SKU scan cancelled.",
        "query_error": "SKU scan could not complete. Check device and try again.",
    }
    # Always display the boundary before any observed prices, even when
    # the input claims verification. This renderer cannot verify a profile.
    lines = ["SKU / PRODUCT / OFFER (PLAY ACCOUNT UNVERIFIED)"]
    items = result.get("items") if isinstance(result.get("items"), list) else []
    for row in items[:MAX_OFFERS]:
        if not isinstance(row, dict):
            continue
        sku = row.get("sku", "")
        base = row.get("base_plan_id", "")
        offer = row.get("offer_id") or "(base plan)"
        if any(not isinstance(x, str) or not ID_RE.fullmatch(x)
               for x in (sku, base)) or not isinstance(offer, str):
            continue
        if offer != "(base plan)" and not ID_RE.fullmatch(offer):
            continue
        lines.append(f"SKU: {sku}  |  Base: {base}  |  Offer: {offer}")
        phases = row.get("phases") if isinstance(row.get("phases"), list) else []
        for index, phase in enumerate(phases[:MAX_PHASES], 1):
            if not isinstance(phase, dict):
                continue
            try:
                micros = _price(phase["price_amount_micros"])
                if micros is None:
                    continue
                amt = Decimal(micros) / Decimal(1_000_000)
                currency = phase["currency"]
                period = phase["billing_period"]
                if (not isinstance(currency, str) or not CURRENCY_RE.fullmatch(currency)
                        or not isinstance(period, str) or not PERIOD_RE.fullmatch(period)):
                    continue
                amount = f"{amt:,.6f}".rstrip("0").rstrip(".")
                if "." not in amount:
                    amount += ".00"
                elif len(amount.rsplit(".", 1)[1]) == 1:
                    amount += "0"
                mode = _number(phase.get("recurrence_mode"))
                cycles = _number(phase.get("billing_cycle_count"))
                recurrence = ("ongoing" if mode == 1 else
                              f"{cycles} cycle(s)" if mode == 2 and cycles else
                              "one-time" if mode == 3 else "recurrence unknown")
                lines.append(f"  Phase {index}: {amount} {currency} / {period} ({recurrence})")
            except (KeyError, TypeError, ArithmeticError):
                continue
        warnings = pricing_phase_warnings([ph for ph in phases if isinstance(ph, dict)])
        if warnings:
            lines.append("  Pricing metadata incomplete or inconsistent:")
            for warning in warnings:
                lines.append(f"    - {warning}")
        else:
            lines.append("  Pricing phases observed; verify actual charges and renewal in Google Play.")
    if status in messages:
        lines.append(messages[status])
    missing = result.get("missing_skus")
    if isinstance(missing, list):
        for sku in missing[:MAX_SKUS]:
            if isinstance(sku, str) and SKU_RE.fullmatch(sku):
                lines.append(f"SKU: {sku}  |  Not returned (eligibility unknown)")
    no_offers = result.get("no_offer_skus")
    if isinstance(no_offers, list):
        for sku in no_offers[:MAX_SKUS]:
            if isinstance(sku, str) and SKU_RE.fullmatch(sku):
                lines.append(f"SKU: {sku}  |  No subscription offers returned")
    for sku in (result.get("unusable_skus") or [])[:MAX_SKUS]:
        if isinstance(sku, str) and SKU_RE.fullmatch(sku):
            lines.append(f"SKU: {sku}  |  Some returned metadata unavailable or invalid")
    if result.get("truncated") is True:
        lines.append("Offer details truncated locally; results are incomplete.")
    lines.append("Play account for additional SKU results: UNVERIFIED")
    lines.append("Eligibility: UNVERIFIED  |  Subscription: UNVERIFIED")
    lines.append("No checkout or subscription change was requested.")
    return "\n".join(lines)
