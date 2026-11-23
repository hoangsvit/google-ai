# Installation and first run (Windows)

[Documentation home](README.md) · [Repository README](../README.md) · [Safety](SAFETY.md)

## Install and prepare

**This guide is for Windows only.** Use **PowerShell**, not the macOS Terminal launcher. macOS users should follow the [separate Mac prerequisites and setup guide](MACOS-PREVIEW.md) instead; macOS does **not** need PowerShell. For Ubuntu and a rooted USB phone, use the [Linux setup guide](LINUX.md).

### Requirements

- **Windows** with PowerShell **5.1+**, **Python 3.10+** and **Git**.
- **MuMuPlayer installed separately**, started with an Android instance that permits root and ADB access.
- **Google Play Store** and **Google One** installed and signed into the intended Google account inside Android.
- A connection to Android through ADB. The toolkit can locate or download **Android SDK Platform-Tools** when ADB is missing; it does **not** install the Android emulator.
- A compatible **Frida 16.5.9** host/device environment. The setup helper can prepare Frida, but compatibility depends on the emulator and Android version.

### Step 1 — Install MuMuPlayer

**MuMuPlayer is neither included in this repository nor automatically downloaded by the toolkit.**

Download it from the **[official MuMuPlayer website (NetEase)](https://www.mumuplayer.com/download/)**, choose the Windows edition, and install it yourself. Avoid third-party download mirrors.

Start MuMuPlayer, enable root and ADB debugging for the Android instance, and ensure Google Play Store and Google One are available. Sign into the Google account you intend to check.

For illustrated setup instructions, use the **[Install guide on this project's GitHub Wiki](https://github.com/hoangsvit/google-ai/wiki/Install)**.

### Step 2 — Get the toolkit

Open **PowerShell** in the folder where you want to install the toolkit:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

If you already cloned the repository, update it before starting:

```powershell
git pull --ff-only
.\run-all.ps1
```

The no-argument command opens the Textual dashboard, installing its pinned dependency on first launch if needed. When you run a check, the environment helper can also install or locate ADB and the pinned Frida version. **You generally do not need to execute `setup_env.py` manually first.** Environment preparation may install tools or adjust Android/Frida/emulator settings.

If the terminal shows an ADB error, confirm that MuMu is running and Android debugging is enabled. Where ADB is on your PATH, you can verify the connection with:

```powershell
adb devices
```

The device must show as `device`, not `offline` or `unauthorized`. If ADB is not on PATH, let the toolkit locate/install Platform-Tools or follow the [detailed troubleshooting guide](DETAILED-GUIDE.md).

### Alternative: use a published release if the latest source fails

If you encounter errors when running the latest repository version, you can try a **previously published release** from [GitHub Releases](https://github.com/hoangsvit/google-ai/releases). Open a release, read its notes, and download the available Windows package **if one is attached**. If the release only provides GitHub's automatic **Source code (zip)** archive, download and extract that ZIP, open PowerShell in the extracted folder, and run:

```powershell
.\run-all.ps1
```

A **source ZIP is not a prebuilt `.exe` or installer**. Keep the release in a **separate folder** from your current clone so you can compare versions and roll back without overwriting files. Release builds may lack newer bug fixes, and they still require Windows, Python, MuMuPlayer, ADB/Frida and the same billing precautions. If the error persists, check [Troubleshooting](TROUBLESHOOTING.md) or [report an issue](https://github.com/hoangsvit/google-ai/issues).
