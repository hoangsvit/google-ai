# Detailed setup, operations, and troubleshooting

This guide describes the maintained **Python + ADB + Frida** workflow. The Playwright wrapper was removed because it only delegated to the same Python script and added an unnecessary Node.js dependency. The optional **pure JavaScript test** for the Frida hook still uses Node.js in CI; end users do **not** need Node.js.

[Back to README](../README.md) · [Security precautions](../SECURITY.md) · [Original stage reference (English)](ORIGINAL-STEPS.md)

> **Safety:** Offer data and a first pricing phase of 0 do **not** prove that a promotion applies to the account, that the subscription is active, or that time can be stacked. The original `ultra0.py` may automatically click **Subscribe** when not run in `--list` mode. Always inspect Google's live pricing, recurring charges, cancellation terms and actual subscription record in Google Play.

## Prerequisites

- Windows with MuMu, or another Android emulator/device that supports debugging, root and a compatible Frida server.
- Python 3.10+; Android SDK platform-tools or a working ADB path.
- Google Play Store and Google One installed and usable on the Android device.
- Frida 16.5.9 is pinned by this repository's current implementation, not guaranteed compatible with every Android/ART build.
- Account signed into Google Play Store; check the active profile carefully.

The original helper `setup_env.py` can install Frida and ADB and attempt to connect emulator endpoints. Review its source first: setup and runtime checks may install/replace dependencies or change Android proxy/network settings.

## Quick start

Clone the repository if needed, or update it:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
git pull --ff-only
```

### Install ADB first (Windows PowerShell)

Run the setup helper from the repository directory:

```powershell
python --version
python setup_env.py
```

MuMuPlayer must be installed separately from the [official NetEase download](https://www.mumuplayer.com/download/); this helper does **not** install MuMu. It searches `ADB_PATH`, existing `platform-tools` folders, known MuMu locations, and PATH. It verifies `adb.exe version` works. If it needs to download Google's official Platform-Tools, it extracts them in a fresh temporary directory and installs into the project or, if that directory is locked, `%LOCALAPPDATA%\google-ai\platform-tools`.

**If `adb` is not recognized in PowerShell:** You can use `.\\run-all.ps1 -Serial emulator-5554 -ListOnly` without changing PATH. Or run the local executable:

```powershell
.\\platform-tools\\adb.exe version
.\\platform-tools\\adb.exe devices
```

For a per-user installation, use `& "$env:LOCALAPPDATA\\google-ai\\platform-tools\\adb.exe" devices`.

**If PowerShell reports an inline Python syntax error or `UnicodeEncodeError: cp1252`:** Old versions passed inline `python -c` code through PowerShell and could corrupt Python quoting, then try to print Unicode status symbols using the wrong Windows codepage. Run `git pull --ff-only`. The maintained `run-all.ps1` uses `scripts/runtime-lookup.py` for ASCII-safe runtime discovery **and** sets `PYTHONIOENCODING` / UTF-8 output for child Python processes, avoiding the separate `cp1252` status-symbol crash.

**If `setup_env.py` previously raised `PermissionError: [Errno 13] ... platform-tools\\adb.exe`:** The file may be locked by an emulator/ADB process or protected by directory permissions. Update the repository with `git pull --ff-only` and rerun setup. The installer now avoids overwriting working ADB files and falls back to the per-user directory if the project folder cannot be updated. Do not force-delete the file or disable antivirus.

Then inspect the device:

```powershell
adb devices
adb -s emulator-5554 shell getprop ro.build.version.release
adb -s emulator-5554 shell getprop ro.build.version.sdk
adb -s emulator-5554 shell getprop ro.product.cpu.abi
```

Replace `emulator-5554` with the serial from `adb devices`. If no device is online, start MuMu, enable ADB debugging, approve device authorization and use the ADB endpoint documented by your emulator. Do not assume a universal port number. A device in `offline` or `unauthorized` state is not ready.

**One command for setup and diagnostics (automatic device selection):**

```powershell
.\run-all.ps1 -ListOnly
```

If `adb devices` lists several connections such as `127.0.0.1:16384`, `127.0.0.1:7555`, and `emulator-5554`, these may all point to the same Android instance. The tool checks each instance's boot UUID and treats matching UUIDs as aliases. If several different Android kernels are connected, it selects the one uniquely running Google One or the only one with Google One installed. It does **not** guess if the identification is inconclusive: specify `-Serial emulator-5554` (using a serial that really appears in `adb devices`). The single-step CLI exits rather than asking for an interactive device choice.

For setup only:

```powershell
.\run-all.ps1 -SetupOnly
```

For an individual original billing stage (possible real purchase):

```powershell
.\run-all.ps1 -Step 2 -Email your-email@gmail.com
```

For the complete original sequence (environment check, offer listing, Steps 2–4, and optional Step 5), run:

```powershell
.\run-all.ps1 -AllStages
```

**Resume after an active 12-month plan:** Do not repeat Step 2. For the guided `-AllStages` flow, the wrapper asks for a **numbered confirmation** that Google Play shows no active subscription before the Step 2 checkout. The text `NO ACTIVE` is no longer an input requirement. After reviewing the active Google AI Pro plan and next renewal date in Google Play, you can explicitly start at Step 3:

```powershell
.\run-all.ps1 -AllStages -StartStep 3
```

This asks you to choose 1 (Continue), 2 (Skip) or 0 (Stop), and does not infer whether prior extensions succeeded. An `already_subscribed` checkout error means there is no verified extra subscription period; stop instead of trying later stages.

The active Play Store email is detected automatically; `-Email` can specify an expected account. `-Force` passes the original Python `--force` to bypass **only** the account-verification check, after a numbered approval prompt. Normally it is unnecessary.

For `-AllStages`, all approvals use **1 = Continue, 2 = Skip / End run, 0 = Stop**. After each attempted subscription stage, review the Google Play plan, next payment date, and price before selecting 1. Optional Step 5 requires another numeric approval. Individual `-Step 2`, `-Step 3`, `-Step 4` or `-Step 5` commands are **non-interactive at the PowerShell confirmation layer**: no `RUN N`, `NO ACTIVE` or `VERIFIED` input is requested. Selecting a checkout step explicitly authorizes that attempt, which may tap Subscribe automatically if the current terms appear eligible. If the device or Play account is ambiguous, the standalone step fails closed with a diagnostic rather than asking for input. Check the real subscription and renewal date after the step. The explicit CLI command `-Step 1` remains the read-only offer-listing mode; running `.\run-all.ps1` **without arguments opens the Textual dashboard**.

The original Python code can click **Subscribe** automatically on a screen it interprets as a zero-priced checkout. This is a real billing flow, not a simulation, and the claimed subscription extensions are not guaranteed.

If local execution policy prevents PowerShell scripts, review the file and follow your organization's Windows execution-policy rules rather than disabling system protections globally.

## Direct Python and diagnostic commands

Environment check:

```powershell
python ultra0.py --check --serial emulator-5554
```

**Offer listing without checkout:**

```powershell
python ultra0.py --account "current@device" --no-add --list --plan pro12 --serial emulator-5554
```

In listing mode, the email placeholder identifies the device's current account and is **not proof that the account matches any intended email**. Check Google Play's profile in the emulator.

Read-only Activity inspection, after opening Google One in the emulator:

```powershell
python scripts/diagnose-activity.py --serial emulator-5554
```

The tool reports `ok` only when it can read a usable Android Activity through `ActivityThread`. It does not query or confirm a purchase.

## Android and Frida compatibility

The default Android Activity strategy is `--activity-method auto`: try `Java.choose()`, then fallback to `ActivityThread.mActivities`. Force one method for diagnostics with:

```powershell
python ultra0.py --check --serial emulator-5554
python scripts/diagnose-activity.py --serial emulator-5554
```

The guided PowerShell script accepts `-ActivityMethod auto|choose|thread`, and the Python CLI accepts `--activity-method auto|choose|thread`. A successful read-only Activity probe is not proof that checkout will work.

On some Android 15 / API 35 x86_64 emulator builds, Frida `Java.choose()` raises a `libart.so` / `EnsurePluginLoaded` error. This is a runtime compatibility issue distinct from Google Play account eligibility. The fallback may help, but is not guaranteed across Android vendors and versions.

## Original stage mapping (reference only)

| Stage | Original shortcut | Python option |
| --- | --- | --- |
| Claimed 12-month offer | `legacy/windows/02-pro-12-months.bat` | `--plan pro12` |
| Claimed additional six months | `legacy/windows/03-pro-add-6-months.bat` | `--plan pro6 --stack` |
| Claimed additional six months | `legacy/windows/04-pro-add-6-months-again.bat` | `--plan pro6b --stack` |
| Optional alternative six months | `legacy/windows/05-pro-alternative-6-months.bat` | `--plan pro6c --stack` |

The historical shortcuts are kept under `legacy/windows/` and use `--force` to bypass account verification and may initiate purchase flows. The guided PowerShell entrypoint uses `--no-switch` and verifies the detected account by default; explicit `-Force` mirrors the original account-check bypass and requires separate confirmation. The original 12+6+6 stacking claim is unverified and cannot be inferred from offer identifiers.

## Common failures

| Result | Meaning / next step |
| --- | --- |
| `account_unverified` | Script cannot read active Google Play email; open the Store profile and check account manually |
| `wrong_account` | Account read from Google Play differs from the target; do not bypass it |
| `app_not_started` | Google One package/process did not start; open app manually and inspect ADB process |
| `activity_lookup_failed` | Frida could not locate a usable Activity; check ART/Frida compatibility and read-only probe |
| `no_activity` | Running app has no usable Activity; return to a foreground Google One screen |
| `billing_flow_error` | BillingClient returned an error; read sanitized `launched` and `errors` fields |
| `launch_failed` | Script did not observe successful checkout launch; does not imply a purchase |
| `listed` | Offer details returned, but no checkout or subscription confirmed |

For local status without exposing offer tokens, select only fields from the report:

```powershell
Get-Content .\ultra0-report\eplusdotdev.json -Raw |
    ConvertFrom-Json |
    Select-Object status, error, launched, errors
```

Do **not** publish full JSON reports, offer tokens, purchase tokens, passwords, 2FA secrets or card data. The repository ignores common sensitive local files.

If a checkout is ever initiated, confirm subscription status, renewal date, amount and currency directly in **Google Play Store → Payments & subscriptions → Subscriptions**. A message saying a checkout window opened does not prove that any subscription was activated.

## Project files

- `ultra0.py`: Python entrypoint and original billing orchestration.
- `run-all.ps1`: Guided Windows workflow with safety checks.
- `setup_env.py`: Original setup helper.
- `query_sku.py`: Direct product/offer query helper.
- `assets/frida/billing.js`: Extracted Frida hook.
- `assets/modules/module_521.b64`: Original embedded DEX archive as Base64.
- `scripts/diagnose-activity.py`: Read-only ActivityThread probe.
- `scripts/runtime-lookup.py`: ASCII-safe runtime discovery for Windows PowerShell.
- `tests/`: Python tests and one dependency-free Node.js Frida JavaScript test.
- `.github/workflows/static-checks.yml`: Hosted CI; **no actual Android billing test**.

## Technical fixes and diagnostics

The maintained workflow includes compatibility fixes that are intentionally omitted from the quick-start README:

- **Windows PowerShell automatic variables:** older wrappers used `$pid`, which collides with the read-only `$PID` variable. The maintained wrapper uses `$googleOnePid` and CI checks for accidental assignments to reserved variables.
- **Android 15 and Frida process enumeration:** some Frida builds cannot verify `get_process(pid)` even when ADB can find Google One. The CLI checks the selected device and process identity via ADB before attaching; it refuses mismatched PIDs.
- **Account and subscription replacement checks:** ADB transport selection is deterministic when identifiable, and subscription updates fail closed when an appropriate existing purchase token or update mode cannot be verified.
- **PowerShell inline Python and Windows codepages:** the wrapper uses `scripts/runtime-lookup.py` to return ASCII-safe machine-readable values rather than fragile inline `python -c` commands.
- **ADB file permissions:** `setup_env.py` reuses a working Android platform-tools installation and falls back to a writable per-user location instead of overwriting a locked `adb.exe`.

To inspect the active Google One Activity without making a purchase:

```powershell
python scripts/diagnose-activity.py --serial emulator-5554
```


## Checkout shows a renewal price or backup-payment prompt

The Google Play popup **Turn on backup payment methods?** asks permission to charge alternate saved payment methods if a primary method fails. It does not itself prove a subscription offer was accepted, and this toolkit does not turn it on. See https://support.google.com/googleplay/answer/4646404.

A displayed amount such as **US$19.99** may be a later renewal price, not the amount payable today. The checkout parser distinguishes these by requiring an explicit **today $0** amount and the expected trial duration on the *live checkout screen*. It no longer assumes the first monetary amount is today's payment. If either detail cannot be checked, it records a reason in `ultra0-report/<account>.json`, leaves the Google Play UI open for review, and does not tap Subscribe. The original BillingClient offer's first phase is not proof of actual account eligibility. Avoid `-Force` when the checkout price is unclear.

## Google Play payment security error OR-REH-04

If the Play checkout shows **"Your transaction can't be completed. To continue this transaction, secure your account"** with **OR-REH-04**, this is a Google Play/payment-account security block, not a missing Frida Activity, a missing offer, or an unverified trial duration. A `launchBillingFlow` code of 0 means the checkout was opened, **not** that the purchase was accepted.

The script records `checkout_security_blocked` with checkout reason `payment_security_blocked`, **does not tap Subscribe**, leaves the Google Play dialog visible, and stops the stage sequence. It never uses `--force` to bypass Google payment restrictions.

Use Google's official [payment troubleshooting](https://support.google.com/googleplay/answer/1267137) and check alerts or verification requests in [Google Payments](https://payments.google.com/) and [Google Account Security](https://myaccount.google.com/security). Confirm the exact payment profile and billing-address information are correct; contact Google support if the restriction remains. Do not repeatedly retry billing stages or attempt later stacking steps until the issue is resolved and the actual subscription/renewal date is confirmed.
