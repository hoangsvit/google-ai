# Android batch launcher research

Status: static research only; no third-party executable code imported and no live billing test performed.

## Provenance

- Source: [Dgkncn/g1-acq-plus / android-mumu-scripts](https://github.com/Dgkncn/g1-acq-plus/tree/5a3c9bbe15a71f569789fb6aeafb68735f361c09/android-mumu-scripts)
- Snapshot: 2026-11-26 23:22 UTC (2026-11-27 Vietnam time).
- No repository license was declared in the GitHub metadata or root file listing at review time. Obtain permission or verify applicable licensing before redistributing any upstream script.

## Batch inventory

The following labels describe upstream filenames and author claims only. They are not eligibility or price guarantees.

| Upstream filename | Purpose claimed |
| --- | --- |
| `01_Pro5TB_免费12个月_直拉收银台.bat` | 12-month free introductory offer |
| `02_Pro5TB_免费叠加6个月_可叠至24个月.bat` | 6-month extension; claimed cumulative duration of 24 months |
| `1_Pro5TB_每个月1.99_12个月.bat` | USD 1.99 monthly for 12 months |
| `2_Pro5TB_每个月1.99_3个月.bat` | USD 1.99 monthly for 3 months |
| `3_Pro5TB_1个月0.99.bat` | USD 0.99 for one month |
| `03_查询当前账号所有可用免费与折扣Offer.bat` | Offer listing |
| `0_环境自检.bat` | Environment self-check |
| `一键安装环境.bat` | Environment setup |

## Findings

- This repository already has its own Android engine, environment setup, offer-discovery components, Windows launcher and approval controls. Do not replace them with the similarly named third-party files.
- Upstream documentation refers to batch files absent from the snapshot. Its requirements file allows Frida >=16.0, but its setup documentation specifies 16.5.9.
- The upstream self-check invokes its main Python engine; it is not equivalent to a passive device inspection.
- The upstream engine handles sensitive billing and account information. No tokens, private identifiers, credentials, purchase commands or hidden-SKU scan logic are included in this research directory.

## Research scope

The original local-only `check-device.bat` checks Python, ADB availability and the presence of the two apps on one selected Android device. It does not install dependencies, connect to arbitrary endpoints, modify device settings, inject code or invoke the billing engine. Run it from Command Prompt on Windows with a device you control and ADB on PATH. Multiple devices or unauthorized devices require manual resolution in ADB.

Any future integration must preserve the existing approval gates and account validation. Use mock offer data for offline UI tests; do not perform real checkout in CI or circumvent eligibility. Confirm offers and renewal terms in Google Play itself.

No changes to production launchers, stage mappings, CI or existing Python code.
