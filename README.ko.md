# ePlus AI Toolkit — 한국어

[English](README.md) · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · **한국어** · [Español](README.es.md) · [Français](README.fr.md)

Android, ADB, Frida, Google Play를 통해 Google AI Pro 혜택을 확인하는 비공식 터미널 도구입니다. Windows와 macOS 모두 실행 방법을 제공합니다. Mac 버전은 0–5단계를 구현했지만 실제 기기 결제는 아직 검증되지 않았습니다.

![ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **실제 비용이 발생할 수 있습니다.** **2–5단계**는 Google Play 결제를 열고 Subscribe를 자동 실행할 수 있습니다. 혜택 표시나 첫 결제 금액 0은 무료 이용, 구독 활성화 또는 기간 연장을 입증하지 않습니다. Google Play에서 계정, 당일 결제액, 갱신 가격과 날짜를 직접 확인하세요. 환경 점검 시 Android/Frida/네트워크 설정이 변경될 수도 있습니다.

## Windows 설치

1. **Python 3.10+**, **Git**, PowerShell 5.1+, [Windows용 MuMuPlayer](https://www.mumuplayer.com/download/)를 설치합니다.
2. Android 인스턴스를 실행하고 **root/ADB 디버깅**을 켠 뒤 **Google Play Store**와 **Google One**에 로그인합니다.
3. **PowerShell**을 열어 실행:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

## macOS 설치

1. **Python 3.10+**, **Git**, **Android SDK Platform-Tools (ADB)**를 설치합니다. Homebrew 사용 시 `brew install android-platform-tools`.
2. 루팅된 Android 기기 또는 Google Play Store/Google One이 있는 호환 에뮬레이터를 연결합니다. Mac용 **MuMuPlayer Pro는 Apple Silicon 전용**입니다. Intel Mac은 다른 Android 환경이 필요합니다.
3. **Terminal**에서 실행:

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
sh run-macos.sh
```

Mac 실행 스크립트는 `.venv`에 Python 종속성을 설치합니다. 0–5단계를 구현했지만 **실제 Mac/MuMu의 결제는 검증되지 않았습니다**. [Mac 설치 안내](docs/MACOS-PREVIEW.md)를 참고하세요.

## 첫 실행 (Windows 및 Mac 공통)

**Check Device & Offers**로 혜택을 확인하세요(1단계, 결제 없음). 0단계는 ADB/Frida/Android 설정을 변경할 수 있습니다. **2–5단계는 실제 요금이 청구될 수 있으므로** Google Play 조건을 확인하세요.

## 문서

[한국어 상세 안내](docs/i18n/README.ko.md) · [문서 모음](docs/README.md) · [설치](docs/INSTALLATION.md) · [Mac 가이드](docs/MACOS-PREVIEW.md) · [결제 안전](docs/SAFETY.md)

[릴리스](https://github.com/hoangsvit/google-ai/releases) · [이슈 제보](https://github.com/hoangsvit/google-ai/issues) · [기여](CONTRIBUTING.md) · [보안](SECURITY.md) · [면책조항](DISCLAIMER.md)

Original: [gylive/google-ultra](https://github.com/gylive/google-ultra). Maintainer: [@hoangsvit](https://github.com/hoangsvit) · [ePlus.DEV](https://eplus.dev). Not affiliated with Google or MuMuPlayer.
