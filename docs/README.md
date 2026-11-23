# ePlus AI Toolkit — Documentation

[← Project overview](../README.md) · [Security](../SECURITY.md) · [GitHub Releases](https://github.com/hoangsvit/google-ai/releases)

This is the **version-controlled documentation hub** for the Windows, macOS and Linux toolkit. Start with the platform guide, then follow only the instructions relevant to your goal. The main README retains the original full user guide format, including platform installation and detailed usage.

> [!CAUTION]
> **Unofficial project. Steps 2–5 can initiate real Google Play charges.** A listed offer or a $0 introductory price does not prove subscription eligibility, activation or renewal. Review the current account, today's charge, later prices and subscription details directly in Google Play. See [Safety & billing](SAFETY.md).

## Platform software requirements

| | Windows | macOS |
| --- | --- | --- |
| Shell | **PowerShell 5.1+** | **Terminal (zsh/bash)**; PowerShell is **not** needed |
| Python and Git | Python **3.10+** and Git | Python **3.10+** and Git |
| Android | Root/ADB-enabled MuMuPlayer or authorized Android device with Google Play Store and Google One | Rooted compatible Android device/emulator with both apps; MuMuPlayer Pro for Mac is an Apple Silicon option, not Intel |
| ADB and Frida | Windows launcher can locate/install Platform-Tools and prepare Frida **16.5.9** | Install ADB separately (e.g. `brew install android-platform-tools`); Mac launcher installs Frida **16.5.9** into `.venv` |
| Launcher | `.\run-all.ps1` | `sh run-macos.sh` or `ePlus-AI-Toolkit.command` |
| Setup guide | [Windows requirements and installation](INSTALLATION.md) | [macOS requirements and installation](MACOS-PREVIEW.md) |

Use the native setup instructions for [Linux](LINUX.md). Automated checks use mocks for billing on every platform. Real Mac/MuMu billing remains unverified.

## Start here

| Goal | Guide |
| --- | --- |
| Install Windows, MuMuPlayer, Python and ADB | [Installation & prerequisites](INSTALLATION.md) |
| Start the dashboard and use the guided steps | [Dashboard & PowerShell CLI](USAGE.md) |
| Install and use the macOS version (Steps 0–5) | [macOS guide](MACOS-PREVIEW.md) |
| Set up Ubuntu and a rooted USB phone | [Linux guide](LINUX.md) |
| Diagnose ADB, Frida, account or billing errors | [Troubleshooting & results](TROUBLESHOOTING.md) |
| Deep dive into setup and compatibility | [Advanced technical guide](DETAILED-GUIDE.md) |
| Understand charge risks and limitations | [Safety & billing](SAFETY.md) · [Security policy](../SECURITY.md) |
| Check the original author's steps and legacy shortcuts | [Historical stage reference](ORIGINAL-STEPS.md) · [Author notes](AUTHOR-NOTES.md) |
| Verify a Windows release on actual hardware | [Manual Windows smoke test](WINDOWS-SMOKE-TEST.md) |
| Review files, branch policy and authorship | [Project structure & credits](PROJECT.md) |
| Review release changes | [Release notes: v1.0.1](releases/v1.0.1.md) · [All releases](https://github.com/hoangsvit/google-ai/releases) |

## Detailed guides in other languages

Detailed localized historical guides are also available alongside the full root-language READMEs:

- [Vietnamese](i18n/README.vi.md) · [Simplified Chinese](i18n/README.zh-CN.md) · [Japanese](i18n/README.ja.md)
- [Korean](i18n/README.ko.md) · [Spanish](i18n/README.es.md) · [French](i18n/README.fr.md)

Translations are maintained on a best-effort basis. For the latest technical behavior, use the English guides and the code on the selected branch.

## Getting help and contributing

[Report an issue](https://github.com/hoangsvit/google-ai/issues) · [Contributing](../CONTRIBUTING.md) · [AI agent development instructions](../AGENTS.md) · [Disclaimer](../DISCLAIMER.md) · [Third-party notices](../THIRD_PARTY_NOTICES.md)

Work on the `dev` branch first; changes are promoted to `main` and published only after review. Automated checks do not validate real Google Play purchases.
