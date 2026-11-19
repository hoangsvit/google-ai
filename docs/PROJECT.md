# Repository structure, maintenance and credits

[Documentation home](README.md) · [Repository README](../README.md) · [Safety](SAFETY.md)

## Repository structure

Keep the active platform launchers and imported Python modules at the repository root. **Use `run-all.ps1` on Windows or `run-macos.sh` on macOS.**

| Location | Purpose |
| --- | --- |
| `run-all.ps1` | Windows entrypoint (Textual dashboard and guided CLI) |
| `run-macos.sh`, `ePlus-AI-Toolkit.command`, `macos_runner.py` | macOS launcher and adapter (Steps 0–5; real-device checkout unverified) |
| `tui.py`, `tui_core.py`, `ultra0.py`, `setup_env.py`, `device_selector.py`, `query_sku.py` | Active Python runtime and supporting tools; kept in place for compatibility |
| [`tools/windows/`](../tools/windows/README.md) | Optional manual Windows setup shortcut; not required for normal launch |
| [`legacy/windows/`](../legacy/windows/README.md) | Historical batch shortcuts; some bypass account checks with `--force` and may initiate a **real charge**. Use the maintained launcher instead |
| `scripts/`, `assets/` | Runtime helpers and bundled Android/Frida assets |
| `tests/`, `.github/workflows/`, `docs/` | Offline regression tests, CI and reference documentation |

**Branch policy:** Features and maintenance changes target [`dev`](https://github.com/hoangsvit/google-ai/tree/dev) first. After validation, merge `dev` into `main` through a reviewed PR. Production releases are built from `main`; reorganizing files must not trigger a release.

## Documentation and contributing

- [Install guide — GitHub Wiki](https://github.com/hoangsvit/google-ai/wiki/Install)
- [Detailed setup and troubleshooting](DETAILED-GUIDE.md)
- [Original author's stage and batch-file reference](ORIGINAL-STEPS.md)
- [Historical author notes](AUTHOR-NOTES.md)
- [Full disclaimer](../DISCLAIMER.md)
- [Security and billing precautions](../SECURITY.md)
- [Contributing](../CONTRIBUTING.md) · [AI agent guidelines](../AGENTS.md) · [Third-party notices](../THIRD_PARTY_NOTICES.md)

GitHub Actions checks Python, PowerShell, Textual and mocked Frida/Billing behavior **without initiating real Google Play transactions**. Passing CI does not prove hardware compatibility or subscription eligibility.

## Credits

- **Original author:** [@gylive](https://github.com/gylive) — upstream [google-ultra](https://github.com/gylive/google-ultra), including the original Python/ADB/Frida/Google Play approach.
- **Maintainer:** [David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev) — Windows/MuMu adaptation, terminal UI, compatibility fixes, tests and documentation.
- [Community contributors](https://github.com/hoangsvit/google-ai/graphs/contributors)

The upstream MIT notice is retained in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md); that notice does not independently license unrelated new contributions.
