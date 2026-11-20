# AGENTS.md — ePlus AI Toolkit

Instructions for coding agents working in this repository. Read this file, `README.md`, `CONTRIBUTING.md`, and `SECURITY.md` before changing code. Prefer the implementation on the current target branch over old PR descriptions, screenshots, or previous task summaries.

## macOS full-stage port constraints

- `run-macos.sh` launches the shared Textual dashboard with Steps 0–5. `macos_runner.py` is the macOS-native adapter to the **unchanged** Android engine; do not invoke Windows-only `setup_env.py` on Mac.
- Do not bypass stage confirmation, current Google Play account lookup, exact offer ID or zero-price introductory phase validation. The Mac adapter intentionally does **not** support `--force` or automatic account switching.
- Steps 2–5 may initiate real charges. Every stage requires a separate TUI approval, and continuing a sequence requires user verification of the subscription and renewal date in Google Play. The native CLI requires explicit authorization flags.
- macOS CI is restricted to unit and integration mocks; never run a real checkout in CI, and never claim that a successful host run verifies actual Mac/MuMu billing.
- Follow the existing dev-first PR workflow, but treat real Mac/Android hardware validation and publication as separate release gates. Preserve Windows behavior.


## Project purpose and boundaries

**ePlus AI Toolkit** is a Windows and macOS Python toolkit for inspecting Google AI Pro offers on Android. Windows uses PowerShell (`run-all.ps1`) and its setup helper; macOS uses Terminal/zsh/bash (`run-macos.sh` and `macos_runner.py`) and must never be instructed to run the Windows `.ps1` or `.bat` setup tools. The Textual UI must remain an interface to the existing engine, not a second implementation of Android, Frida, account, offer, or Google Play Billing logic.

- **`run-macos.sh` / `macos_runner.py`** — macOS-only POSIX launcher and native stage adapter; no PowerShell or Windows `setup_env.py` on Macs.
- **`run-all.ps1`** — Windows entrypoint. No parameters launches the Textual dashboard; explicit `-Step N`, `-Cli`, or `-AllStages` use the CLI path. Read the real parameter and approval logic before changing an option.
- **`tui.py`** — Textual dashboard, user confirmations, subprocess orchestration, live output and safe Stop/Exit handling.
- **`tui_core.py`** — stage mapping, command construction, setup requirements, fresh-report validation and outcome interpretation.
- **`ultra0.py`** — upstream-derived Android/Frida/Google Play integration; treat changes here as high risk.
- **`setup_env.py`**, `scripts/`, `tools/windows/setup-environment.bat` — environment detection, setup and compatibility. Historical `legacy/windows/*.bat` shortcuts are not the supported entrypoint; preserve their relative paths and explicitly flag their `--force` risk.
- **`tests/`** — offline regression checks. Test with mocks instead of connecting to real Google accounts or buying subscriptions.
- **`README.md`**, `docs/`, `SECURITY.md`, `THIRD_PARTY_NOTICES.md` — public guidance, provenance and safety constraints.

The current stage contract is **0: Environment**, **1: Available offers**, **2: Pro 12 months**, **3: Pro +6 months**, **4: second Pro +6 months**, **5: optional +6 months**. Keep these numeric meanings and report formats compatible.

## Non-negotiable safety rules

1. **Step 1 is the default quick-check action, not the no-argument CLI default.** Running `run-all.ps1` without arguments opens the Textual dashboard; the visible **Check Device & Offers** action invokes Step 1 and must not initiate checkout. Step 0 may still modify local/emulator setup (ADB/Frida/proxy), so do not characterize Step 0 as entirely side-effect-free.
2. **Steps 2–5 may charge money.** They can open Google Play checkout or press Subscribe through upstream code. Never automatically trigger those stages at startup, silently approve them, or run a real checkout in CI.
3. Every checkout stage in the TUI requires a **separate, explicit approval**. Guided sequences must require the user to check Google Play subscriptions/charges/renewal terms before offering **Verified in Google Play → Next**. `checkout_requested` remains a **current internal status** assigned by `ultra0.py` when the Subscribe tap is reported; it is **not** activation, success, or proof of eligibility. Do not remove or rename it in code or fixtures based solely on a UI change. Prefer plain-language descriptions in end-user docs.
4. Preserve account/device checks; never default to `--force` or `-Force`, bypass payment/security eligibility, or imply that a zero-priced first phase guarantees a free subscription.
5. Preserve **Stop/Exit distinctions**: read-only steps 0–1 can request termination of their own subprocess tree; checkout steps 2–5 are **not** force-killed mid-transaction because their remote outcome could be unknown. Exit during checkout waits for the current step and must not start another. Avoid orphaned processes and killing unrelated processes.
6. Do not print, commit, or expose Google emails, passwords, card details, billing/offer/purchase tokens, local device identifiers, or unredacted reports. Keep `logs/`, `ultra0-report/`, `accounts.txt` and local configuration out of commits. Mask or sanitize samples and screenshots.
7. Keep attribution to upstream **[gylive/google-ultra](https://github.com/gylive/google-ultra)** and maintainer **[@hoangsvit](https://github.com/hoangsvit)**. Preserve the upstream MIT notice in `THIRD_PARTY_NOTICES.md`; do not assume that notice automatically licenses unrelated contributions.

## Textual UX contract

The UI is for everyday users, not just developers:

- Default screen: clear **ePlus AI Toolkit** branding, one visible **Check Device & Offers** button and an immediately visible **Live Status** area.
- **Advanced: Run by step** is opt-in. Its modes must mean exactly: **One step only** (selected 0–5), **From selected step** (guided 2–5), **All: Steps 2–5** (guided from Step 2). The CLI's `-AllStages` is not necessarily identical to the TUI sequence.
- Place workflow configuration in a **wide content area**, not the narrow sidebar. Do not cram long hint text, dropdowns, or a tall primary button into the step list. Use readable labels, clear spacing and scroll containment.
- During an active step, disable **all ways to start another step** (including keyboard actions, selectors, and quick start). Keep Help and technical log access usable; show Stop/Next only when meaningful.
- Show real state and elapsed time. **Do not invent percentages**, mark a step as successful without verified output, or present an inactive account/device as connected.
- Keep both author credits as clickable GitHub links when supported.
- Design and test terminal widths/heights around **90×20 and 110×35**; also handle narrower terminals without hiding the primary action or status behind an unscrollable panel.
- Do not hide actionable error information solely inside Debug. User-facing error summaries should explain what failed and what is safe to do next; technical details may include sanitized diagnostics.

## Branch routing and integration

- `main` is the production/release branch. Never develop new features or reorganize files directly on `main`.
- `dev` is the shared integration branch. Create feature/fix branches **from `dev`** and open Draft PRs **targeting `dev`**; run relevant Linux and Windows checks before integration.
- After validation, promote **`dev` → `main`** through a separate reviewed PR. Only publish a release from tested `main`. Do not merge feature branches straight into `main`.
- Keep active Windows entrypoints and imported Python modules at their current paths until tests prove a separate migration safe; move legacy installers/shortcuts with path updates and documentation.

## Development workflow

1. Inspect the latest target branch, existing PRs/issues and relevant code. Do not base a new change on an unrelated unmerged PR or overwrite concurrent work.
2. Prefer the smallest focused patch. Keep `tui.py` for interaction/layout and `tui_core.py` for pure parsing, stage and outcome rules. Never duplicate checkout/Frida routines inside TUI.
3. Add regression tests for each bug. In tests, mock `subprocess.Popen` or the relevant application methods; **never** connect to a production emulator or initiate a Google Play transaction.
4. Run, when available, using the shell native to the host:

   **Windows PowerShell:**
   
   ```powershell
   python -m unittest discover -s tests -v
   python -m py_compile tui.py tui_core.py
   ```

   **macOS Terminal (zsh/bash; no PowerShell required):**

   ```sh
   python3 -m unittest discover -s tests -v
   python3 -m py_compile tui.py tui_core.py macos_runner.py
   sh -n run-macos.sh
   ```

   Also run repository CI/static checks and any targeted test files affected by the patch. For layout changes, verify widget visibility, geometry, focus and scrollability at both compact and normal terminal sizes.
5. Review UI change impact on Step 1 and on the Step 2–5 approval gates. Verify disabled buttons are disabled in **logic as well as appearance**.
6. Update `README.md` and relevant docs when commands, labels, run modes, safety behavior, prerequisites or screenshots change. Avoid shipping code and outdated documentation together.
7. Open a focused **Draft PR targeting `dev`** with: problem, affected files, behavioral changes, tests/results, any unverified Windows/MuMu assumptions, and billing-risk implications. Do not merge or push directly to `main` without explicit authorization. A green CI run is not proof of real-device compatibility.

## Change-specific checklists

**TUI / responsive UI**
- Startup action and Live Status are visible at 90×20.
- Run mode, Step, Run and Quick Check stay locked while busy.
- A click on hidden/disallowed controls or a keyboard shortcut cannot bypass a payment approval.
- No overlap, clipped labels, accidental command palette activation or horizontal overflow.
- Links open the correct profiles and are accessible by keyboard when possible.

**Subprocess / cancellation**
- Use the existing CLI entrypoint and preserve UTF-8 output on Windows.
- Handle child process exit, cancellation and missing reports distinctly.
- Ensure a read-only Stop does not cause a later queued command to launch.
- Treat payment outcomes after interruption as **unknown** until verified in Google Play.

**Reports / eligibility / billing**
- Read only reports generated by the current invocation; stale reports cannot authorize another checkout.
- Keep error codes and account masking consistent.
- Do not infer free months, subscription activation, future billing or eligibility from offer metadata or UI prompts.

## README translation workflow

- Translate from `README.md` on the **current target branch**, never from a prior localized README or `docs/i18n/`. `README.md` is the English content source; `README.en.md` is an English redirect.
- Preserve all canonical major topics, code commands, sections, links, payment warnings, limitations, and technical details in all **six** root localized READMEs. Do not replace full translations with condensed overviews.
- Each root translation contains `<!-- Source README.md git-blob: SHA -->`. Update that marker **only after examining and translating the exact canonical blob**. The gate in `tests/test_readme_source_parity.py` detects stale markers and some missing topics.
- Do not document features that exist only on `dev` when promoting translations to `main`. Translate from the canonical README and actual runtime of the release branch, not a future development branch.
- Write each locale as **natural, reader-friendly documentation**, not a word-for-word machine translation. Prefer the idiomatic technical vocabulary, sentence order, polite form, and punctuation normally used by native speakers of that language. Avoid importing English words such as "checkout", "preflight", "launcher" or "repository" when a clear, common local-language expression exists.
- Keep **actual UI control labels, command syntax, product IDs, file paths, URLs, numerical thresholds and billing/security meanings** unchanged. A natural rewrite must not weaken any warning or introduce unsupported feature claims.
- Perform a final human-quality language pass: read paragraphs as a user would, check consistency of register, Markdown code fences, punctuation, and heading/body separation. The structural tests only catch easily detectable errors.
- This gate is **not a linguistic quality review**: verify wording and actual code behavior manually. In particular never soften the real-billing warnings or imply compatibility and eligibility have been confirmed.
- The guides under `docs/i18n/` are supplemental historical references, **not** the source for root translations; link users to current root translations first.

## Documentation source of truth

Keep the original detailed README format for English and all six localized README files: disclaimer, Windows installation, macOS installation, Textual dashboard, advanced CLI, troubleshooting, support and credits. The default-branch installation commands must work without switching branches. Maintain topic-specific references in `docs/README.md`, `docs/INSTALLATION.md`, `docs/USAGE.md`, `docs/SAFETY.md`, `docs/TROUBLESHOOTING.md`, `docs/PROJECT.md` and `docs/MACOS-PREVIEW.md`. The historical localized guides under `docs/i18n/` remain as additional references.

When moving or changing guidance, keep original safety, billing and credit statements accurate, fix relative links from the document's new directory, and update `tests/test_readme_locales.py` and `tests/test_docs_navigation.py`. Do not collapse the root README to a short landing page again, or claim Mac hardware compatibility based on CI.

## Source of truth and reporting

When instructions conflict, follow security restrictions first; then the current code and tests; then `SECURITY.md`, `CONTRIBUTING.md` and the user documentation. If the implementation disagrees with a user-facing claim, fix or report the discrepancy rather than repeating the claim.

In your PR summary distinguish **verified** (tests actually run) from **not verified** (Windows/MuMu hardware, live Google Play, visual screenshots). Never claim that a change works on the user's device solely because Linux CI passed.
