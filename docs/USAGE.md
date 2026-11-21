# Using the Textual dashboard and PowerShell CLI

[Documentation home](README.md) · [Repository README](../README.md) · [Safety](SAFETY.md)

## Use the dashboard (recommended)

The dashboard follows a checkout-style guided path: start with **Check Device & Offers** (Step 1). A fresh successful listing, an identified Play account and the matching initial offer with a zero-priced first phase reveal **Continue: 12-month stage →**. This only opens the separate Step 2 approval; the engine rechecks account, offer and payment terms before checkout. It is not proof of eligibility, free months or activation. After a reviewable checkout attempt, verify the actual result in Google Play before **Verified in Google Play → Next**, or choose **Finish here**. Step 5 is optional. No stage starts automatically.

**Advanced: Run by step** is a full button beside the guided action, stacked below it in narrower terminals. It opens a separate configuration view with its own visible Run button; **← Back to guided flow** returns to the wizard. **From selected step** only offers Steps 2–5. **All: Steps 2–5** shows the planned route from Step 2 and hides the step selector. The **R** shortcut works only in this view. Offer Explorer is available through **View offers** after a successful listing. Help opens separately and preserves the current result.

[Standard dashboard preview](../assets/images/dashboard.png) · [Compact 90×20 preview](../assets/images/dashboard-compact.png). Both previews show a simulated successful inspection; no billing operation was run.

### Start with Check Device & Offers

1. Click **Check Device & Offers** on the welcome screen. It invokes **Step 1 — Available offers**, intended to *list* offers rather than initiate checkout.
2. Watch **Live Status** for the stage, elapsed time, current activity and result. **Show technical details** reveals execution output. A warning after 30 seconds without new output indicates inactivity, **not proof of a hang**.
3. Check the account and offer information on the Android screen. A listed offer is **not** a guarantee of eligibility or a successful subscription.
4. If **Continue: 12-month stage →** appears, review its separate approval before starting Step 2. After each checkout attempt, verify Google Play before Next, or choose **Finish here**.
5. Open **Advanced: Run by step** only to deliberately configure a separate step or sequence.

**Important distinction:** Step 1 does not initiate a purchase, but underlying environment preflight can still install or repair ADB/Frida and change emulator/network settings. **Step 0 — Environment** is a setup/diagnostics stage, not a purchase-free guarantee of zero local side effects.

The top progress strip shows the guided stages; their durations are labels, not verified entitlements. Android Device / Google Account cards update from observed output; account identifiers are masked. Original-author and maintainer credits link to their GitHub profiles in supported terminals.

### Application updates

The dashboard checks for a newer revision of the official `main` branch in the background at startup. **Check for updates** retries the check; when a newer revision is available, **Update & Restart** installs the displayed revision and reopens the native launcher at an idle dashboard. Versions are shown as short Git commit IDs. No stage or checkout is resumed.

Automatic updates require an official Git clone on `main`, no local changes or unfinished Git operations, and a fast-forward history. Development branches, forks and source ZIPs must be updated manually; keep ZIP installations in separate folders. Network/Git failures appear in the update status and can be retried. Updating is locked during a stage, connection diagnosis, payment approval or guided Google Play review. While installation runs, new stages and Exit are locked; Help and technical details remain available. The updater never resets or stashes local files.

### Advanced run modes

| Mode | Behavior |
| --- | --- |
| **One step only** | Runs only the selected Step **0–5**. |
| **From selected step** | Begins a guided checkout sequence at the chosen Step **2–5**, without replaying earlier checkout steps. |
| **All: Steps 2–5** | Begins the guided checkout sequence at **Step 2**. Step **5** is optional. |

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

- **Stop check (Steps 0–1):** requests cancellation of the local process tree. Cancellation can fail if a child process is stuck; inspect technical details.
- **Stop after this step (Steps 2–5):** prevents further stages, but **does not force-kill a checkout in progress**. The remote payment outcome could otherwise become unknown.
- **Exit toolkit / Q:** exits immediately while idle; during Steps 0–1 it requests cancellation and exits afterward, and during Steps 2–5 it queues exit after the current stage.
- **D** toggles technical details; **R** uses the selected run mode only while the Advanced view is open. A **Next** button is available only for a reviewable checkout outcome in a guided sequence.

Neither Stop nor closing the terminal reverses an existing Google Play transaction. Always verify the real transaction and subscription status directly.

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

The CLI performs its environment/offer checks and then proceeds through the original subscription stages, requesting numbered approvals between potentially billable operations (**1 = Continue, 2 = End run, 0 = Stop**). This differs from **All: Steps 2–5** on the TUI, which begins its guided sequence at Step 2. Starting the CLI sequence at Step 3 must only follow independent verification of an existing plan; it does not prove any prior extension succeeded.

Optional parameters:

```powershell
.\run-all.ps1 -Step 1 -Serial emulator-5554
.\run-all.ps1 -AllStages -Email "account@gmail.com"
```

Only use a `-Serial` observed through ADB. `-Email` constrains the account expected by the checks. `-Force` exists for compatibility but bypasses account-matching protections; **avoid using it**. It does not override Google Play payment restrictions or eligibility.
