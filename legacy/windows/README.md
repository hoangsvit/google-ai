# Android batch research shortcuts

This research branch replaces the six historical Windows batch entrypoints with compatibility wrappers and adds eight independently written English-named batch files. The upstream files were not copied because no license was identified.

Run the files from this directory in Windows Command Prompt with one authorized Android device and ADB on PATH. The environment shortcuts check prerequisites only; the offer shortcuts open Google One on Android for manual review. They do not query hidden SKU data, guarantee eligibility, select offers, stack subscriptions or initiate real Google Play checkout. All five offer-specific shortcuts differ only by the displayed reference label.

The former `--force` account bypass is removed from these batch files. Original step names remain callable for compatibility but no longer execute the old purchase behavior. The separate root launcher and Python engine remain unchanged.

See [research notes](../../research/g1-acq-plus-android-batch/README.md) and [security guidance](../../SECURITY.md).
