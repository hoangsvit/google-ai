# ePlus AI Toolkit

**Languages:** **English** · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md)

A terminal toolkit for **Windows and macOS** to inspect Google AI Pro offers through Android, ADB, Frida and Google Play. The shared Textual dashboard uses a PowerShell/Python launcher on Windows and a native Python adapter on macOS.

![ePlus AI Toolkit — full dashboard (110×35, Steps 0–5)](images/terminal-ui-overview.png)

> [!CAUTION]
> **Unofficial project. Potential billing charges.** Steps **2–5** can open a real Google Play checkout and may automatically tap **Subscribe**. An offer appearing in a list, a displayed first-phase price of zero, or a message indicating that the Subscribe action was attempted does **not** establish eligibility, an active subscription, a free subscription, or a changed renewal date. Verify the exact account, today's charge, future pricing and renewal date directly in Google Play before any checkout.

> [!NOTE]
> **At least US$3 available for three separate US$1 transactions—not one US$3 charge.** In the currently reported **24-month** sequence, Step 2 (initial 12 months), Step 3 (first +6 months) and Step 4 (second +6 months) each involve a **US$1 card-verification/payment event**: **3 × US$1 = US$3** across three transactions. An event may be a temporary authorization hold rather than a settled charge; the actual amount can differ by bank, account or Google Play. US$3 is the minimum balance for this reported example, **not a universal Google fee or a guarantee that US$3 will always suffice**. Pending holds may reduce the available balance; according to Google, authorizations are not purchases and typically clear in **1–14 business days**, depending on the bank. Verify transaction status and subscription/renewal dates directly in Google Play after each stage. Step 5 is optional and is **not** part of this three-transaction example. [Google Play: Fees, charges & authorizations](https://support.google.com/googleplay/answer/6224192?hl=en).

## Disclaimer

**ePlus AI Toolkit is an independent, unofficial project** and is not affiliated with, endorsed by or supported by Google, Google Play, Google One, NetEase or MuMuPlayer.

The software is provided **as is**, without guarantees of Google AI Pro eligibility, free or extended subscriptions, payment outcomes, account safety or emulator compatibility. **Steps 2–5 can initiate real charges**, and setup may alter Android, Frida or network settings. Use it only with authorized accounts and devices, comply with applicable terms and laws, and verify every payment and renewal directly in Google Play. Stop/Exit does not undo a submitted checkout.

Read the **[full disclaimer](DISCLAIMER.md)** and [security precautions](SECURITY.md) before use. These notices do not remove any liability that cannot legally be excluded.

## Install and prepare

**Choose the instructions for your operating system.** Windows runs PowerShell; macOS runs Terminal with a POSIX shell (zsh/bash). **PowerShell is not required or used on macOS.**

| Software / configuration | Windows | macOS |
| --- | --- | --- |
| Terminal and shell | **PowerShell 5.1+** | Built-in **Terminal**, using **zsh** or **bash**; **no PowerShell** |
| Python | **3.10+** (command: `python`) | **3.10+** (command: `python3`); launcher creates a local `.venv` |
| Git | Install Git for Windows | Install Git (Xcode Command Line Tools or Homebrew are options) |
| Android connection | Rooted, ADB-enabled Android instance; **MuMuPlayer for Windows** is supported by the project workflow | Rooted Android device or compatible emulator; **MuMuPlayer Pro for Mac** is an Apple Silicon option, not an Intel Mac solution |
| Android apps | Google Play Store and Google One, signed in to the intended account | Same; must be available on the chosen Android device/emulator |
| ADB / Platform-Tools | Launcher can locate/download ADB when needed | Install separately, e.g. `brew install android-platform-tools`; verify with `adb devices` |
| Frida | **16.5.9**, prepared by the Windows setup helper as needed | **16.5.9**, installed into the local `.venv` by the Mac launcher; Android-side compatibility must be checked |
| Start command | `.\run-all.ps1` | `sh run-macos.sh` (or `ePlus-AI-Toolkit.command`) |

Both platforms need an authorized, correctly configured Android environment. The macOS implementation covers Steps 0–5 in code, but real Mac/MuMu checkout compatibility has **not** been verified. See the dedicated [Windows guide](docs/INSTALLATION.md) and [macOS guide](docs/MACOS-PREVIEW.md).

### Windows requirements

- **Windows** with PowerShell **5.1+** and Python **3.10+**.
- **MuMuPlayer installed separately**, started with an Android instance that permits root and ADB access.
- **Google Play Store** and **Google One** installed and signed into the intended Google account inside Android.
- A connection to Android through ADB. The toolkit can locate or download **Android SDK Platform-Tools** when ADB is missing; it does **not** install the Android emulator.
- A compatible **Frida 16.5.9** host/device environment. The setup helper can prepare Frida, but compatibility depends on the emulator and Android version.

### Step 1 — Install MuMuPlayer

**MuMuPlayer is neither included in this repository nor automatically downloaded by the toolkit.**

Download it from the **[official MuMuPlayer website (NetEase)](https://www.mumuplayer.com/download/)**, choose the Windows edition, and install it yourself. Avoid third-party download mirrors.

Start MuMuPlayer, enable root and ADB debugging for the Android instance, and ensure Google Play Store and Google One are available. Sign into the Google account you intend to check.

For illustrated setup instructions, use the **[Install guide on this project's GitHub Wiki](https://github.com/hoangsvit/google-ai/wiki/Install)**.

### Step 2 — Get the toolkit

Open **PowerShell** in the folder where you want to install the toolkit:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

If you already cloned the repository, update it before starting:

```powershell
git pull --ff-only
.\run-all.ps1
```

The no-argument command opens the Textual dashboard, installing its pinned dependency on first launch if needed. When you run a check, the environment helper can also install or locate ADB and the pinned Frida version. **You generally do not need to execute `setup_env.py` manually first.** Environment preparation may install tools or adjust Android/Frida/emulator settings.

If the terminal shows an ADB error, confirm that MuMu is running and Android debugging is enabled. Where ADB is on your PATH, you can verify the connection with:

```powershell
adb devices
```

The device must show as `device`, not `offline` or `unauthorized`. If ADB is not on PATH, let the toolkit locate/install Platform-Tools or follow the [detailed troubleshooting guide](docs/DETAILED-GUIDE.md).

### Alternative: use a published release if the latest source fails

If you encounter errors when running the latest repository version, you can try a **previously published release** from [GitHub Releases](https://github.com/hoangsvit/google-ai/releases). Open a release, read its notes, and download the available Windows package **if one is attached**. If the release only provides GitHub's automatic **Source code (zip)** archive, download and extract that ZIP, open PowerShell in the extracted folder, and run:

```powershell
.\run-all.ps1
```

A **source ZIP is not a prebuilt `.exe` or installer**. Keep the release in a **separate folder** from your current clone so you can compare versions and roll back without overwriting files. Release builds may lack newer bug fixes, and they still require Windows, Python, MuMuPlayer, ADB/Frida and the same billing precautions. If the error persists, check [Troubleshooting](#troubleshooting-and-results) or [report an issue](https://github.com/hoangsvit/google-ai/issues).

## macOS — Install and run

**macOS uses Terminal (zsh/bash), not PowerShell.** Do not run `.ps1` / `.bat` launchers or the Windows-only `setup_env.py` on a Mac.

The native [macOS implementation](docs/MACOS-PREVIEW.md) supports **Steps 0–5**, including guided subscription stages, without using the Windows PowerShell setup helper. It reuses the existing Python/Frida Android engine and shared Textual dashboard. **Steps 2–5 can create real Google Play charges**, so each requires a separate confirmation, an identifiable current Play account and an available matching offer. The adapter never uses `--force`.

**Requirements:** macOS, **Git**, Python 3.10+, Android SDK Platform-Tools/ADB (Homebrew: `brew install android-platform-tools`), and a rooted Android device/emulator with Google Play Store and Google One. **MuMuPlayer Pro for Mac supports Apple Silicon**; Intel Macs require another compatible rooted Android setup.

Open **Terminal** and install from the default repository branch:

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
adb devices
sh run-macos.sh
```

The launcher prepares Textual and Frida 16.5.9 in a local `.venv`. Optional commands: `sh run-macos.sh --check` (Android/Frida check; may alter settings), `sh run-macos.sh --list` (offers only), and `sh run-macos.sh --step 2` (preselect Step 2 in the TUI; **does not automatically pay**). The `ePlus-AI-Toolkit.command` file is a Finder-friendly Terminal launcher, **not a signed or notarized .app**.

The macOS adapter exposes **Steps 0–5**. **Steps 2–5 may initiate real Google Play charges** and require explicit confirmation. No real Mac/MuMu checkout or subscription activation has been validated. [Full macOS guide](docs/MACOS-PREVIEW.md).


## Linux — Install and run

On Ubuntu x86_64, install Git, Python 3.10+ with `venv` and `pip`, and Android SDK Platform-Tools. Put `adb` on `PATH` or set `ADB_PATH` to its executable. Connect a rooted Android phone with Google Play Store and Google One over USB. Enable USB debugging, unlock the phone, and approve the authorization prompt. Check that ADB reports one device with status `device`.

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
git switch feature
adb devices
sh run-linux.sh
```

Use the `feature` branch while Linux support is being validated. It contains `run-linux.sh`. The launcher opens the dashboard and installs the pinned Textual and Frida 16.5.9 dependencies into a local `.venv`. If Ubuntu cannot create that environment, install `python3-venv` or the venv package for your Python version.

- `sh run-linux.sh --check` runs Step 0, which can modify Android, Frida or network settings.
- `sh run-linux.sh --list` runs Step 1 to list offers without requesting checkout. It can also prepare the Android environment.
- `sh run-linux.sh --step 3` opens Advanced controls with Step 3 selected. `sh run-linux.sh --sequence` opens guided controls starting at Step 2. Neither starts a stage on launch.

**Android 16 and later:** The Linux launcher stops before device setup because pinned Frida 16.5.9 predates Android 16 support. **Diagnose Android connection** remains available for USB checks.

**Steps 2–5 can incur real Google Play charges.** Each requires separate approval, a verified current Play account and a fresh exact-match offer with a zero-priced first phase. Guided continuation requires verifying the subscription and renewal date in Google Play. Linux checkout coverage uses mocks, and an end-to-end device check is pending. [Linux setup, USB troubleshooting and verification](docs/LINUX.md).


## Use the dashboard (recommended)

### Start with Check Device & Offers

1. Click **Check Device & Offers** on the welcome screen. It invokes **Step 1 — Available offers**, intended to *list* offers rather than initiate checkout.
2. Watch **Live Status** for the stage, elapsed time, current activity and result. **Show technical details** reveals execution output. A warning after 30 seconds without new output indicates inactivity, **not proof of a hang**.
3. Check the account and offer information on the Android screen. A listed offer is **not** a guarantee of eligibility or a successful subscription.
4. Expand **Choose another step** only when you deliberately need to select a different stage.

While the dashboard is idle, it checks existing ADB connections about every five seconds. If ADB or Android is unavailable, a popup explains what to check. It checks again automatically and updates the device status; reconnecting alone does not unlock paid steps. Monitoring pauses during a running step and other dialogs. It does not install or connect devices in the background, though `adb devices` may start the local ADB server.

On Windows, **Check Device & Offers** looks for ADB and, if necessary, attempts to download official Android SDK Platform-Tools. Downloads or installation can fail; check **Show technical details** if they do. On macOS, install Platform-Tools following the Mac instructions. Install and start MuMu separately, enable root and ADB debugging, and sign in to Google Play and Google One.

Steps 2–5 stay locked until a fresh Step 1 check returns offers and verifies the Play account. If the 12-month offer `12months-eft` has a zero-priced first phase, the completion popup and main screen show **Continue to Step 2**. Otherwise, review the listed offers. The button opens a separate approval; it does not prove eligibility or final cost. After checkout, verify the actual subscription, renewal date and charges in Google Play before choosing **Verified in Google Play → Next**. Each later stage requires its own approval. A new check, failed paid stage or device change can lock the paid steps again.

**Important distinction:** Step 1 does not initiate a purchase, but underlying environment preflight can still install or repair ADB/Frida and change emulator/network settings. **Step 0 — Environment** is a setup/diagnostics stage, not a purchase-free guarantee of zero local side effects.

The sidebar lists the six stages. Android Device / Google Account cards update from observed output; account identifiers are masked. Original-author and maintainer credits link to their GitHub profiles in supported terminals.

The Device card shows the Android release, SDK, CPU ABI and ADB transport when read; hover for full details. **Choose account**, beside the Account card, lists signed-in Android account candidates. Select the intended profile in both Play Store and Google One, then repeat Step 1. When Play Store exposes an explicit active-profile email, the toolkit can distinguish it from other signed-in accounts.

The action panel fits its controls and **Live Status** uses the remaining height, with the latest activity first. **Show technical details** opens a log that follows new output. Both the main button and **Run this step** show the running step and elapsed seconds. On Windows, Step 0 receives a checkmark once its environment check completes within the offer-check flow. If a paid step lacks a fresh verified check, the green **Check Device & Offers — Step 1** button appears in step selection.

**Recent history** saves stage starts, results and the user's **Verified in Google Play → Next** action locally under `logs/stage-history/`. Startup restores the latest saved history; selecting an account loads its own history. **↺** marks a previously attempted step. History alone cannot verify a subscription or unlock checkout. A fresh Step 1 check is required after reopening the toolkit or changing accounts. Runs before history recording was added are unavailable.

**Retry connection** in the disconnected-device popup shows **Retrying…** and elapsed seconds. On Windows it tries the existing local emulator connection routine; Windows stages also attempt reconnection when no ADB device is online. **Got it** dismisses the popup. During read-only checks, a failed app startup gets one restart attempt. If recovery fails, close and reopen MuMu, wait for Android to boot and repeat Step 1. The engine restarts Google One before querying offers; Play Store stays running when already available. **Reload toolkit** restarts the idle dashboard with local code and begins a new session.

Before automatically tapping **Subscribe**, checkout must show exactly the expected email, today's zero total and the expected trial duration, with the requested offer already matched. Missing or different checkout accounts stop the automatic tap and require manual review. The submitted checkout still needs independent subscription, renewal-date and charge verification in Google Play. Each paid stage requires its own approval. The three-card-event reminder appears in the payment approvals.

### Additional run options

By default, only the selected step runs. In **Choose another step**, select **More run options…** at the bottom of the step dropdown to show guided-sequence modes.

| Mode | Behavior |
| --- | --- |
| **Stop after this step** | Runs only the selected Step **0–5**. |
| **Offer the next step** | Begins a guided checkout sequence at the chosen Step **2–5**, without replaying earlier checkout steps. |
| **Start at Step 2** | Begins the guided checkout sequence at **Step 2**. Step **5** is optional. |

**Reported 24-month example (subject to Google Play confirmation):**

| Step | Duration if applied | Separate card event |
| --- | --- | --- |
| **2 — Pro 12 months** | Initial **12 months** | **US$1** (first transaction) |
| **3 — Pro +6 months** | **18 months total** | **US$1** (second transaction) |
| **4 — Pro +6 months (second)** | **24 months total** | **US$1** (third transaction) |
| **Total through Step 4** | **24 months if verified** | **3 × US$1 = US$3**, not one US$3 charge |

**Step 5 is optional and excluded from this three-transaction example.** No listed duration or authorization proves that an extension succeeded; check the subscription and renewal date in Google Play after each checkout.

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
- **D** toggles technical details; **R** uses the selected advanced run mode. A **Next** button is available only for a reviewable checkout outcome in a guided sequence.

Neither Stop nor closing the terminal reverses an existing Google Play transaction. Always verify the real transaction and subscription status directly.

## PowerShell CLI (advanced)

**Windows only:** These PowerShell commands apply to `run-all.ps1`, not macOS. On a Mac, use the POSIX `run-macos.sh` launcher and [Mac-specific commands](docs/MACOS-PREVIEW.md). The Windows dashboard and CLI reuse the same PowerShell/Python engine. Explicit command arguments bypass the TUI.

### Safe offer check and diagnostics

```powershell
.\run-all.ps1 -Step 1           # List offers; no checkout
.\run-all.ps1 -Step 1 -Debug    # Same check with technical diagnostics
.\run-all.ps1 -Step 0           # Environment diagnostics and setup
.\run-all.ps1 -Cli              # Legacy CLI, default Step 1
```

Local technical logs are stored under `logs/`, while fresh offer and stage reports are under `ultra0-report/`. **Do not share raw logs or full reports** without removing account identifiers and sensitive billing/purchase tokens.

The standalone `setup_env.py` and [`tools/windows/setup-environment.bat`](tools/windows/setup-environment.bat) remain troubleshooting/repair tools, not mandatory steps before launching the dashboard.

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

## Troubleshooting and results

| Problem or result | What to check |
| --- | --- |
| **MuMu / ADB not detected** | Install/start MuMu separately, enable root/ADB, verify the correct connected Android instance and authorization. |
| **Frida setup failure** | Review technical details; Frida **16.5.9** must be compatible with the host and device. |
| **No offers / `offer_query_failed`** | Open Google One and Google Play on the target Android instance and run Step 1 again. |
| **Account not verified / wrong account** | Inspect the active Google Play profile; do not bypass verification. |
| **Checkout submitted; check Google Play** | The tool attempted to submit checkout; it has **not** verified a successful subscription or extension. |
| **`already_subscribed` / `ineligible`** | Stop; do not retry other checkout stages based on unverified extension claims. |
| **Payment/security error (e.g. OR-REH-04)** | Follow Google Account/Payments security instructions. Do not repeatedly retry. |
| **Unicode output error** | Update the repository; the maintained Windows launcher configures Python UTF-8 output for piped status symbols. |

Verify subscription, payment amount, currency and renewal terms under **[Google Play Subscriptions](https://play.google.com/store/account/subscriptions)**. For developer-facing status codes and advanced platform/Frida problems, see [Detailed setup and troubleshooting](docs/DETAILED-GUIDE.md).

**Platform support:** Windows and macOS use separate launchers. The macOS port has not been validated with a real Mac/MuMu or Google Play transaction; see [macOS guide](docs/MACOS-PREVIEW.md).

## Community support and related projects

If you need help installing or using ePlus AI Toolkit, see the [ePlus Telegram support/discussion post](https://t.me/eplus_news/29) to get in touch and exchange troubleshooting tips with the community. You can also [open a GitHub Issue](https://github.com/hoangsvit/google-ai/issues) for reproducible bugs. **Never post passwords, 2FA codes, purchase/offer tokens, full unredacted logs, or payment-card details.** Community support is not an official Google support channel.

**Can't access the Google AI Pro offer?** You may also explore [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub) ([browse or share Muse invite codes](https://muse.eplus.dev/)), another ePlus.DEV community project. Muse invite codes are for a **separate service**, are not a substitute for Google AI Pro subscriptions, and do **not** unlock or guarantee Google AI Pro access. Muse code availability and eligibility may vary.

## Repository structure

Active launchers and the Python modules they invoke stay at the repository root. **Use `run-all.ps1` on Windows or `run-macos.sh` on macOS.**

| Location | Purpose |
| --- | --- |
| `run-all.ps1` | Windows entrypoint (Textual dashboard and guided CLI) |
| `run-macos.sh`, `ePlus-AI-Toolkit.command`, `macos_runner.py` | macOS launcher and adapter (Steps 0–5; real-device checkout not validated) |
| `tui.py`, `tui_core.py`, `ultra0.py`, `setup_env.py`, `device_selector.py`, `query_sku.py` | Active Python runtime and supporting tools; kept in place for compatibility |
| [`tools/windows/`](tools/windows/README.md) | Optional manual Windows setup shortcut; not required for normal launch |
| [`legacy/windows/`](legacy/windows/README.md) | Historical batch shortcuts; some bypass account checks with `--force` and may initiate a **real charge**. Use the maintained launcher instead |
| `scripts/`, `assets/` | Runtime helpers and bundled Android/Frida assets |
| `tests/`, `.github/workflows/`, `docs/` | Offline regression tests, CI and reference documentation |

## Documentation and contributing

- [Documentation hub](docs/README.md)
- [Repository structure and maintenance](docs/PROJECT.md)
- [Dashboard usage & PowerShell CLI](docs/USAGE.md)
- [Billing safety](docs/SAFETY.md)

- [Install guide — GitHub Wiki](https://github.com/hoangsvit/google-ai/wiki/Install)
- [Detailed setup and troubleshooting](docs/DETAILED-GUIDE.md)
- [Original author's stage and batch-file reference](docs/ORIGINAL-STEPS.md)
- [Historical author notes](docs/AUTHOR-NOTES.md)
- [Full disclaimer](DISCLAIMER.md)
- [Security and billing precautions](SECURITY.md)
- [Contributing](CONTRIBUTING.md) · [AI agent guidelines](AGENTS.md) · [Third-party notices](THIRD_PARTY_NOTICES.md)

GitHub Actions checks Python, PowerShell, Textual and mocked Frida/Billing behavior **without initiating real Google Play transactions**. Passing CI does not prove hardware compatibility or subscription eligibility.

## Credits

- **Original author:** [@gylive](https://github.com/gylive) — upstream [google-ultra](https://github.com/gylive/google-ultra), including the original Python/ADB/Frida/Google Play approach.
- **Maintainer:** [David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev) — Windows/MuMu adaptation, terminal UI, compatibility fixes, tests and documentation.
- [Community contributors](https://github.com/hoangsvit/google-ai/graphs/contributors)

The upstream MIT notice is retained in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md); that notice does not independently license unrelated new contributions.
