# Android batch research shortcuts

This research branch replaces the six historical Windows batch entrypoints with compatibility wrappers and adds independently written English-named batch files. The upstream files were not copied because no license was identified.

Run the files from this directory in Windows Command Prompt with one authorized Android device and a supported ADB installation. The environment shortcuts check prerequisites only; the offer shortcuts open Google One on Android for manual review. They do not query hidden SKU data, guarantee eligibility, select offers, stack subscriptions or initiate real Google Play checkout. The 14 numbered research shortcuts open the corresponding official app after confirmation.

The former `--force` account bypass is removed from these batch files. Original step names remain callable for compatibility but no longer execute the old purchase behavior. The root launcher includes research review routing, and the engine now leaves Subscribe to the user. Direct research checkout remains disabled.

See [research notes](../../research/g1-acq-plus-android-batch/README.md) and [security guidance](../../SECURITY.md).

## Research Steps 6–19

The named research offer batch files call `run-all.ps1 -Step N` and prompt for explicit confirmation before opening the official app. They are independently written wrappers, not imported upstream checkout scripts. The labels are unverified; no offer is selected automatically.
