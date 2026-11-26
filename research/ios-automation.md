# iOS automation research (experimental, offline PoC and local VM wrapper)

This is a separate research CLI; it does not alter the Android dashboard, numbered stages, or checkout behavior. No Shadowrocket installation is required to run the PoC. It does not acquire live offers, install certificates, intercept traffic, modify responses, automate sign-in or initiate subscriptions.

## Choose a backend

- **Windows without WSL2:** [ASoftware Windows-native adapter](ios-windows.md) (preferred Windows research path).
- **Linux / WSL2:** vphone-linux adapter below.

Neither backend has established Google App or StoreKit compatibility. The Android toolkit is unchanged.

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

## Local VM lifecycle (Linux / WSL2)

Use a separate, reviewed vphone-linux checkout on the Linux filesystem. The wrapper deliberately does not download or install unreviewed software itself. Native Windows and macOS execution are not supported by this adapter; Windows users must run the commands inside WSL2. Follow the upstream requirements and review the firmware license first.

```sh
python -m research.ios_vphone --vphone-dir ~/vphone-linux setup
python -m research.ios_vphone --vphone-dir ~/vphone-linux setup --execute
python -m research.ios_vphone --vphone-dir ~/vphone-linux create --execute
python -m research.ios_vphone --vphone-dir ~/vphone-linux list
python -m research.ios_vphone --vphone-dir ~/vphone-linux start --vm YOUR_VM_NAME --execute
python -m research.ios_vphone --vphone-dir ~/vphone-linux stop --vm YOUR_VM_NAME --execute
python -m unittest discover -s tests -p 'test_ios*.py' -v
```

Without --execute, state-changing actions only print the planned command. List runs the upstream listing script. Setup and create require an interactive terminal and retain upstream prompts; they may download firmware, use sudo and change the host. Start requires an explicit named VM and requests no automatic unlock. Stop requests upstream shutdown, which can interrupt guest work. Save work first. Interrupted commands may leave a VM running: list before retrying. A successful upstream start exit code does not prove iOS boot or network readiness. No account or subscription actions are supported. This adapter is mock-tested by design and awaits real host validation.

## Interactive console and daemon health

```sh
python -m research.ios_menu --vphone-dir ~/vphone-linux
python -m research.ios_status --vphone-dir ~/vphone-linux --cid 3
```

Use the actual CID from the VM list, not necessarily 3. The menu groups diagnostics, setup, creation, listing, start, health, local report import and stop. Every state-changing action previews the command and asks for confirmation; upstream interactive prompts remain active. The health command calls only GET /v1/health through the local vphoned tool (20-second timeout). A positive result confirms a daemon response, not boot completion, screen readiness, Internet access, app installation, account identity or StoreKit. Raw daemon responses are not printed or stored. Run it only with a VM you own.

### Hardware acceptance checklist

After preparing a supported host and reviewing upstream licensing:

- List the VM and confirm its unique guest CID.
- Start the named VM, confirm screen responsiveness manually and run health.
- Manually check basic network access and legitimate app installation; do not assume either works.
- Validate StoreKit separately using an owned development app and Xcode StoreKit Testing, not live subscription checkout.
- Import a synthetic or authorized local SKU report and confirm that all eligibility flags remain false.
- Shut down the VM after saving work and verify the list.

If a gate fails, retain its unverified status. Offline CI cannot replace this checklist.

## Research gates

| Gate | Evidence required | Current status |
| --- | --- | --- |
| Host prerequisites | Supported OS, resources, trusted upstream setup | Partial local diagnostics |
| VM boot | Explicit local user-started boot, UI and input | Lifecycle and daemon health tools added; hardware untested |
| Networking | Authorized basic connectivity | Not tested |
| Google app | Legitimate installation and supported operation | Not tested |
| Account and StoreKit | User-controlled sign-in, official StoreKit availability | Not tested |
| SKU reporting | Local sanitized export or authorized test fixtures | Offline prototype |
| UI integration | Separate iOS console, no changes to Android checkout gates | Interactive research console added; shared TUI deferred until hardware validation |

Stop at a failed gate; never interpret a VM boot as proof of StoreKit compatibility. Use an owned development app with StoreKit Testing or mock data for automation tests; do not substitute product identifiers to obtain unintended pricing, bypass account eligibility or automate live checkout. Keep live accounts, tokens and payment data out of CI and reports.

## References and provenance

- [vphone-linux](https://github.com/YahiaAngelo/vphone-linux) — upstream VM setup and constraints, including WSL software graphics and unverified networking.
- [vphone-cli](https://github.com/Lakr233/vphone-cli) — upstream virtual iPhone research.
- [g1-acq](https://github.com/crhywun/g1-acq) — documented report format, not a runtime dependency. No third-party source is copied; reuse rights must be established separately.
- [Apple StoreKit testing](https://developer.apple.com/documentation/storekit/testing-in-app-purchases-with-storekit-testing-in-xcode) — supported development testing.

No device, StoreKit or purchase compatibility is established by offline tests. Do not install or run untrusted VM software without reviewing its licensing and setup.
