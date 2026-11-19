# Contributing

Thanks for helping improve this Windows/MuMu adaptation. The original implementation comes from [gylive/google-ultra](https://github.com/gylive/google-ultra); current maintenance is by [David Nguyen (@hoangsvit)](https://github.com/hoangsvit).

## Report an issue

Use [GitHub Issues](https://github.com/hoangsvit/google-ai/issues) and include the command, Windows/Android version, relevant non-sensitive errors, and steps to reproduce. **Redact** Google account emails, passwords, payment details, offer/purchase tokens, device identifiers, and local credentials.

## Branches and releases

- **`main`** is the stable release branch; do not push features or documentation changes directly to it.
- **`dev`** is the integration branch. Branch from `dev` and open each feature/fix PR **against `dev`**, not `main`.
- After review and green CI, a separate reviewed PR promotes `dev` into `main`. Releases are created only from `main`.
- This routing is checked by GitHub Actions; repository admins should additionally make the branch-policy check required in branch protection / rulesets for both `main` and `dev`.

## macOS preview contributions

The experimental [full macOS port](docs/MACOS-PREVIEW.md) includes Steps 0–5 and per-stage checkout safeguards. Changes must include mock-only tests for account/offer validation, approval and error paths on Mac runners. Never attempt live checkout in CI or claim real-device compatibility from mocks. Send PRs to `dev` first.

## Propose a change

Open a [pull request](https://github.com/hoangsvit/google-ai/pulls) targeting `dev` with one focused improvement. Keep the original step mappings intact, explain any behavior change, and add mock tests for fixes. Do not run live subscription checkout in CI.

Before opening the PR, prepare the **test-only Textual dependency** and run the Python suite (no Android device or purchase required):

```powershell
python -m pip install -r requirements-tui.txt
python -m unittest discover -s tests -v
```

If Node.js and PowerShell are available, also run the offline JavaScript and PowerShell checks used by GitHub Actions:

```powershell
node --test tests/test_activity_lookup.test.mjs tests/test_subscription_update.test.mjs
pwsh -File ./tests/test_report_identity.ps1
pwsh -File ./tests/test_terminal_prompts.ps1
pwsh -File ./tests/test_user_errors.ps1
```

On Windows PowerShell 5.1, you can use `powershell -File` instead of `pwsh -File` where supported. **Do not** run paid Steps 2–5 or real Google Play checkout to validate a PR. GitHub Actions runs the offline checks automatically; passing them is not proof of real-device or billing compatibility.

Documentation and terminal usability fixes are welcome. Preserve attribution to upstream authors and retain their MIT notice.

## Documentation changes

- Keep root README files as short overviews. Move procedures, diagnostics and legacy references to the [documentation hub](docs/README.md). Root overviews must still show direct, parallel Windows and macOS setup steps; keep branch-specific preview guidance in [the Mac guide](docs/MACOS-PREVIEW.md).
- Update the English topic page first, then review the translated detailed guides in `docs/i18n/` if the change affects user-facing instructions. Each root language README links to its detailed guide.
- Always preserve billing warnings and verification requirements. Do not confuse a Google Play offer listing, submitted checkout or authorization hold with successful subscription activation.
- Before submitting a PR, run `python -m unittest discover -s tests -p 'test_readme_locales.py' -v` and `python -m unittest discover -s tests -p 'test_docs_navigation.py' -v` to check links and README size.

## Translations

The root [English README](README.md) is the maintained reference. Translated guides are [Vietnamese](README.vi.md), [Simplified Chinese](README.zh-CN.md), [Japanese](README.ja.md), [Korean](README.ko.md), [Spanish](README.es.md), and [French](README.fr.md).

When changing the installation requirements, stage/CLI behavior, or billing/security warnings, update all localized READMEs in the same PR. Keep PowerShell commands, code identifiers, original attribution, disclaimer links and safety boundaries identical in meaning. Do not translate executable flags or UI labels that remain in English. Run `python -m unittest discover -s tests -p 'test_readme_locales.py' -v` to check links and key safety text. Other detailed documentation is maintained in English unless explicitly localized.
