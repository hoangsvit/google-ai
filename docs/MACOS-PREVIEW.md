# ePlus AI Toolkit for macOS — full-stage development build

[Documentation home](README.md) · [Project overview](../README.md)

This macOS port exposes the full 6-stage Textual interface and uses the same
Android/Frida engine as Windows. It is **not** a macOS production release:
no real Mac/MuMu/Google Play Billing transaction has been tested. Passing CI
only proves host compatibility and mocked account/offer/confirmation logic.

## What works in the code

- Step 0: Android/ADB/root/Frida environment preflight.
- Step 1: read available offer metadata without opening subscription checkout.
- Step 2: selected Pro offer, with a verified Google Play account, exact offer
  match, first-phase price check and an explicit confirmation.
- Steps 3–4: existing-subscription update stages with account/offer checks and
  additional confirmation of the already-active plan.
- Step 5: optional subscription stage with separate approval.
- Guided sequence and Run All: each subsequent stage requires the user to
  verify Google Play subscription details, renewal date and future price.

**Warning:** Stages 2–5 can initiate real Google Play charges or automatically
press Subscribe via upstream Android scripts. A zero-priced introductory phase
does *not* guarantee eligibility or free renewal. Do not use this against an
account or Android device without authorization. The script has no --force
bypass for Mac.

## Requirements

- macOS, Python 3.10+ and network access to install packages.
- Android SDK Platform-Tools (ADB) on PATH. Homebrew option:
  brew install android-platform-tools
- A rooted Android device or compatible Android emulator with Google One and
  Google Play Store. MuMuPlayer Pro for Mac is an option on Apple Silicon,
  not Intel. Root and Frida compatibility depend on the actual Android build.
- The launcher installs pinned Textual and Frida 16.5.9 into the local .venv;
  it does not install Android or configure a Mac emulator automatically.

## Install from GitHub

Install Python 3.10+ and Android Platform-Tools first, and connect an authorized
rooted Android device. Then clone the project in Terminal:

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
sh run-macos.sh
```

**Branch availability:** If `run-macos.sh` is not found, your cloned version
predates the Mac port. Switch to the development branch with `git switch dev`
and run `sh run-macos.sh` again. **Once this port is promoted to `main`,
the normal clone above works without switching branches.** For an older
GitHub Release, download a version that actually contains the Mac launcher.

## Start from the downloaded Mac source bundle

The CI workflow produces a macOS ZIP source bundle after its tests succeed.
That archive includes the launcher, Python source, pinned dependency lists and
required Android/Frida assets. It is **not a notarized .app or standalone EXE**.

In Terminal, after extracting the archive:

    sh run-macos.sh --help
    adb devices
    sh run-macos.sh              # Full Textual interface, no automatic checkout
    sh run-macos.sh --check      # Step 0, can modify emulator settings
    sh run-macos.sh --list       # Step 1, no subscription checkout
    sh run-macos.sh --step 2     # Open TUI with Step 2 selected; DOES NOT auto-pay
    sh run-macos.sh --step 3 --sequence   # Guided steps, approvals required

The selected step does **not** execute simply because the dashboard starts.
Choose Run, review the account and charges, then explicitly approve the
modal to start a paid stage. Stop during a paid stage prevents later stages
but cannot undo a remote checkout already initiated.

## Account and payment safeguards

Before Steps 2–5, the native adapter:

1. Selects one unique authorized ADB device and runs environment checks.
2. Requests fresh offer metadata for the exact stage, without checkout.
3. Verifies the current Google Play account and requires matching account
   information from the listing report.
4. Rejects missing/wrong accounts, unavailable offers and nonzero-priced
   introductory phases. It never uses --force or switches accounts.
5. Rechecks the account immediately before invoking the existing Android
   checkout flow, with a separate TUI confirmation for each stage.
6. Keeps the resulting report separate by account identity; a submitted
   checkout is **not proof of activated subscription**.

CI mocks these checks. Actual Play Store terms, renewal state and Frida
behavior must still be verified independently on a real device.

## CI testing and limitations

The macOS workflow checks Intel and Apple Silicon runners when available,
runs Python and POSIX shell syntax checks, validates pinned Frida dependencies,
exercises mock-only stage and approval tests and uploads a source ZIP with a
SHA-256 checksum. The Windows regression suite remains independent.

Because the maintainer has no Mac hardware, **no end-to-end Android test,
actual Google Play transaction or confirmed subscription extension** has been
performed on macOS. Treat the result as a development build, not fully
supported or notarized software. Never report successful checkout solely
from a local script exit code or CI status.
