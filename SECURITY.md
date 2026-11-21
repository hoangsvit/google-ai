# Security and billing precautions

This is an independent toolkit, not affiliated with Google. The original author's code can use ADB root, a Frida server, an injected billing module and Google Play purchase flows. Review all scripts before running them.

- **Prefer offer-listing mode:** `run-all.ps1 -Step 1` (or the dashboard's **Check Device & Offers**), `run-all.ps1 -ListOnly`, or `ultra0.py --list`. These modes do **not request subscription checkout**, but environment preflight may still install/repair ADB or Frida and alter Android emulator or proxy/network settings; they are not completely side-effect-free.
- **Possible charges:** Non-list mode in the original Python code can automatically tap **Subscribe** for Pro Steps 2–5. Optional **Ultra Step 6** can open a paid checkout: the new code never automatically taps Subscribe for this plan, and users must verify the actual US$19.99/month x 3 and US$199.99/month renewal in Google Play. Never infer an entitlement from an offer token or the first pricing phase alone.
- **Account identity:** Avoid `--force` (it bypasses account matching). Confirm the selected Google Play account manually and verify the checkout account.
- **Tokens and credentials:** Never share offer tokens, purchase tokens, full report JSON, passwords, 2FA seeds or card details. Reports and `accounts.txt` remain local and must not be checked in.
- **Environment changes:** Setup commands may install/replace Frida or ADB and change Android emulator proxy/network settings. Use a device you control and a safe test environment.
- **Confirm actual status:** Verify active subscriptions, amount, currency, future renewal and cancellation conditions directly in Google Play Store → Payments & subscriptions → Subscriptions.
- **No hardware test coverage:** GitHub Actions only runs mocked and static tests; device/ROM/Frida compatibility varies.

Do not use this repository to bypass eligibility restrictions or other account controls.