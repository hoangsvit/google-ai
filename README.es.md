# ePlus AI Toolkit — Español

[English](README.md) · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · **Español** · [Français](README.fr.md)

Herramienta de terminal **no oficial** para consultar ofertas de Google AI Pro en Android con ADB, Frida y Google Play. Windows es la versión estable; el puerto macOS con pasos 0–5 está en desarrollo en `dev`.

![ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **Pueden producirse cargos reales.** Los **pasos 2–5** pueden abrir el pago de Google Play y pulsar Subscribe automáticamente. Una oferta o un importe inicial de 0 **no demuestran** gratuidad, activación ni renovación. Revisa la cuenta, el cobro de hoy, los precios futuros y la fecha de renovación directamente en Google Play. La preparación puede alterar Android/Frida/red.

## Quick start

**Windows:** instala [MuMuPlayer](https://www.mumuplayer.com/download/) por separado, configura ADB/root y Google Play/Google One y ejecuta PowerShell:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

**macOS en desarrollo:** requiere Python 3.10+, ADB y Android con root. Los pagos reales no se han verificado con Mac/MuMu:

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
git switch dev
sh run-macos.sh
```

## Documentation

[Guía completa en español](docs/i18n/README.es.md) · [Centro de documentación](docs/README.md) · [Instalación](docs/INSTALLATION.md) · [Guía para Mac](docs/MACOS-PREVIEW.md) · [Seguridad de pagos](docs/SAFETY.md)

[Versiones](https://github.com/hoangsvit/google-ai/releases) · [Informar de un problema](https://github.com/hoangsvit/google-ai/issues) · [Contribuir](CONTRIBUTING.md) · [Seguridad](SECURITY.md) · [Aviso legal](DISCLAIMER.md)

Original: [gylive/google-ultra](https://github.com/gylive/google-ultra). Maintainer: [@hoangsvit](https://github.com/hoangsvit) · [ePlus.DEV](https://eplus.dev). Not affiliated with Google or MuMuPlayer.
