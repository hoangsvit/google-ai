# Research: lightweight Android environments

Status: exploratory, 2026-11-24. No alternative emulator has passed a live compatibility test in this study. This is a documentation-only change, not a support announcement.

## Goal

Evaluate a lower-resource Android environment for legitimate, authorized app testing without disrupting the existing MuMu workflow. Aim for minimal manual configuration, but never treat security restrictions, certification, account eligibility or payment checks as obstacles to bypass. A device that cannot meet the supported prerequisites must remain unsupported.

## Existing architecture (main)

- `device_selector.py` already consumes online ADB transports and deduplicates proven aliases by boot UUID; preserve its refusal to select arbitrarily among distinct devices.
- `setup_env.py` locates ADB, including MuMu installation paths, and has emulator-specific connection and error messages.
- `run-all.ps1` contains MuMu-oriented messaging and Windows orchestration.
- The README documents pinned Frida 16.5.9, separate OS launchers and remaining hardware validation gaps.
- No production logic is modified by this PR.

## Candidate matrix

| Environment | Host | Research priority | Evidence and limitations |
| --- | --- | --- | --- |
| MuMu | Windows/macOS (supported host variants) | Baseline | Existing documented workflow; measure the same workload rather than relying on marketing. |
| LDPlayer 9 | Windows | First | Android 9; vendor documents minimum requirements. Current app availability and actual resource use are unknown. |
| NoxPlayer | Windows | Second | Vendor documents requirements and Android versions; Android 9 may demand more resources. |
| BlueStacks / MEmu / newer LDPlayer | Windows | Later | Evaluate only after confirming current vendor documentation and permitted testing capabilities. |
| Genymotion / Android Emulator | Desktop | Later | Developer-oriented; distinguish Google Play images from development images and respect their restrictions. |
| Waydroid | Linux | Separate study | Container-based Android; host kernel, app compatibility and certification are gating factors. |
| ReDroid | Linux | Separate study | Containerized Android; cloud deployment and service licensing are distinct concerns. |
| Physical Android | Supported hosts | Control | Existing authorized-device design; device capabilities and OS compatibility vary. |

Sources (vendor/project documentation):
- [LDPlayer 9 requirements](https://www.ldplayer.net/support/pc-system-requirements-for-android-emulator.html)
- [LDPlayer versions](https://www.ldplayer.net/versions)
- [Nox requirements](https://support.bignox.com/en/101/systemrequirement)
- [Nox Android versions](https://support.bignox.com/en/multi/android-version)
- [Android Emulator](https://developer.android.com/studio/run/emulator)
- [Waydroid docs](https://docs.waydro.id/)
- [ReDroid docs](https://github.com/remote-android/redroid-doc)

Vendor minimum host RAM is not measured emulator memory. No performance ranking is established.

## Proposed research scope

1. Inventory already authorized devices using standard ADB discovery; display observed OS, device identity, ABI and connection status. Unknown device brands must remain unknown.
2. Design an opt-in, read-only compatibility report for a developer-owned test app or fixture. Report missing capabilities as unsupported, not automatically remedied. No automatic security changes, root enablement, third-party app instrumentation or account/checkout operations.
3. Keep MuMu and existing stages unchanged. Any future production integration needs a separate reviewed PR and a supported, authorized use case.
4. UX: one read-only diagnostics action; if several distinct devices exist, show a selection prompt. Distinguish disconnected, unauthorized, offline, missing capabilities and unverified environments. Do not claim that an emulator is supported based only on its name.
5. Do not bundle third-party emulator images or proprietary Google apps. Use official downloads and respect licensing.

## Benchmark protocol

On the same Windows host, compare MuMu and LDPlayer 9 first. Record CPU, host RAM, virtualization settings, emulator version, Android version and allocated resources. Use one instance, equivalent display settings and the same developer-owned test app. Measure cold boot to responsive UI, idle process-tree memory and CPU after 5 minutes, peak memory during the test workload, disk footprint and reconnect reliability. Repeat three times; publish median and range with failures. No Google account or payment data is needed for this benchmark.

| Metric | MuMu | LDPlayer 9 | Nox |
| --- | --- | --- | --- |
| Cold boot | Not measured | Not measured | Not measured |
| Idle RAM / CPU | Not measured | Not measured | Not measured |
| Peak RAM | Not measured | Not measured | Not measured |
| Disk footprint | Not measured | Not measured | Not measured |
| Authorized ADB reconnect | Not tested | Not tested | Not tested |

## Future test plan

Offline fixture tests: no devices; offline and unauthorized devices; one authorized device; duplicate aliases; multiple distinct devices; unknown provider; timeout; missing app or unsupported capability; Windows/macOS/Linux regression. Use only synthetic device identities and fake app metadata. Add a screenshot of the mock diagnostics UI in a later implementation PR, clearly marked as simulated. Live hardware testing is separate and must not initiate purchases or modify Google Play behavior.

## Exit criteria

- Reproducible benchmark results on at least one Windows host.
- Documented supported device prerequisites and limitations.
- No regressions to the current MuMu workflow.
- No changes to account eligibility, SKU selection, subscription stages, security checks or billing.
- Explicit user authorization and vendor compliance for any further testing.

This study does not establish that an alternative works without configuration, is lighter in practice, or can access any particular offer. 
