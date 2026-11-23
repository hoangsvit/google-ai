# Linux setup and verification

[Documentation home](README.md) · [Dashboard usage](USAGE.md) · [Safety](SAFETY.md)

The Linux launcher targets Ubuntu x86_64 and exposes Steps 0–5 through the shared Textual dashboard. Use a rooted Android test device you control. If you only need to check the USB connection, use **Diagnose Android connection** in the dashboard.

**Android 16 and later.** The Linux launcher blocks all stages before device setup when the Android SDK is 36 or higher, or if it cannot read the SDK version. The toolkit pins Frida 16.5.9. Frida first announced Android 16 support in 17.1.4. The USB connection diagnostic remains available. [Frida 17.1.4 release notes](https://frida.re/news/2025/06/10/frida-17-1-4-released/).

The engine used by Steps 0 and 1 can request an ADB daemon restart for root, deploy or restart the Android Frida server, copy a billing module, clear the Android global HTTP proxy, and force-stop supported VPN apps.

## Setup

1. Install Git, Python 3.10+ with `venv` and `pip`, and Android SDK Platform-Tools. Put `adb` on `PATH` or set `ADB_PATH` to the path of the executable.
2. Connect one rooted Android device by USB. Enable USB debugging, unlock the device and approve the authorization prompt. Google Play Store and Google One must be installed. Sign in to the intended Google Play account on the device.
3. From a toolkit checkout that includes the Linux launcher, run:

   ```sh
   adb devices
   sh run-linux.sh
   ```

The launcher installs pinned Textual and Frida 16.5.9 into a local `.venv`. It opens the dashboard without starting a stage.

| Command | Behavior |
| --- | --- |
| `sh run-linux.sh --check` | Runs Step 0 environment setup and diagnostics. |
| `sh run-linux.sh --list` | Runs Step 1 offer listing. Android preparation can still change settings. |
| `sh run-linux.sh --step 3` | Opens Advanced controls with Step 3 selected. Steps 0–5 can be preselected. |
| `sh run-linux.sh --sequence` | Opens guided controls starting at Step 2. Add it after `--step N` to choose a starting step. Guided checkout accepts Steps 2–5. |

**Steps 2–5 may attempt real charges.** Each checkout requires its own approval, a verified current Google Play account and a fresh exact offer with a zero-priced first phase. Verify the subscription and renewal date in Google Play before continuing a sequence. Offer metadata alone cannot establish eligibility or renewal terms.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| ADB missing | Install Platform-Tools, update `PATH` or set `ADB_PATH` to the executable. When only `ADB_PATH` is set, run that executable with `devices` to check the connection. |
| `unauthorized` | Unlock the phone and approve the USB debugging prompt. Check for status `device`. |
| No device or USB permissions error | Reconnect with a data cable, check USB debugging, and verify Ubuntu's Android USB device rules and access for your user. |
| Multiple devices | Disconnect extra devices and retry. |
| Virtual environment error | Install `python3-venv` or its version-specific equivalent and check that the checkout is writable. If an existing `.venv` belongs to another host or is unusable, move it aside and rerun the launcher. |
| Frida or Android stage failure | Check the dashboard's technical details and device state. Confirm compatibility of Frida 16.5.9 with the Android build before repeating a stage. |
| Offer or account check fails | Open Google One and Google Play on Android and check the selected profile. If the device became unstable, stop testing and review the Android/Frida setup before proceeding. |

## Validation status

Offline tests cover the launcher and dashboard with Python 3.11 and 3.13, including mocked checkout paths. End-to-end Steps 0–1 on a rooted USB phone remain pending. A live checkout is a separate release gate.
