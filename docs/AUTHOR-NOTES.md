# Notes from the original author's README (translated and qualified)

[Documentation home](README.md) · [Project overview](../README.md)

> **Historical claims, not verified guidance.** The original Chinese README advertised a 12-month Google AI Ultra promotion, claimed certain accounts could obtain 20 TB or 30 TB offers, and described the possibility of renewing or cancelling after an introductory period. These claims were written by the original author and should not be read as Google policy or proof of any current promotional entitlement.

## Original implementation overview

The script runs on a rooted Android device or emulator, attaches Frida to Google One, and calls Android BillingClient to enumerate offer IDs and pricing phases. It optionally invokes the Android purchase dialog. The original author said the program:

1. Installs or selects an existing Google account on Android.
2. Checks which Google Play account is currently active.
3. Starts Google One and injects a billing helper.
4. Queries product details and promotional phases.
5. Optionally opens a Google Play billing flow and inspects the displayed price.
6. Attempts to verify the subscription in the official Play Store page.
7. Writes diagnostic output to `ultra0-report/`.

The author's example checkout dates, advertised plan lengths and historical renewal prices are **illustrative, not current offers**. The server and Google Play can reject an offer that appears in a BillingClient response.

## Supported tools

- Python 3.10+ and Android platform-tools (ADB)
- Compatible Frida Python module and `frida-server`
- A rooted Android installation with Google Play and Google One

The original author gave commands such as `python ultra0.py --check`, `python ultra0.py --list`, and `python ultra0.py accounts.txt`. Using account files containing passwords and card information is discouraged. The current recommendation is `run-all.ps1 -ListOnly`, followed by manual verification directly in Google Play.

**Caution:** The source still contains legacy code for filling Android login and payment forms and can automatically press Subscribe. Do not use `--force` to suppress an unverified account mismatch. Do not publish complete reports or tokens.

See [the maintained English guide](DETAILED-GUIDE.md), [the original stage mapping](ORIGINAL-STEPS.md) and [security notes](../SECURITY.md).
