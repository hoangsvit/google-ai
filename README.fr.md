# ePlus AI Toolkit — Français

[English](README.md) · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · **Français**

Outil de terminal **non officiel** pour consulter les offres Google AI Pro sur Android avec ADB, Frida et Google Play. Windows est la version stable ; le port macOS comprenant les étapes 0–5 est développé sur `dev`.

![ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **Des frais réels peuvent être engagés.** Les **étapes 2–5** peuvent ouvrir le paiement Google Play et appuyer automatiquement sur Subscribe. Une offre affichée ou un prix initial nul **ne prouvent pas** la gratuité, l'activation ou la prolongation. Vérifiez le compte, le prix du jour, les tarifs futurs et la date de renouvellement dans Google Play. La configuration peut aussi modifier Android, Frida ou le réseau.

## Quick start

**Windows :** installez [MuMuPlayer](https://www.mumuplayer.com/download/) séparément, préparez ADB/root et Google Play/Google One, puis lancez PowerShell :

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

**macOS en développement :** nécessite Python 3.10+, ADB et Android avec root. Le paiement n'a pas été vérifié sur un véritable Mac/MuMu :

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
git switch dev
sh run-macos.sh
```

## Documentation

[Guide complet en français](docs/i18n/README.fr.md) · [Centre de documentation](docs/README.md) · [Installation](docs/INSTALLATION.md) · [Guide Mac](docs/MACOS-PREVIEW.md) · [Sécurité des paiements](docs/SAFETY.md)

[Versions](https://github.com/hoangsvit/google-ai/releases) · [Signaler un bug](https://github.com/hoangsvit/google-ai/issues) · [Contribuer](CONTRIBUTING.md) · [Sécurité](SECURITY.md) · [Avertissement](DISCLAIMER.md)

Original: [gylive/google-ultra](https://github.com/gylive/google-ultra). Maintainer: [@hoangsvit](https://github.com/hoangsvit) · [ePlus.DEV](https://eplus.dev). Not affiliated with Google or MuMuPlayer.
