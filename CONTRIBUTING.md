# Contributing

Thanks for helping improve the Windows, macOS and Linux implementations of this toolkit. The original implementation comes from [gylive/google-ultra](https://github.com/gylive/google-ultra); current maintenance is by [David Nguyen (@hoangsvit)](https://github.com/hoangsvit).

## Report an issue

Use [GitHub Issues](https://github.com/hoangsvit/google-ai/issues) and include the command, Windows/Android version, relevant non-sensitive errors, and steps to reproduce. **Redact** Google account emails, passwords, payment details, offer/purchase tokens, device identifiers, and local credentials.

## Branches and releases

- **`main`** is the stable release branch; do not push features or documentation changes directly to it.
- **`dev`** is the integration branch. Branch from `dev` and open each feature/fix PR **against `dev`**, not `main`.
- After review and green CI, a separate reviewed PR promotes `dev` into `main`. Releases are created only from `main`.
- This routing is checked by GitHub Actions; repository admins should additionally make the branch-policy check required in branch protection / rulesets for both `main` and `dev`.

## macOS preview contributions

The experimental [full macOS port](docs/MACOS-PREVIEW.md) includes Steps 0–5 and per-stage checkout safeguards. Changes must include mock-only tests for account/offer validation, approval and error paths on Mac runners. Never attempt live checkout in CI or claim real-device compatibility from mocks. Send PRs to `dev` first.

## Linux contributions

The [Linux launcher](docs/LINUX.md) shares the native stage adapter with macOS. CI runs offline tests on Ubuntu with Python 3.11 and 3.13. Validate device compatibility separately on a rooted test phone and stop the hardware test if the phone becomes unstable.

## Propose a change

Open a [pull request](https://github.com/hoangsvit/google-ai/pulls) targeting `dev` with one focused improvement. Keep the original step mappings intact, explain any behavior change, and add mock tests for fixes. Do not run live subscription checkout in CI.

Before opening the PR, prepare the **test-only Textual dependency** and run the Python suite (no Android device or purchase required). Use the shell appropriate for your OS:

**Windows PowerShell:**

```powershell
python -m pip install -r requirements-tui.txt
python -m unittest discover -s tests -v
```

**macOS Terminal (zsh/bash, no PowerShell):**

```sh
python3 -m pip install -r requirements-tui.txt
python3 -m unittest discover -s tests -v
python3 -m py_compile macos_runner.py
sh -n run-macos.sh
```

If Node.js and PowerShell are available (**Windows or a host where PowerShell is deliberately installed**), also run the offline JavaScript and PowerShell checks used by GitHub Actions. **Mac contributors do not need to install PowerShell**; CI runs the Windows-specific suite separately:

```powershell
node --test tests/test_activity_lookup.test.mjs tests/test_subscription_update.test.mjs
pwsh -File ./tests/test_report_identity.ps1
pwsh -File ./tests/test_terminal_prompts.ps1
pwsh -File ./tests/test_user_errors.ps1
```

On Windows PowerShell 5.1, you can use `powershell -File` instead of `pwsh -File` where supported. **Do not** run paid Steps 2–5 or real Google Play checkout to validate a PR. GitHub Actions runs the offline checks automatically; passing them is not proof of real-device or billing compatibility.

Documentation and terminal usability fixes are welcome. Preserve attribution to upstream authors and retain their MIT notice.

## Documentation changes

- Preserve the original detailed format of all root READMEs (Windows + macOS setup, dashboard, CLI, troubleshooting, safety and credits). Keep additional technical guidance in the [documentation hub](docs/README.md); do not require users to switch branches to install either platform.
- Update the full English README and six root-language READMEs together. Review topic-specific docs and historical translations under `docs/i18n/` for consistency.
- Always preserve billing warnings and verification requirements. Do not confuse a Google Play offer listing, submitted checkout or authorization hold with successful subscription activation.
- Before submitting a PR, run `python -m unittest discover -s tests -p 'test_readme_locales.py' -v` and `python -m unittest discover -s tests -p 'test_docs_navigation.py' -v` to check links, classic README structure and platform installation guidance.

## Translations

The root [English README](README.md) is the maintained reference. Translated guides are [Vietnamese](README.vi.md), [Simplified Chinese](README.zh-CN.md), [Japanese](README.ja.md), [Korean](README.ko.md), [Spanish](README.es.md), and [French](README.fr.md).

When changing the installation requirements, stage/CLI behavior, or billing/security warnings, update all localized READMEs in the same PR. Keep PowerShell commands, code identifiers, original attribution, disclaimer links and safety boundaries identical in meaning. Do not translate executable flags or UI labels that remain in English. Run `python -m unittest discover -s tests -p 'test_readme_locales.py' -v` to check links and key safety text. Other detailed documentation is maintained in English unless explicitly localized.
