# ePlus AI Toolkit — Tiếng Việt

[English](README.md) · **Tiếng Việt** · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md)

Bộ công cụ terminal **không chính thức** để kiểm tra ưu đãi Google AI Pro trên Android bằng ADB, Frida và Google Play. Windows và macOS có hướng dẫn cài đặt riêng. Bản Mac có Steps 0–5 nhưng chưa xác minh thanh toán trên thiết bị thực tế.

![ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **Có thể phát sinh phí thật.** Steps **2–5** có thể mở thanh toán Google Play và tự nhấn Subscribe. Thấy ưu đãi hoặc giá ban đầu 0 **không chứng minh** được miễn phí, kích hoạt hay gia hạn thành công. Hãy tự kiểm tra tài khoản, giá hôm nay, giá gia hạn và ngày thanh toán trên Google Play. Cài đặt môi trường cũng có thể thay đổi Android/Frida/network.

## Cài đặt trên Windows

1. Cài **Python 3.10+**, **Git**, PowerShell 5.1+ và [MuMuPlayer cho Windows](https://www.mumuplayer.com/download/).
2. Mở máy Android trong MuMu, bật **root/ADB debugging** và đăng nhập **Google Play Store** cùng **Google One**.
3. Mở **PowerShell** rồi chạy:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

## Cài đặt trên macOS

1. Cài **Python 3.10+**, **Git** và **Android SDK Platform-Tools (ADB)**. Nếu có Homebrew, chạy `brew install android-platform-tools`.
2. Kết nối thiết bị Android có root, Google Play Store và Google One, hoặc trình giả lập tương thích. **MuMuPlayer Pro trên Mac hỗ trợ Apple Silicon**; Mac Intel cần thiết bị/giả lập Android khác.
3. Mở **Terminal** rồi chạy:

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
sh run-macos.sh
```

Launcher Mac tự cài thư viện Python vào `.venv`. Đã có code cho Steps 0–5 nhưng **chưa xác minh thanh toán trên Mac/MuMu thật**. Xem [hướng dẫn cài đặt Mac](docs/MACOS-PREVIEW.md).

## Sử dụng lần đầu (cả hai hệ điều hành)

Chọn **Check Device & Offers** để xem ưu đãi (Step 1, không checkout). Step 0 có thể thay đổi cấu hình ADB/Frida/Android. **Steps 2–5 có thể thanh toán thật**, cần kiểm tra điều khoản trực tiếp trong Google Play.

## Tài liệu

[Hướng dẫn đầy đủ tiếng Việt](docs/i18n/README.vi.md) · [Trung tâm tài liệu](docs/README.md) · [Cài đặt](docs/INSTALLATION.md) · [Hướng dẫn Mac](docs/MACOS-PREVIEW.md) · [An toàn thanh toán](docs/SAFETY.md)

[Bản phát hành](https://github.com/hoangsvit/google-ai/releases) · [Báo lỗi](https://github.com/hoangsvit/google-ai/issues) · [Đóng góp](CONTRIBUTING.md) · [Bảo mật](SECURITY.md) · [Miễn trừ trách nhiệm](DISCLAIMER.md)

Original: [gylive/google-ultra](https://github.com/gylive/google-ultra). Maintainer: [@hoangsvit](https://github.com/hoangsvit) · [ePlus.DEV](https://eplus.dev). Not affiliated with Google or MuMuPlayer.
