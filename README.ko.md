# ePlus AI Toolkit — 한국어

[English](README.md) · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · **한국어** · [Español](README.es.md) · [Français](README.fr.md)

Android, ADB, Frida, Google Play를 통해 Google AI Pro 혜택을 확인하는 비공식 터미널 도구입니다. Windows는 유지 관리되는 안정 버전이며, macOS 0–5단계 버전은 `dev`에서 개발 중입니다.

![ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **실제 비용이 발생할 수 있습니다.** **2–5단계**는 Google Play 결제를 열고 Subscribe를 자동 실행할 수 있습니다. 혜택 표시나 첫 결제 금액 0은 무료 이용, 구독 활성화 또는 기간 연장을 입증하지 않습니다. Google Play에서 계정, 당일 결제액, 갱신 가격과 날짜를 직접 확인하세요. 환경 점검 시 Android/Frida/네트워크 설정이 변경될 수도 있습니다.

## Quick start

**Windows:** [MuMuPlayer](https://www.mumuplayer.com/download/)를 별도 설치하고 ADB/root 및 Google Play/Google One을 준비한 후 PowerShell에서 실행:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

**macOS 개발 버전:** Python 3.10+, ADB, 루팅 가능한 Android가 필요합니다. 실제 Mac/MuMu 결제 호환성은 검증되지 않았습니다:

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
git switch dev
sh run-macos.sh
```

## Documentation

[한국어 상세 안내](docs/i18n/README.ko.md) · [문서 모음](docs/README.md) · [설치](docs/INSTALLATION.md) · [Mac 가이드](docs/MACOS-PREVIEW.md) · [결제 안전](docs/SAFETY.md)

[릴리스](https://github.com/hoangsvit/google-ai/releases) · [이슈 제보](https://github.com/hoangsvit/google-ai/issues) · [기여](CONTRIBUTING.md) · [보안](SECURITY.md) · [면책조항](DISCLAIMER.md)

Original: [gylive/google-ultra](https://github.com/gylive/google-ultra). Maintainer: [@hoangsvit](https://github.com/hoangsvit) · [ePlus.DEV](https://eplus.dev). Not affiliated with Google or MuMuPlayer.
