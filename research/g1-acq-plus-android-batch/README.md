# Android batch launcher research

Status: static research only; no third-party executable code imported and no live billing test performed.

## Provenance

- Source: [Dgkncn/g1-acq-plus / android-mumu-scripts](https://github.com/Dgkncn/g1-acq-plus/tree/5a3c9bbe15a71f569789fb6aeafb68735f361c09/android-mumu-scripts)
- Snapshot: 2026-11-26 23:22 UTC (2026-11-27 Vietnam time).
- No repository license was declared in the GitHub metadata or root file listing at review time. Obtain permission or verify applicable licensing before redistributing any upstream script.

## English batch filename reference

The English filenames below now have independently written executable counterparts in [legacy/windows](../../legacy/windows/README.md). They are prerequisite checks and manual offer-review launchers, not direct replacements for upstream billing behavior. The original Chinese filenames are retained as upstream references. All durations, prices and stacking claims are unverified.

| English filename (reference only) | Original upstream filename | Description |
| --- | --- | --- |
| `01_Pro5TB_Free_12_Months.bat` | `01_Pro5TB_免费12个月_直拉收银台.bat` | Claimed 12-month free introductory offer; opens checkout |
| `02_Pro5TB_Free_6_Month_Extension.bat` | `02_Pro5TB_免费叠加6个月_可叠至24个月.bat` | Claimed six-month extension, with a cumulative duration of up to 24 months |
| `03_List_Available_Free_And_Discounted_Offers.bat` | `03_查询当前账号所有可用免费与折扣Offer.bat` | Lists offers for the current account |
| `00_Environment_Self_Check.bat` | `0_环境自检.bat` | Environment self-check |
| `Pro5TB_1.99_Per_Month_12_Months.bat` | `1_Pro5TB_每个月1.99_12个月.bat` | Claimed USD 1.99 per month for 12 months |
| `Pro5TB_1.99_Per_Month_3_Months.bat` | `2_Pro5TB_每个月1.99_3个月.bat` | Claimed USD 1.99 per month for three months |
| `Pro5TB_0.99_For_1_Month.bat` | `3_Pro5TB_1个月0.99.bat` | Claimed USD 0.99 for one month |
| `One_Click_Environment_Setup.bat` | `一键安装环境.bat` | Automated environment setup |

The upstream documentation file `使用说明.txt` translates to `User_Guide.txt`. The Python filenames are already in English: `setup_env.py`, `ultra0.py`, `query_sku.py`, `scan_hidden.py`, `scan_wide.py`, and `requirements.txt` is already in English.

The actual diagnostic launcher in this branch is `check-device.bat`, with English messages.

## Findings

- This repository already has its own Android engine, environment setup, offer-discovery components, Windows launcher and approval controls. Do not replace them with the similarly named third-party files.
- Upstream documentation refers to batch files absent from the snapshot. Its requirements file allows Frida >=16.0, but its setup documentation specifies 16.5.9.
- The upstream self-check invokes its main Python engine; it is not equivalent to a passive device inspection.
- The upstream engine handles sensitive billing and account information. No tokens, private identifiers, credentials, purchase commands or hidden-SKU scan logic are included in this research directory.

## Research scope

The original local-only `check-device.bat` checks Python, ADB availability and the presence of the two apps on one selected Android device. It does not install dependencies, connect to arbitrary endpoints, modify device settings, inject code or invoke the billing engine. Run it from Command Prompt on Windows with a device you control and ADB on PATH. Multiple devices or unauthorized devices require manual resolution in ADB.

Any future integration must preserve the existing approval gates and account validation. Use mock offer data for offline UI tests; do not perform real checkout in CI or circumvent eligibility. Confirm offers and renewal terms in Google Play itself.

The six historical batch entrypoints in legacy/windows are compatibility wrappers in this branch. Root launchers, stage mappings, CI workflows and existing Python code are unchanged. The setup shortcut checks prerequisites only. The offer-specific shortcuts display a reference label and open the same official Google One app; they do not select the named offer.
