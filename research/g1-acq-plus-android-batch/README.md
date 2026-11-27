# Android batch launcher research

Status: static research only; no third-party executable code imported and no live billing test performed.

## Provenance

- Source: [Dgkncn/g1-acq-plus / android-mumu-scripts](https://github.com/Dgkncn/g1-acq-plus/tree/5a3c9bbe15a71f569789fb6aeafb68735f361c09/android-mumu-scripts)
- Snapshot: 2026-11-26 23:22 UTC (2026-11-27 Vietnam time).
- No repository license was declared in the GitHub metadata or root file listing at review time. Obtain permission or verify applicable licensing before redistributing any upstream script.

## English batch filename reference

The English filenames below now have independently written executable counterparts in [legacy/windows](../../legacy/windows/README.md). They are prerequisite checks and manual offer-review launchers, not direct replacements for upstream billing behavior. Original upstream filenames can be inspected in the pinned source directory above. All durations, prices and stacking claims are unverified.

| English filename | Description |
| --- | --- |
| `01_Pro5TB_Free_12_Months.bat` | Claimed 12-month free introductory offer; opens checkout |
| `02_Pro5TB_Free_6_Month_Extension.bat` | Claimed six-month extension, with a cumulative duration of up to 24 months |
| `03_List_Available_Free_And_Discounted_Offers.bat` | Lists offers for the current account |
| `00_Environment_Self_Check.bat` | Environment self-check |
| `Pro5TB_1.99_Per_Month_12_Months.bat` | Claimed USD 1.99 per month for 12 months |
| `Pro5TB_1.99_Per_Month_3_Months.bat` | Claimed USD 1.99 per month for three months |
| `Pro5TB_0.99_For_1_Month.bat` | Claimed USD 0.99 for one month |
| `One_Click_Environment_Setup.bat` | Automated environment setup |

The upstream Chinese user guide translates to `User_Guide.txt`. The Python filenames are already in English: `setup_env.py`, `ultra0.py`, `query_sku.py`, `scan_hidden.py`, `scan_wide.py`, and `requirements.txt` is already in English.

The actual diagnostic launcher in this branch is `check-device.bat`, with English messages.

## Findings

- This repository already has its own Android engine, environment setup, offer-discovery components, Windows launcher and approval controls. Do not replace them with the similarly named third-party files.
- Upstream documentation refers to batch files absent from the snapshot. Its requirements file allows Frida >=16.0, but its setup documentation specifies 16.5.9.
- The upstream self-check invokes its main Python engine; it is not equivalent to a passive device inspection.
- The upstream engine handles sensitive billing and account information. No tokens, private identifiers, credentials, purchase commands or hidden-SKU scan logic are included in this research directory.

## Research scope

The original local-only `check-device.bat` checks Python, ADB availability and the presence of the two apps on one selected Android device. It does not install dependencies, connect to arbitrary endpoints, modify device settings, inject code or invoke the billing engine. Run it from Command Prompt on Windows with a device you control and ADB on PATH. Multiple devices or unauthorized devices require manual resolution in ADB.

Any future integration must preserve the existing approval gates and account validation. Use mock offer data for offline UI tests; do not perform real checkout in CI or circumvent eligibility. Confirm offers and renewal terms in Google Play itself.

The six historical batch entrypoints in legacy/windows are compatibility wrappers in this branch. The original checkout stage mappings remain unchanged. Separate review stages and their launchers are documented below. The setup shortcut checks prerequisites only. The offer-specific shortcuts display a reference label and open the same official Google One app; they do not select the named offer.

## TUI backend compatibility update

The existing Windows TUI invokes `setup_env.py` and `run-all.ps1`, whose runtime lookup and Android engine use the ADB locators. This branch adds four MuMuPlayer `nx_main` / `nx_device` installation locations to the setup, connection diagnostic and engine locators. Existing device selection, checkout safeguards, reports and stage mappings are unchanged. This is an ADB compatibility change, not a port of the upstream offer or checkout engine. Steps 1–5 retain their existing offer and transaction behavior. No live device validation has been performed.

## Individual research steps 6–19

Choose another step in the TUI or run `./run-all.ps1 -Step 6` (through 19), or run `python ultra0.py --step 6` (through 19) directly. The original Steps 0–5 and 12+6+6 sequence are unchanged. Research steps are integrated directly into `ultra0.py`: the engine queries Google Play for the step's exact reference offer (product, first-phase period and first-phase price must all match) and opens that offer's checkout only on an exact match; otherwise it stops with `offer_not_available`. Steps whose product ID has never been verified (Google AI Plus, Google One storage plans, YouTube Premium) fail closed with `research_product_unverified` instead of guessing a product ID. The step labels are unverified upstream references. No eligibility bypass is implemented. Recheck Step 1 after any research step.

## TUI cleanup

The redundant Browse more offers button has been removed. Select a numbered research step and press Run selected step to approve and run it in ultra0.py; the result dialog displays the engine's result status.

## Confirmation and batch entrypoints

The TUI requires a current Step 1 session and shows its observed-record count and account hint before requiring Confirm & run step. Cancelling does not run anything. CLI and English batch wrappers for Steps 6–19 ask for a numeric confirmation before invoking ultra0.py, unless the TUI's confirmation is passed through with `-ConfirmOfferReview`. Eligibility is only established when Google Play returns the exact reference offer. Steps 0–5 remain unchanged. No hardware test was performed.

## Sidebar step list

The left STEPS panel retains Steps 0–5 (Step 5 remains conditional) and shows Steps 6–19 in the same responsive scrollable STEPS list, with navigation controls below. The separate MORE (REVIEW) header and fixed-height nested list were removed. Compact labels use full terms as tooltips. An exclamation marker means the step ran in ultra0.py, not a completed subscription.

## Android launcher compatibility

The legacy `research_offer_runner.py` app opener (kept for reference, no longer used by the TUI, `run-all.ps1` or the batch wrappers) resolves the installed official app's normal launcher activity if the package-only intent fails. A component outside the expected package is rejected. The CLI reports launcher_unresolved or launcher_rejected instead of silently failing.

## Temporary manual-only checkout

Automatic Subscribe taps are disabled in the existing engine. Even when the current checks match, the engine leaves checkout open and reports `manual_confirmation_required`; the user must review and confirm in Google Play. No automatic sequence advance is authorized by this status. This applies to research Steps 6–19 as well: ultra0.py opens the exact-match checkout, but the Subscribe tap itself is always manual.
