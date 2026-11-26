# Windows-native iOS research (ASoftware)

The preferred Windows research backend does not need WSL2. The reviewed upstream reference is [ASoftware v0.3.1](https://github.com/alpersamur3/asoft-ios/releases/tag/v0.3.1). Its iOS 26 installer uses a small Linux helper VM to prepare firmware, then runs QEMU natively on Windows. This is not a working Google AI billing integration.

## Requirements and release

Windows 10 2004+ or Windows 11 (64-bit); upstream recommends 16 GB RAM, 8 logical processors, about 50 GB free during installation and a recent Vulkan 1.2 driver with VK_EXT_external_memory_host. NVIDIA was tested upstream; Intel/AMD compatibility is not established for every GPU. The toolkit does not independently validate Vulkan; use the upstream check. Review the upstream firmware licensing and unsigned binaries before use.

From the repository root, using PowerShell and Python 3.10+:

```powershell
python -m research.ios_asoft release
python -m research.ios_asoft diagnose --install-dir D:\ASoftware
```

Download the specific win64 release archive and SHA256SUMS.txt from the release page. Compare the archive to the corresponding published digest (a checksum is not a signature). Verify before extraction; do not run an untrusted archive.

```powershell
python -m research.ios_asoft verify .\ASoftware-iOS-0.3.1-win64.zip --sha256 YOUR_64_HEX_DIGEST
```

After extracting the verified package into a reviewed local folder:

```powershell
python -m research.ios_asoft install --package-dir D:\ASoftPackage --install-dir D:\ASoftware --check
python -m research.ios_asoft install --package-dir D:\ASoftPackage --install-dir D:\ASoftware --check --execute
python -m research.ios_asoft install --package-dir D:\ASoftPackage --install-dir D:\ASoftware --execute
python -m research.ios_asoft launch --install-dir D:\ASoftware --execute
```

The wrapper previews commands by default, explicitly selects ios26, helper and nowsl, leaves upstream prompts intact and does not change PowerShell execution policy. If policy blocks the script, use the reviewed upstream release installer according to its documentation; do not disable security controls. Confirm the installer shows the no-WSL path before proceeding. The toolkit does not download, extract or install anything automatically. Launch opens the upstream GUI; select Start and use its own controls for shutdown/snapshots. A launcher exit or executable presence is not proof of a functioning VM. The installed executable path must be checked on the actual installation.

## Acceptance checklist

| Gate | Evidence | Status |
| --- | --- | --- |
| Windows and resources | Diagnose and upstream check | Prototype |
| Firmware preparation | Successful upstream no-WSL install | Unverified |
| Boot and UI | Start from upstream launcher, inspect Home | Unverified |
| Networking | Open a normal public page in Safari | Unverified |
| App installation | Install an owned, authorized test app using supported mechanism | Unverified |
| Google App and sign-in | Legitimate app availability, normal sign-in on supported device | Unverified |
| Apple Account / App Store | Upstream explicitly reports not working | Blocked upstream |
| StoreKit | Supported development app in official StoreKit Testing environment | Unverified |
| SKU report | Existing offline importer, authorized or synthetic data | Prototype |

Upstream only documents installation of compatible decrypted IPA files. This project does not provide third-party IPAs, decryption instructions, account spoofing, certificate injection, response rewriting or payment automation. Do not sign in with important accounts on a research VM whose security controls differ from a real iPhone. Google Play is Android-only. Google App/StoreKit compatibility cannot be inferred from a working Safari or installed test app.

## Testing

```powershell
python -m unittest discover -s tests -p "test_ios*.py" -v
```

Tests are offline and mock execution; no firmware download or real iOS device is required. Linux/WSL2 remains an optional separate backend documented in [ios-automation.md](ios-automation.md).
