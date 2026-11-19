# Windows + MuMu pre-release smoke test (manual)

[Documentation home](README.md) · [Project overview](../README.md)

This is the reusable hardware validation checklist for **any ePlus AI Toolkit release**. GitHub Actions cannot perform it because CI does not have a rooted MuMu/Android instance or a real Google Play account. **Do not test billing Steps 2–5** for release verification.

## Before starting

- Windows 10/11 with PowerShell 5.1 or later, Python 3.10+, and the toolkit extracted into a separate folder.
- MuMuPlayer installed from [the official download](https://www.mumuplayer.com/download/), started with Android root and ADB available, and Google Play Store / Google One installed.
- Only a device and account that you control or have permission to administer.
- Have no payment checkout pending. Back up emulator data before Step 0: environment preparation can modify local ADB/Frida/emulator/proxy settings.
- Never include passwords, OTPs, full emails, purchase tokens, raw logs or payment details in screenshots/issues.

## Obtain the exact CI-tested source archive

1. Open [Windows release smoke tests](https://github.com/hoangsvit/google-ai/actions/workflows/windows-release-smoke.yml). Use **Run workflow** on `main` after the latest changes have been merged; wait for a successful run. A PR run may test a temporary merge commit, not the final commit on `main`.
2. From that successful run, download its **eplus-ai-toolkit-source-<commit SHA>** artifact. GitHub Actions packages the artifact as a download ZIP containing `eplus-ai-toolkit-source.zip` and `eplus-ai-toolkit-source.zip.sha256`.
3. Unzip the artifact, then confirm that the SHA-256 value of the inner source ZIP matches the value in the accompanying `.sha256` file:

    ```powershell
    (Get-FileHash .\eplus-ai-toolkit-source.zip -Algorithm SHA256).Hash
    Get-Content .\eplus-ai-toolkit-source.zip.sha256
    ```

4. Extract the **inner source ZIP** into a new directory for this release, then complete checks A–F below. Record the workflow run URL and its commit SHA with the manual test results.

The artifact contains **only tracked source files** from that workflow's checkout and is retained for **14 days**. It is *not* a Windows `.exe`, does *not* bundle MuMuPlayer or credentials, and is *not* a published GitHub Release. Do not claim that the workflow performed the real-device tests.

## Checks (no subscription checkout)

| Check | Action | Pass criteria |
| --- | --- | --- |
| A. Launcher help | In PowerShell, run the launcher help command below | Help text renders without Unicode error or attempting any checkout |
| B. Device detection | Run ADB listing below if ADB is available | Intended Android serial appears as device (not offline or unauthorized) |
| C. Dashboard | Run no-argument launcher | Textual dashboard shows Check Device & Offers, Live Status and expandable advanced controls, without starting a paid stage |
| D. Read-only offers | Press Check Device & Offers or run Step 1 from the CLI | Status shows the checked Android/account; result may be offers, empty or an explanatory failure—never a payment checkout |
| E. Details, Stop and Exit | Inspect technical details and use Stop on a safe diagnostic if applicable | No stale previous-account status, logs remain readable, and Exit works without launching another Step |
| F. Source ZIP | Extract the source ZIP from a successful **Windows release smoke tests** run on the exact release commit | Required scripts and assets are present; launcher help works from the extracted copy |

Launcher's help and read-only check:

    .\run-all.ps1 -Help
    adb devices
    .\run-all.ps1
    .\run-all.ps1 -Step 1 -Debug

Use Step 0 diagnostics *only if needed*, because they can install or repair ADB/Frida and modify Android settings:

    .\run-all.ps1 -Step 0

A missing offer or an ineligible account is **not by itself a toolkit failure**; capture a sanitized diagnostic summary. Do not turn a failure into a success by using Force or bypassing account matching. No paid checkout should be attempted by this procedure.

## Evidence to record

- Windows version, PowerShell version, Python version
- MuMuPlayer / Android version and ADB device state (mask unique serials if necessary)
- Date and Git commit or release tag tested
- Results A–F with pass / fail / not tested, plus sanitized error type if failing
- An explicit statement: **No live Google Play checkout was executed**

Only mark real-device validation complete if A–F have been run with no unexplained blockers. CI passing by itself is **not sufficient**.

## Publishing after checks pass

Once this checklist has actually passed for the **exact commit intended for release** and the reusable release workflow has been merged to main:

1. Confirm the **Static checks** workflow for the latest main commit is green.
2. Open [GitHub Actions](https://github.com/hoangsvit/google-ai/actions), select **Publish ePlus AI Toolkit (manual)** and choose **Run workflow** on **main**.
3. Enter the desired **version**, such as `1.0.1`, `1.1.0`, or `2.0.0-rc.1` (without a `v` prefix). Mark prereleases accordingly.
4. Enable **I completed docs/WINDOWS-SMOKE-TEST.md on real Windows + MuMu** only after verifying these checks for the release commit.
5. The workflow reruns Windows smoke tests, verifies Static checks on that exact `main` commit and refuses to overwrite existing tags/releases. If `docs/releases/v<VERSION>.md` exists, it uses those notes; otherwise, it generates GitHub release notes automatically. GitHub then provides the source code archives.

No repository code is released merely by opening or merging a documentation PR. Publishing is an explicit action, and it does not bundle MuMuPlayer or produce a Windows installer.

See [README](../README.md), [Security](../SECURITY.md), and the version-specific files in [release notes](releases/v1.0.1.md) (v1.0.1 is an example, not a workflow restriction).
