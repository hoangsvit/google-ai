# ePlus AI Toolkit

**ePlus AI Toolkit** is a Windows-focused terminal toolkit with a read-only macOS preview for inspecting Google AI Pro offers on an Android emulator (including MuMu). It uses the upstream Python/ADB/Frida/Google Play workflow rather than replacing or bypassing those checks.

> **Important:** This is not an official Google product. Displaying an offer, a price of 0, or a checkout request does **not** prove that an account is eligible or that a subscription has been activated. Steps 2–5 may open Google Play checkout and automatically press **Subscribe**, potentially incurring charges. Confirm the Google Play account, the amount due today, recurring price and renewal date before starting any checkout.

## Requirements

- Windows with PowerShell 5.1+, Python 3.10+, and a running rooted MuMu emulator with ADB enabled.
- Google Play Store and Google One installed; sign in to the intended Google account.
- For a checkout stage, prepare a valid payment method in Google Play. The script does not make trial eligibility guarantees.

## macOS preview — read-only Android diagnostics

A separate macOS launcher is available for **Intel and Apple Silicon Macs**. This is an **early read-only preview** (Steps 0 and 1 only), **not yet feature-parity with the Windows subscription workflow**.

Requirements: macOS 11+ (recommended), Python 3.10+, Android SDK Platform-Tools (`adb`) on your PATH, and an **Android device or emulator with root, Google Play Store and Google One**. MuMu for Windows is not a Mac prerequisite. Standard non-root Google Play emulator images may not satisfy the existing Frida/root checks. The original Android engine may repair Frida or modify emulator/network settings even during diagnostics.

Install ADB using Homebrew or the [official Android Platform-Tools for Mac](https://developer.android.com/tools/releases/platform-tools):

```bash
brew install android-platform-tools
adb devices
```

Start the macOS dashboard from the repository directory:

```bash
sh run-macos.sh
```

The launcher creates a local ignored `.venv` if needed and installs pinned **Textual** and **Frida 16.5.9** there. Frida 16.5.9 has a macOS ARM64 wheel, but actual emulator compatibility varies. Run the standalone CLI check instead of TUI with:

```bash
sh run-macos.sh --check   # Step 0: root/ADB/Frida preflight; may adjust emulator setup
sh run-macos.sh --list    # Step 1: read available offers; no checkout
```

On macOS the TUI only offers Steps **0 (Environment)** and **1 (Available offers)**. **Checkout Steps 2–5, Run All and resume-from-step are deliberately blocked**, including through keyboard/argument entrypoints. Do not use `run-all.ps1` or Windows-only `setup_env.py` as macOS setup scripts; the native launcher and `macos_runner.py` take the read-only path.

**Validation status:** Offline tests on a macOS CI runner verify the launcher syntax, stage routing and checkout guards. Actual ADB, rooted Android hardware, Frida injection and Google Play behavior require manual testing and are **not guaranteed** by CI. The macOS build does not promise a successful subscription or eligibility.

## Get started: interactive dashboard

Start MuMu, enable ADB, install/sign into **Google Play Store** and **Google One**, then run from the repository folder:

```powershell
git pull --ff-only
.\run-all.ps1
```

The default entrypoint opens the **ePlus AI Toolkit** Textual dashboard. On first launch, the script installs the pinned Textual dependency if it is absent. When a step begins, the launcher can set up its pinned Frida dependency and locate/install ADB. You normally do **not** need to invoke `python setup_env.py` first. Installation and device preparation may make local environment changes; check the diagnostic output if setup fails.

### Main screen (recommended for first-time users)

1. Click **Check Device & Offers** to start **Step 1 – Available offers**. This is the read-only offer-listing action, **not a checkout**.
2. Monitor **Live Status** for the current step, elapsed time, activity and outcome. If output stops for 30 seconds, the UI warns that no new log has appeared; it does **not** automatically declare the operation frozen. **Show technical details** opens the captured terminal log.
3. Review the offers on the emulator and the fresh result report. Seeing an offer is not confirmation of eligibility. No subscription is purchased by Step 1.
4. Use **Advanced: Run by step** only if you explicitly need another step or a guided checkout sequence.

The sidebar shows Step 0–5 and their current-session progress markers. **Android Device** and **Google Account** cards start in an unchecked state and update when the underlying tool outputs matching device/account information. The account display masks the email address. The credits **@gylive** (original author) and **@hoangsvit** (maintainer) open their GitHub profiles on terminals that support opening links.

### Advanced run modes

Expand **Advanced: Run by step** to show the run-mode selector, starting-step selector and **one contextual Run button**:

| Run mode | What it does | Important boundary |
| --- | --- | --- |
| **One step only** | Runs the selected Step **0–5** and returns a result. | Does not continue to later steps automatically. |
| **From selected step** | Starts a guided sequence at the selected Step **2–5**. | Does not replay earlier steps. The next checkout requires manual review and confirmation. |
| **All: Steps 2–5** | Starts a guided sequence at **Step 2**. | It is **not** an unattended batch purchase. Later steps require explicit user verification and approval; Step 5 is optional. |

**Step 0** checks/prepares the environment and may repair Android/Frida or emulator settings; it is **not** the offer-listing shortcut. **Step 1** lists offers without checkout. **Steps 2–5** are separate, potentially billable Google Play checkout operations. If you already have an active subscription, do not blindly replay Step 2.

For checkout steps, the UI displays an **approval dialog before starting each step**. A `checkout_requested` result means only that checkout was requested, **not** that the plan is active. Only use **Verified in Google Play → Next** after independently confirming the subscription and renewal date in [Google Play Subscriptions](https://play.google.com/store/account/subscriptions). The next step still requires another approval. Failed, unverified or blocked outcomes do not authorize automatic progression.

### While a step is running

| Control | During Step 0–1 | During Step 2–5 |
| --- | --- | --- |
| **Check Device & Offers**, Run, Run mode and Step selection | Disabled while busy | Disabled while busy |
| **Help & Guide**, **Show technical details** | Available | Available |
| **Stop check / Stop after this step** | Requests termination of the local read-only process tree. | Prevents further steps; **does not kill an in-flight checkout**. |
| **Exit toolkit** / **Q** | Requests cancellation and exits after the check finishes. | Queues an exit after the current checkout step finishes. |
| **Verified in Google Play → Next** | Not applicable | Only appears for a reviewable result in a guided sequence. |

The Stop/Exit logic prioritizes avoiding an unknown payment outcome. Windows read-only cancellation uses a process-tree termination request; if the child process cannot be stopped, inspect technical details and the terminal. Neither Stop nor closing the terminal can undo a Google Play transaction that has already been submitted.

**Shortcuts:** **D** toggles technical details, **R** uses the selected advanced run mode, and **Q** requests a safe exit. The terminal may also expose Textual's own command palette shortcut. For normal navigation, use the on-screen controls.

### Compatibility and legacy CLI

The **same original PowerShell/Python engine** is used by the dashboard and the CLI. Command-line options `-Cli`, `-Step N`, `-AllStages`, `-StartStep N` and PowerShell `-Debug` remain available. Explicit `-Step` and `-AllStages` arguments select CLI behavior rather than the interactive dashboard. Legacy batch launchers remain for compatibility.

## CLI quick reference

For a **read-only offer check without opening the TUI**:

```powershell
.\run-all.ps1 -Step 1
```

The standalone `setup_env.py` and `setup-environment.bat` are repair tools
for advanced users, not prerequisites for the TUI.

The setup helper locates or installs ADB, configures Frida 16.5.9 and checks MuMu. Step 1 lists offers **without purchasing**. An unambiguous Android device and the active Play Store email are detected automatically; you usually do not need `-Serial` or `-Email`.

**Terminal output:** The default view shows only the device, account, offers, current step, and outcome. Technical logs are saved locally in `logs/` (ignored by Git). Use PowerShell's built-in `-Debug` parameter to show full diagnostics:

```powershell
.\run-all.ps1 -Step 1 -Debug
```

User-facing errors explain what happened and what to do next. Internal error codes and raw diagnostics appear with `-Debug`. Do not publish diagnostic logs without removing account identifiers and payment data.

### Run the original sequence through the CLI

```powershell
.\run-all.ps1 -AllStages
```

The **CLI** performs its environment check and offer listing before attempting the original Pro stages **2 → 3 → 4**, then offers optional **Step 5**. This differs from the TUI's **All: Steps 2–5** mode, which starts its guided sequence at Step 2. Both require user verification and approval before moving to another checkout. All guided prompts now use **1 = Continue, 2 = Skip / End run, 0 = Stop**. You no longer need to type `RUN ALL`, `VERIFIED`, `RUN 5`, `NO ACTIVE`, or `ACTIVE`. After an attempted transaction, check Google Play and choose 1 only if the subscription changed as expected. Step 5 is optional, and Step 2 requires confirming that no subscription is already active.

**Already subscribed after Step 2?** Do not rerun Step 2. To start at Step 3 without replaying Step 2, first verify the active plan and next renewal date in Google Play:

```powershell
.\run-all.ps1 -AllStages -StartStep 3
```

The script uses a numbered prompt (1/2/0); it cannot prove earlier extensions succeeded. **If Step 3 displays "You're already subscribed", stop.** No additional six months have been verified, and proceeding to Steps 4–5 is not recommended.

### Run one step

| Step | Action | Command |
| --- | --- | --- |
| 0 | Environment check | `.\run-all.ps1 -Step 0` |
| 1 | List Pro offers (read-only) | `.\run-all.ps1 -Step 1` |
| 2 | Original 12-month offer (`pro12`) | `.\run-all.ps1 -Step 2` |
| 3 | Original +6-month update (`pro6 --stack`) | `.\run-all.ps1 -Step 3` |
| 4 | Original second +6-month update (`pro6b --stack`) | `.\run-all.ps1 -Step 4` |
| 5 | Optional +6-month offer (`pro6c --stack`) | `.\run-all.ps1 -Step 5` |

**Single-step commands do not ask you to type confirmation phrases.** Choosing `-Step 2`, `-Step 3`, `-Step 4` or `-Step 5` explicitly starts that step after account/device and offer checks. The underlying script may automatically tap Subscribe on an eligible checkout. After it finishes, **verify subscription activation, renewal date and any charges yourself**. It never assumes `checkout_requested` means success.

If the account or device cannot be identified automatically, single-step mode stops and asks you to rerun with `-Email` or `-Serial` **as command-line arguments**, rather than prompting for input. If Step 2 has already been activated, do **not** run it again. The default `.\run-all.ps1` launches the TUI with the **Check Device & Offers** quick action (Step 1) visible; the advanced step selector is hidden until expanded.

### Optional arguments

```powershell
.\run-all.ps1 -AllStages -Email "account@gmail.com"   # Require this Play account
.\run-all.ps1 -Step 1 -Serial emulator-5554           # Choose an ADB connection
.\run-all.ps1 -AllStages -Force                        # Bypass account verification
```

`-Force` mirrors the author's `--force` **only for the Play account check**. Standalone `-Step N` runs do not prompt again; `-AllStages` still asks for a numeric approval when using `-Force`. It does not override Google Play eligibility, prices or subscription-update checks. Avoid it when the account is already detected.

## Results and documentation

Read-only offers and stage diagnostics are saved under `ultra0-report/`. A status such as `checkout_requested` is **not** confirmation of an active subscription. Check the real plan, charge, currency and renewal date at [Google Play Subscriptions](https://play.google.com/store/account/subscriptions).

- [Detailed setup and troubleshooting](docs/DETAILED-GUIDE.md)
- [Original author's steps and batch-file mapping](docs/ORIGINAL-STEPS.md)
- [Historical author notes](docs/AUTHOR-NOTES.md)
- [Security and billing precautions](SECURITY.md)

The project's GitHub Actions run Python, PowerShell, Textual UI smoke tests and mocked Frida/Billing behavior. They cover run-mode selection, basic layout, button locking and safe Stop/Exit handling without launching purchases. **They do not test real Google Play transactions, or guarantee correct rendering on every Windows terminal size.**

## Credits & contributors

- **Original author — [gylive](https://github.com/gylive):** created the upstream [google-ultra](https://github.com/gylive/google-ultra) project and its Python, ADB, Frida, and Google Play Billing implementation.
- **Maintainer — [David Nguyen (@hoangsvit)](https://github.com/hoangsvit), [ePlus.DEV](https://eplus.dev):** imported and adapted the project for Windows/MuMu, added step-based commands and terminal menus, and maintained device compatibility, tests, and documentation.
- **Community:** see the [contributors history](https://github.com/hoangsvit/google-ai/graphs/contributors).

Contributions and bug reports are welcome; see [Contributing](CONTRIBUTING.md). Coding assistants should also follow the repository-wide [AI agent guidelines](AGENTS.md). The original author's **MIT copyright and license notice** are preserved in [Third-party notices](THIRD_PARTY_NOTICES.md).
