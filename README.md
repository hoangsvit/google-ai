# ePlus AI Toolkit

**Languages:** **English** · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md)

Unofficial terminal toolkit for inspecting **Google AI Pro offers** on Android with ADB, Frida and Google Play. Windows is the maintained release platform; a **full Steps 0–5 macOS port** is under development on `dev`.

<img width="960" alt="ePlus AI Toolkit Textual dashboard" src="https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3" />

> [!CAUTION]
> **Potential real charges.** Steps **2–5** can open Google Play checkout and automatically tap Subscribe. Listed offers, a $0 introductory price or a submitted checkout **do not prove eligibility or subscription activation**. Verify today's amount, future charges, active Google Play account and renewal date yourself. Environment checks can also modify Android/Frida/network settings. [Read the safety guide](docs/SAFETY.md).

## Quick start

**Windows (stable)** — Install [MuMuPlayer](https://www.mumuplayer.com/download/) separately, ensure Android root/ADB and Google Play/Google One work, then open PowerShell:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

The no-argument command opens the Textual dashboard. **Check Device & Offers** runs the offer-listing check (Step 1); it does not initiate subscription checkout.

**macOS (development preview)** — Requires Python 3.10+, ADB and a compatible rooted Android device. Use the `dev` branch:

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
git switch dev
sh run-macos.sh
```

The macOS code exposes all six stages, but real-device/MuMu and checkout behavior **have not been validated**. Do not assume a green CI run proves billing compatibility. See the [Mac setup and limitations](docs/MACOS-PREVIEW.md).

## Documentation

| Topic | Guide |
| --- | --- |
| All guides and translations | **[Documentation hub](docs/README.md)** |
| Install Windows and configure MuMu | [Installation & first run](docs/INSTALLATION.md) |
| Dashboard, steps, controls and CLI | [Usage guide](docs/USAGE.md) |
| macOS setup and full-stage preview | [macOS guide](docs/MACOS-PREVIEW.md) |
| Errors and troubleshooting | [Troubleshooting](docs/TROUBLESHOOTING.md) · [Advanced diagnostics](docs/DETAILED-GUIDE.md) |
| Billing and account security | [Safety](docs/SAFETY.md) · [Security](SECURITY.md) |
| Structure, release process and credits | [Project information](docs/PROJECT.md) |

[GitHub Releases](https://github.com/hoangsvit/google-ai/releases) · [Report an issue](https://github.com/hoangsvit/google-ai/issues) · [Contribute via `dev`](CONTRIBUTING.md) · [Disclaimer](DISCLAIMER.md) · [Third-party notices](THIRD_PARTY_NOTICES.md)

Original project: [gylive/google-ultra](https://github.com/gylive/google-ultra). Maintained by [David Nguyen (@hoangsvit)](https://github.com/hoangsvit) at [ePlus.DEV](https://eplus.dev). Not affiliated with Google, Google Play, Google One, NetEase or MuMuPlayer.
