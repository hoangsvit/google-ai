# ePlus AI Toolkit — Español

[English](README.md) · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · **Español** · [Français](README.fr.md)

Herramienta de terminal **no oficial** para consultar ofertas de Google AI Pro en Android con ADB, Frida y Google Play. Windows y macOS tienen instrucciones de instalación independientes. La versión Mac implementa los pasos 0–5, pero los pagos reales siguen sin verificarse.

![ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **Pueden producirse cargos reales.** Los **pasos 2–5** pueden abrir el pago de Google Play y pulsar Subscribe automáticamente. Una oferta o un importe inicial de 0 **no demuestran** gratuidad, activación ni renovación. Revisa la cuenta, el cobro de hoy, los precios futuros y la fecha de renovación directamente en Google Play. La preparación puede alterar Android/Frida/red.

## Instalar en Windows

1. Instala **Python 3.10+**, **Git**, PowerShell 5.1+ y [MuMuPlayer para Windows](https://www.mumuplayer.com/download/).
2. Inicia Android, activa **root y depuración ADB**, e inicia sesión en **Google Play Store** y **Google One**.
3. Abre **PowerShell** y ejecuta:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

## Instalar en macOS

1. Instala **Python 3.10+**, **Git** y **Android SDK Platform-Tools (ADB)**. Con Homebrew: `brew install android-platform-tools`.
2. Conecta un Android con root, Google Play Store y Google One, o un emulador compatible. **MuMuPlayer Pro para Mac requiere Apple Silicon**; un Mac Intel necesita otro entorno Android.
3. Abre **Terminal** y ejecuta:

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
sh run-macos.sh
```

El lanzador Mac instala las dependencias Python en `.venv`. Los pasos 0–5 están implementados, pero **los pagos no se han verificado en un Mac/MuMu real**. Consulta [la instalación para Mac](docs/MACOS-PREVIEW.md).

## Primer uso (ambos sistemas)

Pulsa **Check Device & Offers** para consultar ofertas (paso 1, sin pago). El paso 0 puede cambiar la configuración ADB/Frida/Android. **Los pasos 2–5 pueden generar cargos reales**: verifica las condiciones en Google Play.

## Documentación

[Guía completa en español](docs/i18n/README.es.md) · [Centro de documentación](docs/README.md) · [Instalación](docs/INSTALLATION.md) · [Guía para Mac](docs/MACOS-PREVIEW.md) · [Seguridad de pagos](docs/SAFETY.md)

[Versiones](https://github.com/hoangsvit/google-ai/releases) · [Informar de un problema](https://github.com/hoangsvit/google-ai/issues) · [Contribuir](CONTRIBUTING.md) · [Seguridad](SECURITY.md) · [Aviso legal](DISCLAIMER.md)

Original: [gylive/google-ultra](https://github.com/gylive/google-ultra). Maintainer: [@hoangsvit](https://github.com/hoangsvit) · [ePlus.DEV](https://eplus.dev). Not affiliated with Google or MuMuPlayer.
