# ePlus AI Toolkit — Français

[English](README.md) · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · **Français**

Outil de terminal **non officiel** pour consulter les offres Google AI Pro sur Android avec ADB, Frida et Google Play. Windows est la version stable ; le port macOS comprenant les étapes 0–5 est développé sur `dev`.

![ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **Des frais réels peuvent être engagés.** Les **étapes 2–5** peuvent ouvrir le paiement Google Play et appuyer automatiquement sur Subscribe. Une offre affichée ou un prix initial nul **ne prouvent pas** la gratuité, l'activation ou la prolongation. Vérifiez le compte, le prix du jour, les tarifs futurs et la date de renouvellement dans Google Play. La configuration peut aussi modifier Android, Frida ou le réseau.

## Installation sous Windows

1. Installez **Python 3.10+**, **Git**, PowerShell 5.1+ et [MuMuPlayer pour Windows](https://www.mumuplayer.com/download/).
2. Démarrez Android, activez **root et le débogage ADB**, puis connectez-vous à **Google Play Store** et **Google One**.
3. Ouvrez **PowerShell** et exécutez :

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

## Installation sous macOS

1. Installez **Python 3.10+**, **Git** et **Android SDK Platform-Tools (ADB)**. Avec Homebrew : `brew install android-platform-tools`.
2. Connectez un Android rooté avec Google Play Store/Google One ou un émulateur compatible. **MuMuPlayer Pro sur Mac nécessite Apple Silicon** ; les Mac Intel demandent une autre configuration Android.
3. Ouvrez le **Terminal** et exécutez :

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
sh run-macos.sh
```

Le lanceur crée `.venv`. Les étapes 0–5 sont implémentées, mais les paiements sur un **véritable Mac/MuMu restent non vérifiés**. Voir [le guide Mac](docs/MACOS-PREVIEW.md).

## Première utilisation (sur les deux systèmes)

Cliquez sur **Check Device & Offers** pour consulter les offres (étape 1, sans achat). L'étape 0 peut modifier ADB/Frida/Android. **Les étapes 2–5 peuvent entraîner des frais réels** ; vérifiez les conditions dans Google Play.

## Documentation

[Guide complet en français](docs/i18n/README.fr.md) · [Centre de documentation](docs/README.md) · [Installation](docs/INSTALLATION.md) · [Guide Mac](docs/MACOS-PREVIEW.md) · [Sécurité des paiements](docs/SAFETY.md)

[Versions](https://github.com/hoangsvit/google-ai/releases) · [Signaler un bug](https://github.com/hoangsvit/google-ai/issues) · [Contribuer](CONTRIBUTING.md) · [Sécurité](SECURITY.md) · [Avertissement](DISCLAIMER.md)

Original: [gylive/google-ultra](https://github.com/gylive/google-ultra). Maintainer: [@hoangsvit](https://github.com/hoangsvit) · [ePlus.DEV](https://eplus.dev). Not affiliated with Google or MuMuPlayer.
