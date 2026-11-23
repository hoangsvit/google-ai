# Using the Textual dashboard and PowerShell CLI

[Documentation home](README.md) · [Repository README](../README.md) · [Safety](SAFETY.md)

## Use the dashboard (recommended)

### Start with Check Device & Offers

While idle, the dashboard checks existing ADB connections roughly every five seconds. If Android is not connected, it shows a dismissible notice and checks again; connecting does not by itself unlock paid steps. Monitoring pauses during stages and other dialogs. It only reads `adb devices` (which can start the local ADB server); it does not scan ports, connect devices, or install ADB in the background.

1. Click **Check Device & Offers** on the welcome screen. It invokes **Step 1 — Available offers**, intended to *list* offers rather than initiate checkout.
2. Watch the top line of **Live Status** for the latest activity. The stage, elapsed time and result appear below it. **Show technical details** reveals execution output. A warning after 30 seconds without new output indicates inactivity, **not proof of a hang**.
3. Check the account and offer information on the Android screen. A listed offer is **not** a guarantee of eligibility or a successful subscription.
4. If the verified account has a listed 12-month offer with a zero-priced first phase, choose **Continue to Step 2** in the completion dialog or on the main screen. A separate approval explains the payment risk before the step starts. If the offer is absent, review the listed offers instead.
5. Expand **Choose another step** only when you deliberately need to select a different stage.

Steps 2–5 stay locked until a fresh offer check returns offers and verifies the Play account. A new check or failed paid stage locks them again. The engine rechecks the device, account and chosen offer before a paid action; the earlier check does not guarantee eligibility or connectivity.

**Important distinction:** Step 1 does not initiate a purchase, but underlying environment preflight can still install or repair ADB/Frida and change emulator/network settings. **Step 0 — Environment** is a setup/diagnostics stage, not a purchase-free guarantee of zero local side effects.

On Windows, running the check locates ADB or attempts to download official Android SDK Platform-Tools when missing. Installation can fail because of connectivity, permissions or security software. On macOS, install Platform-Tools through the platform's setup instructions; the Windows installer is not used.

The sidebar lists the six stages. Android Device / Google Account cards update from observed output; account identifiers are masked. Original-author and maintainer credits link to their GitHub profiles in supported terminals.

**Choose account** appears next to the Account card from startup. It reads the signed-in Android account candidates when clicked. During a stage it is disabled. Choose the matching profile in Google Play and run **Check Device & Offers** to verify the selection.

**Recent history** shows the last six saved events for the selected or freshly verified account, newest first. It records stage starts, results and the user's **Verified in Google Play → Next** action. Private history stays under `logs/stage-history/`, with hashed account filenames. Opening the toolkit requires a fresh device and offer check before paid stages.
Startup displays the most recently saved history even before account selection. The sidebar uses **↺** for previously attempted steps. Select an account to view its own history. A fresh current-session check is still required. Attempts made before account detection are saved as account unverified.

Before automatically tapping Subscribe, the toolkit requires the checkout screen to show exactly the expected email address. If the checkout account is missing, different or ambiguous, inspect the account in the Google Play checkout screen and repeat the device and offer check.
For devices with multiple signed-in accounts, the Play Store account button can identify the active profile when its accessibility label includes an explicit email. An expanded account list with no active-profile indicator requires manual selection. A checkout-account error refers to the billing screen, and includes instructions to check Play Store and Google One before running Step 1 again.

After **Check Device & Offers** reads the Android device, the **Device** card shows the Android version, SDK level, CPU ABI and ADB serial when available. Hover over the card for the full details if the terminal clips the line.

### Additional run options

By default, only the selected step runs. To choose a guided sequence, expand **Choose another step** and select **More run options…** at the bottom of the step dropdown. There is no third button in the default picker.

| Mode | Behavior |
| --- | --- |
| **Stop after this step** | Runs only the selected Step **0–5**. |
| **Offer the next step** | Begins a guided checkout sequence at the chosen Step **2–5**, without replaying earlier checkout steps. |
| **Start at Step 2** | Begins the guided checkout sequence at **Step 2**. Step **5** is optional. |

All checkout stages on the dashboard require **explicit approval per stage**. After a stage reports that it attempted to submit checkout, check the real Google Play subscription and renewal date. The tool cannot independently confirm a successful activation or extension. Only press **Verified in Google Play → Next** if the change has actually been verified. The next stage still requires separate approval. Failed or ambiguous results do not authorize advancing.

| Step | Purpose | Checkout risk |
| --- | --- | --- |
| **0 — Environment** | Diagnose/prepare Android, ADB and Frida | No subscription checkout; local/emulator changes possible |
| **1 — Available offers** | Query offers for the active Google Play account | No subscription checkout; preflight changes possible |
| **2 — Pro 12 months** | Original 12-month offer | **May start real checkout** |
| **3 — Pro +6 months** | Original subscription update | **May start real checkout** |
| **4 — Pro +6 months (second)** | Another original update | **May start real checkout** |
| **5 — Optional +6 months** | Optional original update | **May start real checkout** |

If Google Play already shows an active subscription, do **not** repeat Step 2. The names and durations of offers are historical labels, not guaranteed entitlements or extensions.

### Controls, Stop and Exit

While a stage is running, **Check Device & Offers**, Run, Run mode and Step selection are locked so another stage cannot be started. Help and technical details remain accessible.
During Step 1, the **Check Device & Offers** button displays the elapsed time in seconds.
If Steps 2–5 are selected without a fresh verified check, the step panel shows a green **Check Device & Offers — Step 1** action and explains the prerequisite. Click it to refresh the current device, account and offers.
During Steps 2–5, the same button shows **Running Step N…** and elapsed seconds until the step finishes.
The **Run this step** button in step selection also shows the running step and elapsed seconds.
**Reload toolkit** restarts the dashboard with the current local code. It is available while idle and starts a new session requiring a fresh Step 1 check.
The engine restarts Google One after the device and account checks, before querying offers. **Live Status** reports when this restart begins. A failed stop command ends the attempt.
When the Windows offer check completes its Environment check, Step 0 receives a checkmark while Step 1 continues running.
The action panel fits its controls, and **Live Status** fills the remaining height. Expanding the step controls keeps them in a scrollable panel.

- **Stop check (Steps 0–1):** requests cancellation of the local process tree. Cancellation can fail if a child process is stuck; inspect technical details.
- **Stop after this step (Steps 2–5):** prevents further stages, but **does not force-kill a checkout in progress**. The remote payment outcome could otherwise become unknown.
- **Exit toolkit / Q:** exits immediately while idle; during Steps 0–1 it requests cancellation and exits afterward, and during Steps 2–5 it queues exit after the current stage.
- **D** toggles technical details. Opening the log jumps to the latest line and follows new output. **R** uses the selected advanced run mode. A **Next** button is available only for a reviewable checkout outcome in a guided sequence.

Neither Stop nor closing the terminal reverses an existing Google Play transaction. Always verify the real transaction and subscription status directly.

Linux users can open the advanced controls with `sh run-linux.sh --step N` for Steps 0–5 or `sh run-linux.sh --sequence` to start with Step 2 selected in guided mode. These commands open the dashboard without running a stage. [Linux setup and command reference](LINUX.md).

## PowerShell CLI (advanced)

The dashboard and the CLI reuse the same PowerShell/Python engine. Explicit command arguments bypass the TUI.

### Safe offer check and diagnostics

```powershell
.\run-all.ps1 -Step 1           # List offers; no checkout
.\run-all.ps1 -Step 1 -Debug    # Same check with technical diagnostics
.\run-all.ps1 -Step 0           # Environment diagnostics and setup
.\run-all.ps1 -Cli              # Legacy CLI, default Step 1
```

Local technical logs are stored under `logs/`, while fresh offer and stage reports are under `ultra0-report/`. **Do not share raw logs or full reports** without removing account identifiers and sensitive billing/purchase tokens.

The standalone `setup_env.py` and [`tools/windows/setup-environment.bat`](../tools/windows/setup-environment.bat) remain troubleshooting/repair tools, not mandatory steps before launching the dashboard.

### Checkout commands — may charge money

```powershell
.\run-all.ps1 -Step 2
.\run-all.ps1 -Step 3
.\run-all.ps1 -Step 4
.\run-all.ps1 -Step 5
```

**Unlike the TUI, an explicitly selected single checkout stage does not require a second typed PowerShell approval.** The original Python engine may automatically press Subscribe after checking the Google Play screen. Do not execute these commands unless you intend to initiate a potentially billable operation and have reviewed its terms.

To use the original **CLI** guided sequence:

```powershell
.\run-all.ps1 -AllStages
.\run-all.ps1 -AllStages -StartStep 3
```

The CLI performs its environment/offer checks and then proceeds through the original subscription stages, requesting numbered approvals between potentially billable operations (**1 = Continue, 2 = End run, 0 = Stop**). This differs from **Start at Step 2** on the TUI, which begins its guided sequence at Step 2. Starting the CLI sequence at Step 3 must only follow independent verification of an existing plan; it does not prove any prior extension succeeded.

Optional parameters:

```powershell
.\run-all.ps1 -Step 1 -Serial emulator-5554
.\run-all.ps1 -AllStages -Email "account@gmail.com"
```

Only use a `-Serial` observed through ADB. `-Email` constrains the account expected by the checks. `-Force` exists for compatibility but bypasses account-matching protections; **avoid using it**. It does not override Google Play payment restrictions or eligibility.
