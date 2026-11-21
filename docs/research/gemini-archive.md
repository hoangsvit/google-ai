# Gemini.zip research notes

The supplied archive is 75,690,075 bytes. Its SHA-256 digest is `a7281874f6d82ba5a4ef5295240f18a5bbf22caf097237bda32a052d4beae7fa`.

The bundled README describes an Android instrumentation tool that interacts with the Google One subscription picker on a rooted device. It says the user confirms the transaction in Google Play. These behavioral claims come from the README. This review examined the archive offline without executing its programs or testing a transaction.

## Inventory

| Archive entry | Uncompressed bytes | SHA-256 |
|---|---:|---|
| `assets/frida-server-17.9.1-android-x86_64` | 110,787,848 | `fd677533f1215654308e06db3c34905ed6a456a39343696b2f38ead09415884d` |
| `assets/frida-server-17.9.1-android-x86_64.xz` | 31,614,892 | `f5f1205ffb3cb145de9264a8c6aa7aa8724a2e33df319d476f2ef67cac453c5f` |
| `frida.js` | 20,404 | `c7c420240f1b750dd0e39537757c30e7e33abf1904e7ea9d7c6747db8e335494` |
| `main.py` | 29,538 | `5e466a3a39f61c97036566c95fb97fe6c2e0cba759bbe028e77b273e305c2761` |
| `module_b64.py` | 150,842 | `060940f2ec63af90005475da2c56981048b143bb8a2cacbbd6598d4e30039ecb` |
| `README.md` | 2,204 | `e44ed47f0d91ecd5d1a67011a86ba4ffad30910ad13bcad5363023f0c9e133b6` |
| `requirements.txt` | 36 | `2c465ce8aaec8f4490194a7f25dbe2e2024057f0c6f14eaf4ce4ce8a952892b8` |

## Findings

- Decompressing the XZ entry produced the same SHA-256 digest as the standalone server. Both entries represent the same binary.
- The bundled server filename indicates Frida 17.9.1 for Android x86_64. The Python requirements specify lower bounds of `frida>=17.9.1` and `frida-tools>=14.8.1`, so they permit later releases.
- The hashes identify this sample for future comparisons. The publisher and upstream provenance of the bundled binaries remain unverified.
