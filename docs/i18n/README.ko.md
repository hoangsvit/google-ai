# ePlus AI Toolkit — 한국어

[← Short overview](../../README.ko.md) · [Documentation home](../README.md) · [English user guide](../USAGE.md)

[English](../../README.md) · [Tiếng Việt](../../README.vi.md) · [简体中文](../../README.zh-CN.md) · [日本語](../../README.ja.md) · **한국어** · [Español](../../README.es.md) · [Français](../../README.fr.md)

**macOS 미리보기:** [Mac 버전](../../docs/MACOS-PREVIEW.md)은 0–5단계 전체 흐름을 구현했습니다. 결제 2–5단계는 실제 요금이 발생할 수 있으므로 단계별 확인이 필요합니다. 실제 Mac/MuMu에서 결제 호환성은 아직 검증되지 않았습니다.

> **기준 문서:** [영어 README](../../README.md). 이 번역은 주요 사용법과 주의사항을 설명합니다. 내용이 다르면 최신 소스 코드와 영어 README를 확인하세요.

**ePlus AI Toolkit**은 주로 **Windows**에서 사용하는 터미널 도구입니다. **PowerShell, Python, ADB, Frida, Android 에뮬레이터(MuMuPlayer)**를 통해 Google One / Google Play의 Google AI Pro 프로모션 정보를 확인합니다. Textual UI와 CLI는 같은 실행 엔진을 사용합니다.

![ePlus AI Toolkit 화면](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **비공식 도구이며 실제 요금이 청구될 수 있습니다.** **Step 2–5**는 실제 Google Play 결제 화면을 열고 상황에 따라 **Subscribe(구독)**를 자동으로 누를 수 있습니다. 프로모션이 표시되거나 첫 결제 금액이 0이거나 결제 요청 메시지가 나타나더라도 **프로모션 적용, 무료 구독, 구독 활성화, 기간 연장이 확인된 것은 아닙니다**. 실행 전에 Google Play에서 계정, 오늘의 결제 금액, 이후 요금과 갱신일을 확인해야 합니다. 도구를 중지해도 이미 제출한 거래는 취소되지 않습니다.

> [!NOTE]
> **Google Play 결제 금액이 0달러로 표시되어도 카드 확인을 위해 금액이 일시적으로 묶일 수 있습니다.** 카드 명세서에 **약 미화 3달러**(다른 금액일 수도 있음)의 **승인 보류**가 표시될 수 있습니다. **3달러는 예시일 뿐 Google의 고정 수수료나 확정된 구독 청구액이 아닙니다.** 보류 금액만큼 사용 가능 잔액이 일시적으로 줄 수 있습니다. Google에 따르면 이러한 승인은 구매 대금이 아니며 은행에 따라 보통 **영업일 기준 1~14일** 내 해제됩니다. 실제 청구로 확정되었거나 14영업일 이후에도 보류가 남아 있다면 카드 발급사 및 Google Payments에 문의하세요. [Google Play 공식 안내](https://support.google.com/googleplay/answer/6224192?hl=en).

## 면책 고지

이 프로젝트는 Google, Google One, Google Play, NetEase, MuMuPlayer와 **제휴·후원·승인 관계가 없는 독립 비공식 도구**입니다. 소프트웨어는 **있는 그대로** 제공되며 프로모션 자격, 결제 결과, 에뮬레이터 호환성을 보장하지 않습니다. 본인이 소유하거나 사용 권한이 있는 장치 및 계정에서만 사용하고, 법률과 플랫폼 약관을 준수하세요. [전체 면책 고지(영어)](../../DISCLAIMER.md)와 [보안 안내](../../SECURITY.md)를 참고하세요.

## 1. 준비 사항

- **Windows**, PowerShell **5.1+**, Python **3.10+**.
- **MuMuPlayer를 별도로 설치**하고 Android 인스턴스에서 root 및 ADB 디버깅을 활성화합니다.
- Android에 **Google Play Store**와 **Google One**을 설치하고 대상 Google 계정으로 로그인합니다.
- 도구는 필요하면 **Android SDK Platform-Tools(ADB)**와 **Frida 16.5.9**를 찾아 설치/준비할 수 있지만 **MuMuPlayer 자체를 자동으로 설치하지 않습니다**. Frida 호환성은 Android 버전에 따라 달라집니다.

**MuMuPlayer 공식 다운로드:** [mumuplayer.com/download](https://www.mumuplayer.com/download/)에서 Windows 버전을 선택하세요. 비공식 미러는 피하세요. 추가 설명: [설치 Wiki](https://github.com/hoangsvit/google-ai/wiki/Install).

## 2. 설치 및 실행

PowerShell에서 실행:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

이미 저장소를 다운로드했다면:

```powershell
git pull --ff-only
.\run-all.ps1
```

**인자 없이 실행**하면 Textual 대시보드가 열리고 결제는 자동으로 시작되지 않습니다. 필요한 경우 Textual, ADB, Frida를 준비합니다. 일반적으로 `setup_env.py`를 미리 실행할 필요가 없습니다. 초기 준비 과정은 에뮬레이터, 프록시 또는 네트워크 설정을 변경할 수 있습니다.

ADB가 PATH에 있다면 연결 확인:

```powershell
adb devices
```

장치 상태가 `device`여야 하며 `offline`이나 `unauthorized`이면 안 됩니다. 문제 해결은 [상세 가이드](../../docs/DETAILED-GUIDE.md)를 참고하세요.

### 대안: 최신 소스에서 오류가 발생하면 릴리스 버전 사용

최신 소스 코드 실행 중 오류가 발생한다면 [GitHub Releases](https://github.com/hoangsvit/google-ai/releases)에서 **공개된 릴리스 버전**을 사용해 볼 수 있습니다. 릴리스 노트를 확인하고 Windows용 첨부 파일이 있는 경우 해당 파일을 받으세요. GitHub에서 자동 제공하는 **Source code (zip)**만 있다면 ZIP을 다운로드하고 압축을 푼 다음, 해당 폴더에서 PowerShell을 열어 실행하세요.

```powershell
.\run-all.ps1
```

**Source code (zip)은 미리 빌드된 `.exe`나 설치 프로그램이 아닙니다.** 기존 소스 폴더를 덮어쓰지 말고 **별도 폴더**에 보관하세요. 이전 릴리스에는 최신 버그 수정이 빠져 있을 수 있습니다. Windows, Python, MuMuPlayer, ADB/Frida와 결제 관련 주의사항은 여전히 필요합니다. 문제가 계속되면 [문제 해결 가이드](../../docs/DETAILED-GUIDE.md) 또는 [Issues](https://github.com/hoangsvit/google-ai/issues)를 확인하세요.

## 3. 대시보드 사용법

**Check Device & Offers**는 **Step 1 — Available offers**를 실행하여 프로모션을 조회합니다. **구독 결제를 시작하지 않습니다**. **Live Status**와 **Show technical details**에서 진행 상황을 확인하세요. 30초 동안 로그가 없다는 경고는 반드시 프로그램이 멈췄다는 뜻이 아닙니다.

**Advanced: Run by step** 모드:

| 모드 | 기능 |
| --- | --- |
| **One step only** | 선택한 Step 0–5 하나만 실행 |
| **From selected step** | 선택한 Step 2–5부터 안내형 시퀀스 시작 |
| **All: Steps 2–5** | Step 2부터 시퀀스 시작. Step 5는 선택 사항 |

| Step | 기능 | 위험 |
| --- | --- | --- |
| **0 — Environment** | Android / ADB / Frida 점검과 준비 | 결제 없음. 환경 설정은 변경될 수 있음 |
| **1 — Available offers** | Google Play 프로모션 조회 | 결제 없음. 사전 점검 중 환경 변경 가능 |
| **2 — Pro 12 months** | 기존 12개월 프로모션 단계 | **실제 결제 가능** |
| **3 — Pro +6 months** | 구독 변경 시도 | **실제 결제 가능** |
| **4 — Pro +6 months (second)** | 두 번째 구독 변경 시도 | **실제 결제 가능** |
| **5 — Optional +6 months** | 선택적 변경 시도 | **실제 결제 가능** |

표시된 개월 수는 **이전 워크플로의 단계 이름**이며 실제 구독 기간 연장을 보장하지 않습니다. 이미 활성 구독이 있다면 **Step 2를 다시 실행하지 마세요**.

TUI에서 **각 결제 단계는 별도 승인이 필요합니다**. 도구가 결제 제출을 시도했다고 표시해도 [Google Play 구독 관리](https://play.google.com/store/account/subscriptions)에서 실제 구독, 요금과 갱신일을 확인하세요. 직접 변경 사항을 확인한 경우에만 **Verified in Google Play → Next**를 선택하세요. 도구는 구독 성공을 독립적으로 증명할 수 없습니다.

**중지/종료:** Step 0–1에서는 Stop이 로컬 검사를 종료하도록 요청합니다. Step 2–5의 **Stop after this step**은 이후 단계를 막을 뿐 **진행 중인 결제를 강제 종료하지 않습니다**. 결제 중 **Q / Exit**는 현재 단계 종료 후 종료합니다. **D**는 기술 로그, **R**은 선택한 모드 실행입니다.

## 4. PowerShell CLI (고급)

**조회/진단(구독 결제 없음):**

```powershell
.\run-all.ps1 -Step 1
.\run-all.ps1 -Step 1 -Debug
.\run-all.ps1 -Step 0
.\run-all.ps1 -Cli
```

**다음 명령은 실제 결제를 시작할 수 있습니다:**

```powershell
.\run-all.ps1 -Step 2
.\run-all.ps1 -Step 3
.\run-all.ps1 -Step 4
.\run-all.ps1 -Step 5
```

TUI와 달리 단독 `-Step 2..5` 명령은 **PowerShell에서 별도의 승인 질문을 표시하지 않습니다**. 실제 결제를 의도하고 조건을 확인한 경우에만 실행하세요.

확인 절차가 있는 CLI 시퀀스:

```powershell
.\run-all.ps1 -AllStages
.\run-all.ps1 -AllStages -StartStep 3
```

CLI 선택: **1 = Continue(계속), 2 = End run(종료), 0 = Stop(중지)**. 각 단계마다 Google Play에서 직접 결과를 검증하세요. `-StartStep 3`은 이전 단계가 성공했다는 증거가 아닙니다.

장치/계정 선택:

```powershell
.\run-all.ps1 -Step 1 -Serial emulator-5554
.\run-all.ps1 -AllStages -Email "account@gmail.com"
```

ADB에서 실제로 표시되는 시리얼만 사용하세요. `-Force`는 계정 일치 확인을 건너뛰므로 **권장하지 않습니다**. 프로모션 자격이나 Google 결제 제한을 우회하지는 못합니다.

## 5. 결과와 문제 해결

- **MuMu/ADB가 감지되지 않음:** 에뮬레이터 실행, root/ADB 권한 및 장치 상태를 확인하세요.
- **Frida 오류:** 로그와 **16.5.9** / Android 호환성을 확인하세요.
- **프로모션이 없음:** Google One / Play Store를 열고 **Step 1**을 다시 실행하세요.
- **계정 불일치:** Play Store 프로필을 확인하고 검증을 우회하지 마세요.
- **결제 제출 시도:** 구독 성공과 다릅니다. 재시도 전에 Google Play에서 상태를 확인하세요.
- **결제 보안 오류(예: OR-REH-04):** 결제 단계를 중단하고 공식 보안 절차를 확인하세요.

로그는 `logs/`, 보고서는 `ultra0-report/`에 저장됩니다. **계정 정보, 토큰, 결제 정보를 포함한 원본 파일을 공유하지 마세요.** CI는 정적/모의 테스트만 수행하며 실제 결제 성공을 검증하지 않습니다. **macOS 전체 지원은 아직 없습니다.**

## 커뮤니티 지원 및 관련 프로젝트

ePlus AI Toolkit 설치나 사용에 문제가 있다면 [ePlus Telegram 지원·토론 게시물](https://t.me/eplus_news/29)에서 커뮤니티와 연락하고 해결 방법을 공유할 수 있습니다. 재현 가능한 버그는 [GitHub Issue](https://github.com/hoangsvit/google-ai/issues)로도 제보해 주세요. **비밀번호, OTP/2FA 코드, 오퍼/구매 토큰, 개인정보가 포함된 원본 로그, 카드 정보를 공개하지 마세요.** Google 공식 지원 채널은 아닙니다.

**Google AI Pro 프로모션에 참여할 수 없나요?** 별도의 ePlus.DEV 커뮤니티 프로젝트인 [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub)에서 [Muse 초대 코드를 찾거나 공유](https://muse.eplus.dev/)할 수 있습니다. **Muse는 별도 서비스**이며 초대 코드로 **Google AI Pro 구독을 활성화하거나 대신할 수 없습니다**. 코드 이용 가능 여부 및 지역·계정 자격은 보장되지 않습니다.

## 문서와 기여자

[영어 README](../../README.md) · [설치 Wiki](https://github.com/hoangsvit/google-ai/wiki/Install) · [상세 가이드](../../docs/DETAILED-GUIDE.md) · [원본 단계](../../docs/ORIGINAL-STEPS.md) · [면책 고지](../../DISCLAIMER.md) · [보안](../../SECURITY.md) · [기여](../../CONTRIBUTING.md) · [저작권 고지](../../THIRD_PARTY_NOTICES.md)

**원저자:** [@gylive](https://github.com/gylive) — [google-ultra](https://github.com/gylive/google-ultra). **관리자:** [David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev). 원본 MIT 저작권 고지는 `THIRD_PARTY_NOTICES.md`에 보존되어 있습니다.
