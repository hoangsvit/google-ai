# ePlus AI Toolkit — Tiếng Việt

[English](README.md) · **Tiếng Việt** · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md)

Bộ công cụ terminal **không chính thức** để kiểm tra ưu đãi Google AI Pro trên Android bằng ADB, Frida và Google Play. Windows là bản phát hành ổn định; phiên bản macOS đủ Steps 0–5 đang phát triển trên `dev`.

![ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **Có thể phát sinh phí thật.** Steps **2–5** có thể mở thanh toán Google Play và tự nhấn Subscribe. Thấy ưu đãi hoặc giá ban đầu 0 **không chứng minh** được miễn phí, kích hoạt hay gia hạn thành công. Hãy tự kiểm tra tài khoản, giá hôm nay, giá gia hạn và ngày thanh toán trên Google Play. Cài đặt môi trường cũng có thể thay đổi Android/Frida/network.

## Quick start

**Windows:** cài [MuMuPlayer](https://www.mumuplayer.com/download/) riêng, bật ADB/root và đăng nhập Google Play/Google One; mở PowerShell:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

**macOS (bản phát triển):** cần Python 3.10+, ADB và thiết bị Android hỗ trợ root; chưa kiểm thử thanh toán với Mac/MuMu thực tế:

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
git switch dev
sh run-macos.sh
```

## Documentation

[Hướng dẫn đầy đủ tiếng Việt](docs/i18n/README.vi.md) · [Trung tâm tài liệu](docs/README.md) · [Cài đặt](docs/INSTALLATION.md) · [Hướng dẫn Mac](docs/MACOS-PREVIEW.md) · [An toàn thanh toán](docs/SAFETY.md)

[Bản phát hành](https://github.com/hoangsvit/google-ai/releases) · [Báo lỗi](https://github.com/hoangsvit/google-ai/issues) · [Đóng góp](CONTRIBUTING.md) · [Bảo mật](SECURITY.md) · [Miễn trừ trách nhiệm](DISCLAIMER.md)

Original: [gylive/google-ultra](https://github.com/gylive/google-ultra). Maintainer: [@hoangsvit](https://github.com/hoangsvit) · [ePlus.DEV](https://eplus.dev). Not affiliated with Google or MuMuPlayer.
