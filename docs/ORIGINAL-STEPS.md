# Historical Google AI Pro stage reference (English)

> The original author claimed the following promotional sequence existed. The alleged 12 + 6 + 6 + optional 6 month stacking is **unverified** and may be ineligible, unavailable, paid, or rejected by Google Play. This is a translation of the procedure's intent, **not a promise of free service**.

## Environment

Use a compatible rooted Android emulator with the Google Play Store and Google One installed. Sign in to the desired Google account. Install Python 3.10+, Android platform-tools and the Frida version required by this repository. Verify the account and payment conditions in Google Play.

Run `tools/windows/setup-environment.bat` from the repository root (or double-click it) to invoke the original setup helper, or use the maintained `run-all.ps1 -SetupOnly` command. Setup may install dependencies, restart Frida, and modify emulator network settings.

## Guided PowerShell commands aligned with the author's steps

```powershell
# Step 0: environment validation (no checkout)
.\run-all.ps1 -Step 0

# Step 1: offers (no checkout; this is the default)
.\run-all.ps1 -Step 1

# Step 2: author's first 12-month offer
.\run-all.ps1 -Step 2 -Email account@gmail.com

# Step 3: original subscription update (+6 months claimed)
.\run-all.ps1 -Step 3 -Email account@gmail.com

# Step 4: second original update (+6 months claimed)
.\run-all.ps1 -Step 4 -Email account@gmail.com

# Step 5: optional alternative offer (+6 months claimed)
.\run-all.ps1 -Step 5 -Email account@gmail.com

# Entire original sequence: preflight, offer list, Steps 2-4, optional Step 5
.\run-all.ps1 -AllStages

# Resume from Step 3 without replaying Step 2 on an already-active plan
.\run-all.ps1 -AllStages -StartStep 3

# Original account-check bypass (only when necessary)
.\run-all.ps1 -AllStages -Force
```

`-AllStages` uses numbered prompts instead of long phrases: **1 = Continue, 2 = Skip / End run, 0 = Stop**. It asks before running, after you verify each Google Play subscription change, and before optional Step 5. A standalone `-Step N` performs its selected step without typed confirmation (`RUN N`, `NO ACTIVE`, `VERIFIED`); the selected step itself is the explicit instruction to attempt checkout. `-Force` only bypasses Play account checking, not offer eligibility or payment validation; in `-AllStages` it still requires a numeric approval, while a single step does not prompt.

For the **Step 3–5** subscription replacement, the revised code rejects missing purchase tokens, expired or wrong-account database tokens, or unsupported replacement modes instead of silently falling back to a fresh standalone purchase. If the optional BillingClient query finds multiple subscriptions, it only accepts the matching original Google AI Pro product ID.

**Current internal report statuses:** `listed` means the offer query returned data; `checkout_requested` is still assigned by `ultra0.py` when the script reports tapping **Subscribe** after checking displayed terms; `checkout_not_confirmed` means the tap was not confirmed. None of these statuses proves a completed purchase, active subscription or extended renewal date. Confirm the actual charge and next renewal date in Google Play before continuing. The proposed 12+6+6(+6) durations remain unverified historical claims.

## Maintained entrypoints

| Action | Filename | Description |
| --- | --- | --- |
| Check environment | `legacy/windows/00-environment-check.bat` | Checks ADB, Frida and required Android packages |
| Read available offers | `legacy/windows/01-list-offers.bat` | Queries offers; no checkout |
| Original stage 1 | `legacy/windows/02-pro-12-months.bat` | Claimed one-year promotional flow; **possible purchase** |
| Original stage 2 | `legacy/windows/03-pro-add-6-months.bat` | Claimed subscription replacement with `--stack`; **possible purchase** |
| Original stage 3 | `legacy/windows/04-pro-add-6-months-again.bat` | Additional claimed `--stack` flow; **possible purchase** |
| Alternate stage | `legacy/windows/05-pro-alternative-6-months.bat` | Claimed alternative offer; **possible purchase** |

All batch paths above are relative to the repository root. These legacy-compatible batch files preserve the original `--force` option and **do not verify the Play account**. The guided `run-all.ps1 -AllStages` includes optional Step 5 and checks the account by default. Add `-Force` only to mirror the author's deliberate account-check bypass; you must confirm that choice. In the guided `-AllStages` flow, prompts use numeric approvals and users must independently verify the Google Play subscription. **Standalone `-Step 2..5` does not prompt for a second PowerShell approval** and can initiate a real checkout.

## What the original script attempts

For a product with an existing subscription, it may read an existing `purchaseToken` from Google Play's local database and construct `BillingFlowParams.SubscriptionUpdateParams` to request a subscription replacement. The author claimed this could extend a promotional trial, but an accepted API call or offer token does not establish an entitlement or a new renewal date. Only Google's live checkout and subscription record establish actual terms.

Do not assume a cancelled subscription is eligible for stacking or that cancellation preserves an advertised term. After any transaction, check the **actual renewal date and currency** in Google Play Store → Payments & subscriptions → Subscriptions. Do not confirm purchases simply because a summary says the price is zero.

## Troubleshooting

- **Account mismatch:** Verify the active Play Store profile; do not bypass the check.
- **Connection timeout:** Confirm the device, internet connectivity and running apps.
- **Activity lookup errors:** Inspect the Frida/Android Runtime version and run `python scripts/diagnose-activity.py --serial YOUR_DEVICE`.
- **Offer ineligible or checkout price is nonzero:** Stop and review the actual terms in Play Store.
- **Unknown subscription result:** Check the subscription record directly; don't rerun automatic checkout until you know what happened.

Read [the maintained English guide](DETAILED-GUIDE.md) and [security notes](../SECURITY.md) before running the optional live billing flow.
