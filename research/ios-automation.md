# iOS automation research (experimental, offline PoC)

This is a separate research CLI; it does not alter the Android dashboard, numbered stages, or checkout behavior. No Shadowrocket installation is required to run the PoC. It does not acquire live offers, install certificates, intercept traffic, modify responses, automate sign-in or initiate subscriptions.

## Run the offline prototype

From the repository root with Python 3.10+:

```sh
python -m research.ios_automation diagnose
python -m research.ios_automation diagnose --vphone-dir /path/to/vphone-linux
python -m research.ios_automation import-report /path/to/local-report.json
python -m unittest discover -s tests -p test_ios_research.py -v
```

Use an authorized local report or synthetic sample, never commit personal reports. On Windows use the equivalent local path. Diagnose checks script presence and local tool availability, not compatibility or whether a VM is running. Import recognizes schema 1 scan.skus entries, deduplicates observed IDs, ignores mapping targets and execution history, bounds input, and emits only identifiers and explicitly unverified status flags. An identifier is not an offer, a price, an eligible account, or an active entitlement.

Example synthetic report:

```json
{"schemaVersion":1,"scan":{"skus":[{"id":"g1.example.product"}]}}
```

## Research gates

| Gate | Evidence required | Current status |
| --- | --- | --- |
| Host prerequisites | Supported OS, resources, trusted upstream setup | Partial local diagnostics |
| VM boot | Explicit local user-started boot, UI and input | Not tested |
| Networking | Authorized basic connectivity | Not tested |
| Google app | Legitimate installation and supported operation | Not tested |
| Account and StoreKit | User-controlled sign-in, official StoreKit availability | Not tested |
| SKU reporting | Local sanitized export or authorized test fixtures | Offline prototype |
| UI integration | Separate iOS adapter, no changes to Android checkout gates | Future |

Stop at a failed gate; never interpret a VM boot as proof of StoreKit compatibility. Use an owned development app with StoreKit Testing or mock data for automation tests; do not substitute product identifiers to obtain unintended pricing, bypass account eligibility or automate live checkout. Keep live accounts, tokens and payment data out of CI and reports.

## References and provenance

- [vphone-linux](https://github.com/YahiaAngelo/vphone-linux) — upstream VM setup and constraints, including WSL software graphics and unverified networking.
- [vphone-cli](https://github.com/Lakr233/vphone-cli) — upstream virtual iPhone research.
- [g1-acq](https://github.com/crhywun/g1-acq) — documented report format, not a runtime dependency. No third-party source is copied; reuse rights must be established separately.
- [Apple StoreKit testing](https://developer.apple.com/documentation/storekit/testing-in-app-purchases-with-storekit-testing-in-xcode) — supported development testing.

No device, StoreKit or purchase compatibility is established by offline tests. Do not install or run untrusted VM software without reviewing its licensing and setup.
