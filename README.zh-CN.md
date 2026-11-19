# ePlus AI Toolkit — 简体中文

[English](README.md) · [Tiếng Việt](README.vi.md) · **简体中文** · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md)

非官方终端工具，使用 Android、ADB、Frida 和 Google Play 查看 Google AI Pro 优惠。Windows 和 macOS 均提供安装与启动方式；Mac 版实现了步骤 0–5，但尚未通过真实设备验证支付。

![ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **可能产生真实费用。** 第 **2–5** 步可能打开 Google Play 结账并自动点击订阅。看到优惠或首期费用为 0 **不代表**免费、已激活或成功延期。请自行核实 Google Play 账户、当前及后续费用与续费日期。环境设置也可能修改 Android/Frida/网络配置。

## Windows 安装

1. 安装 **Python 3.10+**、**Git**、PowerShell 5.1+ 和 [Windows 版 MuMuPlayer](https://www.mumuplayer.com/download/)。
2. 启动 Android 实例并开启 **root/ADB 调试**，登录 **Google Play Store** 和 **Google One**。
3. 打开 **PowerShell** 执行：

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

## macOS 安装

1. 安装 **Python 3.10+**、**Git** 和 **Android SDK Platform-Tools (ADB)**。Homebrew 用户可运行 `brew install android-platform-tools`。
2. 连接带 root、Google Play Store 与 Google One 的 Android 设备或兼容模拟器。Mac 版 **MuMuPlayer Pro 支持 Apple Silicon**；Intel Mac 需要其他兼容设备/模拟器。
3. 打开 **Terminal** 执行：

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
sh run-macos.sh
```

Mac 启动器会把 Python 依赖安装在 `.venv`。步骤 0–5 已实现，但**未在真实 Mac/MuMu 上验证支付**。详见 [Mac 安装指南](docs/MACOS-PREVIEW.md)。

## 首次运行（两个平台）

点击 **Check Device & Offers** 查询优惠（步骤 1，不结账）。步骤 0 可能修改 ADB/Frida/Android 设置。**步骤 2–5 可能产生真实费用**，务必在 Google Play 核实条款。

## 文档

[中文版完整指南](docs/i18n/README.zh-CN.md) · [文档主页](docs/README.md) · [安装说明](docs/INSTALLATION.md) · [Mac 指南](docs/MACOS-PREVIEW.md) · [付款安全](docs/SAFETY.md)

[版本发布](https://github.com/hoangsvit/google-ai/releases) · [报告问题](https://github.com/hoangsvit/google-ai/issues) · [参与贡献](CONTRIBUTING.md) · [安全说明](SECURITY.md) · [免责声明](DISCLAIMER.md)

Original: [gylive/google-ultra](https://github.com/gylive/google-ultra). Maintainer: [@hoangsvit](https://github.com/hoangsvit) · [ePlus.DEV](https://eplus.dev). Not affiliated with Google or MuMuPlayer.
