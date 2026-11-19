# ePlus AI Toolkit — 简体中文

[English](README.md) · [Tiếng Việt](README.vi.md) · **简体中文** · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md)

非官方终端工具，使用 Android、ADB、Frida 和 Google Play 查看 Google AI Pro 优惠。Windows 是维护中的稳定版本；macOS 版本已实现步骤 0–5，仍在 `dev` 分支开发。

![ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **可能产生真实费用。** 第 **2–5** 步可能打开 Google Play 结账并自动点击订阅。看到优惠或首期费用为 0 **不代表**免费、已激活或成功延期。请自行核实 Google Play 账户、当前及后续费用与续费日期。环境设置也可能修改 Android/Frida/网络配置。

## Quick start

**Windows：**单独安装 [MuMuPlayer](https://www.mumuplayer.com/download/)，启用 ADB/root 并登录 Google Play/Google One，然后运行 PowerShell：

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

**macOS 开发版：**需要 Python 3.10+、ADB 和已 root 的 Android 设备；尚未通过真实 Mac/MuMu 验证结账：

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
git switch dev
sh run-macos.sh
```

## Documentation

[中文版完整指南](docs/i18n/README.zh-CN.md) · [文档主页](docs/README.md) · [安装说明](docs/INSTALLATION.md) · [Mac 指南](docs/MACOS-PREVIEW.md) · [付款安全](docs/SAFETY.md)

[版本发布](https://github.com/hoangsvit/google-ai/releases) · [报告问题](https://github.com/hoangsvit/google-ai/issues) · [参与贡献](CONTRIBUTING.md) · [安全说明](SECURITY.md) · [免责声明](DISCLAIMER.md)

Original: [gylive/google-ultra](https://github.com/gylive/google-ultra). Maintainer: [@hoangsvit](https://github.com/hoangsvit) · [ePlus.DEV](https://eplus.dev). Not affiliated with Google or MuMuPlayer.
