# ePlus AI Toolkit — 简体中文

> [!NOTE]
> 本文是历史补充资料，**并非当前 README 的完整最新翻译**。尤其在可能产生费用的操作前，请先阅读[最新简体中文 README](../../README.zh-CN.md)。

[← 当前简体中文翻译](../../README.zh-CN.md) · [Documentation home](../README.md) · [English user guide](../USAGE.md)

[English](../../README.md) · [Tiếng Việt](../../README.vi.md) · **简体中文** · [日本語](../../README.ja.md) · [한국어](../../README.ko.md) · [Español](../../README.es.md) · [Français](../../README.fr.md)

**macOS 预览版：**[Mac 专用版](../../docs/MACOS-PREVIEW.md)已实现步骤 0–5。步骤 2–5 可能产生真实扣费，每一步都需要单独确认；CI 测试不代表真实 Mac/MuMu 上的支付已验证。

> **权威版本：**[英文 README](../../README.md)。本翻译说明主要操作和风险；若有差异，请以当前代码及英文 README 为准。

这是一个主要面向 **Windows** 的终端工具，通过 **PowerShell、Python、ADB、Frida 和 Android 模拟器（MuMuPlayer）** 检查 Google One / Google Play 中的 Google AI Pro 优惠。Textual 界面与 CLI 使用同一底层引擎。

![ePlus AI Toolkit 界面](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **非官方工具，可能产生真实费用。** **Step 2–5** 可能打开 Google Play 的真实结账页面，并自动点击 **Subscribe（订阅）**。发现优惠、看到首期价格为 0，或收到“已提交结账”的消息，**均不代表**账户有资格、订阅免费、已激活或续期成功。每次操作前，请在 Google Play 上核实账户、本次收费、后续价格和续订日期。停止工具不能撤销已经提交的交易。

> [!NOTE]
> **即使 Google Play 的结账金额显示为 0 美元，银行卡验证仍可能暂时占用资金。** 您可能看到**约 3 美元**（也可能是其他金额）的待处理**预授权冻结**。**3 美元仅为示例，不是 Google 规定的固定费用，也不代表订阅已成功扣款。** 冻结金额可能暂时减少可用余额。Google 说明，此类预授权并非购买收费，通常会依据银行处理情况在 **1–14 个工作日**内解除。若变为正式入账的费用，或超过 14 个工作日仍未解除，请联系发卡银行与 Google Payments。参见 [Google Play 官方说明](https://support.google.com/googleplay/answer/6224192?hl=en)。

## 免责声明

本项目与 **Google、Google One、Google Play、NetEase、MuMuPlayer 没有从属或官方合作关系**。软件按**现状**提供，不保证优惠可用、订阅结果或设备兼容性。仅在您拥有或获授权使用的设备、账户上运行，并遵守法律及平台条款。详情参见[完整免责声明（英文）](../../DISCLAIMER.md)和[安全说明](../../SECURITY.md)。

## 1. 安装准备

- **Windows**、PowerShell **5.1+**、Python **3.10+**。
- **自行安装 MuMuPlayer**，在 Android 模拟器中启用 root 和 ADB 调试。
- 在模拟器中安装并登录 **Google Play Store** 与 **Google One**。
- 工具可在缺少时寻找/下载 **Android SDK Platform-Tools（ADB）**并准备 **Frida 16.5.9**，但**不会自动下载或安装 MuMuPlayer**。Frida 与 Android 版本的兼容性需单独确认。

**MuMuPlayer 官方下载：**[mumuplayer.com/download](https://www.mumuplayer.com/download/)（选择 Windows 版本）。请勿使用不明镜像站。更多说明见[项目安装 Wiki](https://github.com/hoangsvit/google-ai/wiki/Install)。

## 2. 获取并启动

在 PowerShell 中运行：

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

已克隆仓库时：

```powershell
git pull --ff-only
.\run-all.ps1
```

**不带参数**会打开 Textual 交互界面，而非立即执行结账。首次启动或检查时可能自动配置 Textual、ADB、Frida；通常不需要预先执行 `setup_env.py`。环境准备可能修改模拟器、代理或网络配置。

如 ADB 已在 PATH 中，检查设备：

```powershell
adb devices
```

设备应显示为 `device`，不能是 `offline` 或 `unauthorized`。有问题请参考[详细故障排查](../../docs/DETAILED-GUIDE.md)。

### 备用方案：最新源码出错时使用已发布版本

如果运行仓库最新代码遇到错误，可以尝试 [GitHub Releases](https://github.com/hoangsvit/google-ai/releases) 中**已发布的版本**。先阅读版本说明；若附带 Windows 安装包，可下载相应文件。若页面只有 GitHub 自动提供的 **Source code (zip)**，请下载 ZIP 并解压，在解压后的文件夹打开 PowerShell，然后运行：

```powershell
.\run-all.ps1
```

**Source code (zip) 不是预编译的 `.exe` 或安装程序。** 建议将发布版本放在**独立文件夹**，不要覆盖当前仓库。旧版本可能缺少最新修复；仍需 Windows、Python、MuMuPlayer、ADB/Frida，并遵守相同的支付安全注意事项。如果问题仍在，请参考[故障排查](../../docs/DETAILED-GUIDE.md)或[提交 Issue](https://github.com/hoangsvit/google-ai/issues)。

## 3. Textual 界面

点击 **Check Device & Offers** 执行 **Step 1 — Available offers**：查询优惠，**不会发起订阅结账**。查看 **Live Status** 和 **Show technical details** 以判断运行情况；30 秒无新日志不一定是死机。

在 **Advanced: Run by step** 中，可选择：

| 模式 | 行为 |
| --- | --- |
| **One step only** | 只执行所选的 Step 0–5 |
| **From selected step** | 从所选 Step 2–5 启动引导式流程 |
| **All: Steps 2–5** | 从 Step 2 启动引导式流程；Step 5 可选 |

| 步骤 | 用途 | 风险 |
| --- | --- | --- |
| **0 — Environment** | 准备/诊断 Android、ADB、Frida | 不结账，但可能修改本地/模拟器设置 |
| **1 — Available offers** | 查询 Google Play 优惠 | 不结账，但预检查可能修改环境 |
| **2 — Pro 12 months** | 原始 12 个月优惠流程 | **可能扣费** |
| **3 — Pro +6 months** | 原始订阅更新流程 | **可能扣费** |
| **4 — Pro +6 months (second)** | 第二次订阅更新流程 | **可能扣费** |
| **5 — Optional +6 months** | 可选更新流程 | **可能扣费** |

以上月数只是**历史流程名称**，不保证真正延长订阅。如果已有有效订阅，**不要重复 Step 2**。

TUI 中**每个结账步骤均需单独批准**。当工具提示已尝试提交结账时，请到 [Google Play Subscriptions](https://play.google.com/store/account/subscriptions) 亲自确认实际套餐、收费与续订日期。只有确认订阅确实改变后才能选择 **Verified in Google Play → Next**；工具本身**无法独立证明激活成功**。

**停止与退出：**Step 0–1 的 Stop 会请求终止本地检查。Step 2–5 的 **Stop after this step** 只阻止后续步骤，**不会强制中断正在进行的支付**。**Q / Exit** 在结账期间会等当前步骤结束；**D** 切换技术日志，**R** 执行当前选择。

## 4. PowerShell CLI（高级）

**查询/诊断：不发起结账**

```powershell
.\run-all.ps1 -Step 1
.\run-all.ps1 -Step 1 -Debug
.\run-all.ps1 -Step 0
.\run-all.ps1 -Cli
```

**以下命令可能发起真实交易：**

```powershell
.\run-all.ps1 -Step 2
.\run-all.ps1 -Step 3
.\run-all.ps1 -Step 4
.\run-all.ps1 -Step 5
```

与 TUI 不同，独立执行 `-Step 2..5` 时 **PowerShell 不会再次弹出批准提示**。请确认自己确实希望发起结账并已核实条款。

引导式 CLI：

```powershell
.\run-all.ps1 -AllStages
.\run-all.ps1 -AllStages -StartStep 3
```

CLI 确认选项为 **1 = Continue（继续）、2 = End run（结束）、0 = Stop（停止）**。每步后必须自行检查 Google Play。使用 `-StartStep 3` **不代表**前面的订阅更新已成功。

可指定设备或预期账号：

```powershell
.\run-all.ps1 -Step 1 -Serial emulator-5554
.\run-all.ps1 -AllStages -Email "account@gmail.com"
```

仅使用 ADB 实际显示的序列号。请避免 `-Force`：它会绕过账号匹配检查，但**不能**绕过优惠资格或 Google 支付限制。

## 5. 结果与排查

- **检测不到 MuMu/ADB：**检查模拟器运行状态、root、ADB 授权及设备连接。
- **Frida 错误：**查看技术日志，核对 **16.5.9** 及 Android 兼容性。
- **没有优惠：**启动 Google One/Play Store，重新执行 **Step 1**。
- **账户不匹配：**在 Play Store 检查登录账号，不要跳过验证。
- **已尝试提交结账：**不等于成功续订；重新操作前必须在 Google Play 上确认。
- **支付安全错误（如 OR-REH-04）：**停止付费步骤，按官方流程处理账号安全问题。

日志位于 `logs/`，报告位于 `ultra0-report/`。**不要公开包含账户、token 或支付信息的原始文件。** CI 只运行静态/模拟测试，**不验证真实交易**。完整 **macOS** 支持尚未完成。

## 社区支持及相关项目

安装或使用 ePlus AI Toolkit 时遇到问题，可通过 [ePlus Telegram 支持/讨论帖](https://t.me/eplus_news/29) 与社区联系、交流排错经验。可复现的软件问题也可以[提交 GitHub Issue](https://github.com/hoangsvit/google-ai/issues)。**请勿公开密码、OTP/2FA 验证码、优惠或购买 token、未经脱敏的日志以及银行卡信息。** 此渠道是社区交流，不属于 Google 官方支持。

**无法参与 Google AI Pro 优惠？** 可另行了解 ePlus.DEV 的 [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub)，在[网站上查找或分享 Muse 邀请码](https://muse.eplus.dev/)。**Muse 是独立服务**，Muse 邀请码**不能激活或替代** Google AI Pro 订阅，也不保证邀请码可用；资格可能受地区或账户限制。

## 资料与致谢

[英文 README](../../README.md) · [安装 Wiki](https://github.com/hoangsvit/google-ai/wiki/Install) · [详细指南](../../docs/DETAILED-GUIDE.md) · [原始步骤说明](../../docs/ORIGINAL-STEPS.md) · [免责声明](../../DISCLAIMER.md) · [安全说明](../../SECURITY.md) · [贡献](../../CONTRIBUTING.md) · [第三方版权声明](../../THIRD_PARTY_NOTICES.md)

**原作者：**[@gylive](https://github.com/gylive) — [google-ultra](https://github.com/gylive/google-ultra)。**维护者：**[David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev)。原始 MIT 版权声明保留在 `THIRD_PARTY_NOTICES.md`。
