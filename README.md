# ePlus AI Toolkit

**Languages:** **English** · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md)

A terminal toolkit to inspect Google AI Pro offers and manage the original Android workflow via ADB, Frida and Google Play. **Windows and macOS use the same Textual interface**, with separate launchers.

<img width="960" alt="ePlus AI Toolkit dashboard" src="https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3" />

> [!CAUTION]
> **Unofficial project; real charges are possible.** Steps **2–5** can open Google Play checkout and press Subscribe. A listed offer, a $0 initial price or a checkout request does **not** prove eligibility, activation or extension. Verify the account, today's charge, recurring price and renewal date in Google Play. [Safety & billing](docs/SAFETY.md).

## Installation

### Windows

1. Install **Python 3.10+**, **Git** and [MuMuPlayer for Windows](https://www.mumuplayer.com/download/). PowerShell 5.1+ is required.
2. Start an Android instance with **root and ADB debugging** enabled. Install/open **Google Play Store** and **Google One**, signed in to the intended account.
3. Open **PowerShell** and run:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

The launcher prepares required tools when needed. [Windows installation details](docs/INSTALLATION.md).

### macOS

1. Install **Python 3.10+**, **Git** and **Android SDK Platform-Tools (ADB)**. With Homebrew: `brew install android-platform-tools`.
2. Connect a **rooted Android device** with Google Play Store and Google One, or use a compatible rooted emulator. **MuMuPlayer Pro for Mac is for Apple Silicon**; Intel Macs need another compatible Android setup.
3. Open **Terminal** and run:

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
sh run-macos.sh
```

The Mac launcher installs dependencies in a local `.venv`. **Steps 0–5 are implemented, but actual Mac/MuMu and billing compatibility have not been verified.** See [Mac installation and branch availability](docs/MACOS-PREVIEW.md).

## First run (both platforms)

Use **Check Device & Offers** for Step 1 (offer listing, not checkout). Step 0 checks the Android environment and may change ADB/Frida/emulator settings. **Only run Steps 2–5 after reviewing the actual Google Play terms.** They may result in payment.

## Documentation

[Full documentation](docs/README.md) · [Windows setup](docs/INSTALLATION.md) · [Mac setup](docs/MACOS-PREVIEW.md) · [Usage / CLI](docs/USAGE.md) · [Troubleshooting](docs/TROUBLESHOOTING.md) · [Safety](docs/SAFETY.md) · [Project information](docs/PROJECT.md)

[Releases](https://github.com/hoangsvit/google-ai/releases) · [Issues](https://github.com/hoangsvit/google-ai/issues) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Disclaimer](DISCLAIMER.md) · [Third-party notices](THIRD_PARTY_NOTICES.md)

Original project: [gylive/google-ultra](https://github.com/gylive/google-ultra). Maintained by [David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev). Not affiliated with Google or MuMuPlayer.
