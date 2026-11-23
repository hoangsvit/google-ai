# ePlus AI Toolkit — 简体中文

<!-- Source README.md git-blob: 4f68b0ea54146c62a96a97b322a6c8cab816547e -->

[English](README.md) · [Tiếng Việt](README.vi.md) · **简体中文** · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md)


> **原始文档：**[英文 README](README.md)。中文版采用更易理解的表述，同时保留原文中的命令、技术要求和安全警告。如文档与实际运行情况不一致，请以源代码及英文原文为准。

**ePlus AI Toolkit** 用于查看 Android 设备上的 Google One 和 Google Play 提供的 Google AI Pro 优惠。它支持 **Windows 和 macOS**：Windows 用户通过 PowerShell 启动，Mac 用户则使用 Terminal（zsh/bash）。Textual 图形化终端界面与命令行模式共用 Python、ADB 和 Frida 执行引擎。

![ePlus AI Toolkit 界面](images/terminal-ui-overview.png)

> [!CAUTION]
> **非官方工具，可能产生真实费用。** **Step 2–5** 可能打开 Google Play 的真实结账页面，并自动点击 **Subscribe（订阅）**。发现优惠、看到首期价格为 0，或收到“已提交结账”的消息，**均不代表**账户有资格、订阅免费、已激活或续期成功。每次操作前，请在 Google Play 上核实账户、本次收费、后续价格和续订日期。停止工具不能撤销已经提交的交易。

> [!NOTE]
> **至少准备 3 美元可用余额，用于三笔各 1 美元的独立交易，并非一次扣除 3 美元。** 在用户报告的 **24 个月**流程中，Step 2（最初 12 个月）、Step 3（延长 6 个月）和 Step 4（再延长 6 个月）各涉及**一笔 1 美元的银行卡验证或支付交易**：**3 × US$1 = US$3**。其中的 1 美元可能只是临时预授权冻结，并非已入账的实际扣款；金额也可能因银行、账户或 Google Play 的要求而不同。**3 美元只是这一案例的最低备用余额，不是固定手续费，也不保证所有账户都能获得 24 个月。** 预授权会暂时占用可用余额，通常依据银行处理情况在 **1–14 个工作日**内解除。每完成一步，请到 Google Play 核实交易状态和订阅续订日期。可选的 Step 5 **不计入上述三笔交易**。[Google Play 官方说明](https://support.google.com/googleplay/answer/6224192?hl=en)。

## 免责声明

本项目与 **Google、Google One、Google Play、NetEase、MuMuPlayer 没有从属或官方合作关系**。软件按**现状**提供，不保证优惠可用、订阅结果或设备兼容性。仅在您拥有或获授权使用的设备、账户上运行，并遵守法律及平台条款。详情参见[完整免责声明（英文）](DISCLAIMER.md)和[安全说明](SECURITY.md)。

## 1. 使用前的准备工作

**请按照自己的操作系统进行设置。** Mac 用户无需安装 PowerShell。

| 项目 | Windows | macOS |
| --- | --- | --- |
| 终端 | **PowerShell 5.1 或更高版本** | 系统自带的 **Terminal**（zsh/bash） |
| Python | **3.10 或更高版本**，使用 `python` 命令 | **3.10 或更高版本**，使用 `python3`；启动时创建本地 `.venv` 环境 |
| Git | Git for Windows | 通过 Xcode Command Line Tools 或 Homebrew 安装 |
| Android 环境 | 已开启 root 和 ADB 的设备或模拟器；项目提供 **Windows 版 MuMuPlayer** 的操作流程 | 已 root 的 Android 设备或兼容模拟器；**Mac 版 MuMuPlayer Pro** 适用于 Apple Silicon，不支持 Intel Mac |
| Android 应用 | Google Play Store 和 Google One，并登录要检查的账户 | 所选 Android 设备上同样需要安装这两个应用 |
| ADB | 工具可按需查找或下载 Android SDK Platform-Tools | 需单独安装，例如 `brew install android-platform-tools`；使用 `adb devices` 检查连接 |
| Frida | **16.5.9**，可由 Windows 配置程序准备 | 在 `.venv` 中安装 **16.5.9**，仍需核实与 Android 的兼容性 |
| 启动命令 | `.\run-all.ps1` | `sh run-macos.sh` 或 `ePlus-AI-Toolkit.command` |

无论使用哪种系统，都需要一个已经正确配置、且你有权访问的 Android 环境。虽然 macOS 版本已实现 Steps 0–5，**但尚未在真实 Mac/MuMu 环境中验证支付流程**。另请参考 [Windows 指南](docs/INSTALLATION.md)和 [macOS 指南](docs/MACOS-PREVIEW.md)。

### Windows 环境要求

- Windows，已安装 **PowerShell 5.1 或更高版本**及 **Python 3.10 或更高版本**。
- 自行安装 MuMuPlayer，并为 Android 实例启用 root 和 ADB 调试。
- 在 Android 中安装 Google Play Store 和 Google One，使用要检查优惠的 Google 账户登录。
- 准备可连接的 ADB 和兼容的 **Frida 16.5.9**。本工具可协助配置，但**不会代为安装 MuMuPlayer**。

### 第一步 — 安装 MuMuPlayer

从 [MuMuPlayer 官方网站（NetEase）](https://www.mumuplayer.com/download/)下载 Windows 版本。请勿使用来源不明的下载站点。

启动模拟器后，启用 root 权限和 ADB 调试。确保 Google Play Store 和 Google One 可用，并登录正确的 Google 账户。

需要图文步骤时，可参阅 [GitHub Wiki 安装指南](https://github.com/hoangsvit/google-ai/wiki/Install)。

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

设备应显示为 `device`，不能是 `offline` 或 `unauthorized`。有问题请参考[详细故障排查](docs/DETAILED-GUIDE.md)。

### 最新版本无法使用时，尝试已发布版本

如果运行仓库最新代码遇到错误，可以尝试 [GitHub Releases](https://github.com/hoangsvit/google-ai/releases) 中**已发布的版本**。先阅读版本说明；若附带 Windows 安装包，可下载相应文件。若页面只有 GitHub 自动提供的 **Source code (zip)**，请下载 ZIP 并解压，在解压后的文件夹打开 PowerShell，然后运行：

```powershell
.\run-all.ps1
```

**Source code (zip) 不是预编译的 `.exe` 或安装程序。** 建议将发布版本放在**独立文件夹**，不要覆盖当前仓库。旧版本可能缺少最新修复；仍需 Windows、Python、MuMuPlayer、ADB/Frida，并遵守相同的支付安全注意事项。如果问题仍在，请参考[故障排查](docs/DETAILED-GUIDE.md)或[提交 Issue](https://github.com/hoangsvit/google-ai/issues)。

## macOS — 安装和启动

macOS 需安装 **Git**、**Python 3.10+** 与 **Android SDK Platform-Tools (ADB)**（Homebrew：`brew install android-platform-tools`）。连接已 root、具有 Google Play Store 和 Google One 的 Android 设备或兼容模拟器。Mac 版 **MuMuPlayer Pro 支持 Apple Silicon**，Intel Mac 需要其他兼容 Android 环境。

在 **Terminal** 中执行：

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
adb devices
sh run-macos.sh
```

`sh run-macos.sh` 打开包含 **步骤 0–5** 的 Textual 界面。`--check` 检查环境（可能改变配置）；`--list` 仅查询优惠；`--step 2` 只预选该步骤，**不会自动付款**。步骤 2–5 可能产生真实费用，必须逐步确认。**真实 Mac/MuMu 上的支付尚未验证。** 参阅 [Mac 详细指南](docs/MACOS-PREVIEW.md)。

## Linux — 安装和启动

在 Ubuntu x86_64 上安装 Git、带有 `venv` 和 `pip` 的 Python 3.10 或更高版本，以及 Android SDK Platform-Tools。将 `adb` 加入 `PATH`，或用 `ADB_PATH` 指定可执行文件。用 USB 连接已取得 root 权限且装有 Google Play 商店和 Google One 的 Android 手机。打开 USB 调试，解锁手机并确认授权。ADB 应只显示一台状态为 `device` 的设备。

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
git switch feature
adb devices
sh run-linux.sh
```

请选择包含 `run-linux.sh` 的版本。启动脚本会打开界面，并在本地 `.venv` 中安装固定版本的 Textual 和 Frida 16.5.9。如果 Ubuntu 无法创建虚拟环境，请安装 `python3-venv` 或与当前 Python 版本对应的 venv 软件包。

- `sh run-linux.sh --check` 运行第 0 步，可能更改 Android、Frida 或网络设置。
- `sh run-linux.sh --list` 运行第 1 步以查看优惠，不会发起结账，但仍可能配置 Android 环境。
- `sh run-linux.sh --step 3` 打开高级设置并预选第 3 步。 `sh run-linux.sh --sequence` 打开从第 2 步开始的引导设置。两个命令都只打开界面，不会执行步骤。

**Android 16 及更高版本：** 固定使用的 Frida 16.5.9 尚不支持 Android 16，因此 Linux 启动脚本会在配置设备前停止。仍可通过 **Diagnose Android connection** 检查 USB 连接。

**第 2–5 步可能产生真实的 Google Play 费用。** 每一步都须单独确认、核实当前 Play 账号，并通过本次查询确认优惠完全匹配且首期价格为零。继续引导流程前，请在 Google Play 中核实订阅和续订日期。Linux 结账仅通过模拟测试，真机端到端验证尚未完成。 [Linux 安装、USB 故障排查和验证](docs/LINUX.md).


## 3. Textual 界面

在某个步骤运行期间，**Check Device & Offers**、**Run** 以及模式和步骤选择功能会暂时锁定，避免重复执行。Step 0 可能修改电脑上的设置；Step 1 虽不会主动付款，但在准备过程中可能调整 ADB/Frida。请先到 Google Play 核实结果，再进入下一步。**点击 Stop 或 Exit 并不能撤销已提交的交易。**


点击 **Check Device & Offers** 执行 **Step 1 — Available offers**：查询优惠，**不会发起订阅结账**。可通过 **Live Status** 和 **Show technical details** 查看进度。如果 30 秒内没有新日志，程序会给出提醒，但这**不一定表示程序卡住了**。

界面空闲时，工具约每 5 秒检查一次现有 ADB 连接。找不到 ADB 或 Android 设备时，会弹窗说明处理方法；工具会继续检查并更新设备状态。重新连接本身不会解锁付款步骤。执行步骤或显示其他对话框时，监测会暂停。工具不会在后台安装或连接设备，但 `adb devices` 可能启动电脑上的本地 ADB 服务。

在 Windows 上，运行 **Check Device & Offers** 时，工具会查找 ADB，必要时尝试下载官方 Android SDK Platform-Tools。下载或安装可能失败，请通过 **Show technical details** 查看详情。macOS 请按 Mac 指南安装 Platform-Tools。MuMu 需要自行安装和启动，并启用 root、ADB 调试，登录 Google Play 与 Google One。

只有新的 Step 1 检查返回优惠并确认 Play 账号后，Step 2–5 才会解锁。如果 12 个月优惠 `12months-eft` 的首期价格为 0，完成弹窗和主界面会显示 **Continue to Step 2**；否则请查看优惠列表。该按钮只会打开单独的确认窗口，并不保证账号符合条件或最终费用为零。提交付款请求后，请先在 Google Play 核对订阅、续费日期和实际费用，再选择 **Verified in Google Play → Next**。后续每一步都需要单独确认。重新检查、付款步骤失败或设备变化可能使付款步骤重新锁定。

在 **Choose another step** 中，可选择：

默认只执行所选步骤。在 **Choose another step** 的步骤下拉列表底部选择 **More run options…**，即可显示引导式运行模式。

| 模式 | 行为 |
| --- | --- |
| **Stop after this step** | 只执行所选的 Step 0–5 |
| **Offer the next step** | 从所选 Step 2–5 启动引导式流程 |
| **Start at Step 2** | 从 Step 2 启动引导式流程；Step 5 可选 |

| 步骤 | 用途 | 风险 |
| --- | --- | --- |
| **0 — Environment** | 准备/诊断 Android、ADB、Frida | 不结账，但可能修改本地/模拟器设置 |
| **1 — Available offers** | 查询 Google Play 优惠 | 不结账，但预检查可能修改环境 |
| **2 — Pro 12 months** | 原始 12 个月优惠流程 | **可能扣费** |
| **3 — Pro +6 months** | 原始订阅更新流程 | **可能扣费** |
| **4 — Pro +6 months (second)** | 第二次订阅更新流程 | **可能扣费** |
| **5 — Optional +6 months** | 可选更新流程 | **可能扣费** |

**用户报告的 24 个月示例（需要在 Google Play 核实）：**

| 步骤 | 成功生效后的累计时长 | 独立交易 |
| --- | --- | --- |
| **2 — Pro 12 months** | 最初 **12 个月** | **1 美元**（第 1 笔） |
| **3 — Pro +6 months** | 合计 **18 个月** | **1 美元**（第 2 笔） |
| **4 — Pro +6 months (second)** | 合计 **24 个月** | **1 美元**（第 3 笔） |
| **截至 Step 4** | 核实后合计 **24 个月** | **3 × US$1 = US$3**，不是一次支付 3 美元 |

**可选的 Step 5 不计入这三笔交易。** 页面上显示的时长或银行卡预授权并不能证明续期成功；每一步完成后都应在 Google Play 中确认订阅和续订日期。

以上月数只是**历史流程名称**，不保证真正延长订阅。如果已有有效订阅，**不要重复 Step 2**。

TUI 中**每个结账步骤均需单独批准**。当工具提示已尝试提交结账时，请到 [Google Play Subscriptions](https://play.google.com/store/account/subscriptions) 亲自确认实际套餐、收费与续订日期。只有确认订阅确实改变后才能选择 **Verified in Google Play → Next**；工具本身**无法独立证明激活成功**。

**停止与退出：**Step 0–1 的 Stop 会请求终止本地检查。Step 2–5 的 **Stop after this step** 只阻止后续步骤，**不会强制中断正在进行的支付**。**Q / Exit** 在结账期间会等当前步骤结束；**D** 切换技术日志，**R** 执行当前选择。

### 设备、账号与历史记录

Device 卡片显示读取到的 Android 版本、SDK、ABI 和 ADB 连接信息，悬停可查看完整内容。Account 旁的 **Choose account** 会列出 Android 已登录的账号。请在 Play Store 和 Google One 中选择目标账号，然后重新运行 Step 1。若 Play Store 明确提供当前个人资料的邮箱，工具会据此识别正在使用的账号。

操作面板按内容调整高度，**Live Status** 使用剩余空间，最新活动显示在顶部。**Show technical details** 的日志会自动跟随新行。主按钮和 **Run this step** 均显示正在运行的步骤及已用秒数。Windows 的优惠查询流程完成环境检查后，Step 0 会出现勾选标记。缺少新的已验证检查结果时，会显示绿色 **Check Device & Offers — Step 1** 按钮。

**Recent history** 将开始、结果和 **Verified in Google Play → Next** 操作保存到本地 `logs/stage-history/`。启动时恢复最近保存的记录，选择账号后显示该账号的历史。**↺** 表示曾尝试运行的步骤。历史本身不能证明订阅成功，也不会解锁付款。重新打开工具或更换账号后，需要重新运行 Step 1。加入历史记录功能之前的运行无法恢复。

断开连接的弹窗提供 **Retry connection**，处理时显示 **Retrying…** 和已用秒数；**Got it** 关闭弹窗。Windows 会尝试重新连接本地模拟器，启动步骤时找不到在线 ADB 设备也会尝试连接。只读查询期间，应用启动失败会重启一次。若仍失败，请关闭并重新打开 MuMu，等待 Android 启动完成后重跑 Step 1。查询优惠前会重启 Google One；已正常运行的 Play Store 会保持运行。空闲时点击 **Reload toolkit** 可使用本地代码重新打开界面并开始新会话。

自动点击 **Subscribe** 前，付款画面必须显示准确匹配的邮箱、今天应付总额为零及预期试用期，所请求的优惠也必须匹配。邮箱缺失或不匹配时，会停止自动点击并要求人工核对。每个付款步骤都需要单独批准。提交后仍需在 Google Play 核实订阅、续费日期和扣款。三次银行卡验证的提醒显示在付款确认框中。

## 4. PowerShell 命令行操作（高级）

**仅适用于 Windows。** 以下命令在 PowerShell 中使用。Mac 用户请改用 `run-macos.sh`，并参考 [macOS 使用指南](docs/MACOS-PREVIEW.md)。启动时指定参数会直接进入 CLI 模式，而不是打开 Textual 界面。

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

## 5. 查看结果与排查问题

- **检测不到 MuMu/ADB：**检查模拟器运行状态、root、ADB 授权及设备连接。
- **Frida 错误：**查看技术日志，核对 **16.5.9** 及 Android 兼容性。
- **没有优惠：**启动 Google One/Play Store，重新执行 **Step 1**。
- **账户不匹配：**在 Play Store 检查登录账号，不要跳过验证。
- **已尝试提交结账：**不等于成功续订；重新操作前必须在 Google Play 上确认。
- **支付安全错误（如 OR-REH-04）：**停止付费步骤，按官方流程处理账号安全问题。

日志位于 `logs/`，报告位于 `ultra0-report/`。**不要公开包含账户、token 或支付信息的原始文件。** CI 仅执行静态检查和模拟测试，**不会进行或验证真实的 Google Play 交易**。

## 社区支持及相关项目

安装或使用 ePlus AI Toolkit 时遇到问题，可通过 [ePlus Telegram 支持/讨论帖](https://t.me/eplus_news/29) 与社区联系、交流排错经验。可复现的软件问题也可以[提交 GitHub Issue](https://github.com/hoangsvit/google-ai/issues)。**请勿公开密码、OTP/2FA 验证码、优惠或购买 token、未经脱敏的日志以及银行卡信息。** 此渠道是社区交流，不属于 Google 官方支持。

**无法参与 Google AI Pro 优惠？** 可另行了解 ePlus.DEV 的 [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub)，在[网站上查找或分享 Muse 邀请码](https://muse.eplus.dev/)。**Muse 是独立服务**，Muse 邀请码**不能激活或替代** Google AI Pro 订阅，也不保证邀请码可用；资格可能受地区或账户限制。

## 项目文件结构

为保证现有使用说明仍然有效，启动脚本和主要 Python 模块保留在仓库根目录。Windows 使用 `run-all.ps1`，macOS 使用 `run-macos.sh`。

| 文件或目录 | 用途 |
| --- | --- |
| `run-all.ps1` | 在 Windows 上打开 Textual 界面或命令行模式 |
| `run-macos.sh`、`ePlus-AI-Toolkit.command`、`macos_runner.py` | 在 Mac 上启动、运行 Steps 0–5；尚未验证真实支付 |
| `tui.py`、`tui_core.py`、`ultra0.py`、`setup_env.py`、`device_selector.py`、`query_sku.py` | 工具当前使用的 Python 组件 |
| [`tools/windows/`](tools/windows/README.md) | 按需使用的 Windows 手动配置工具 |
| [`legacy/windows/`](legacy/windows/README.md) | 旧版 .bat 脚本；部分脚本使用 `--force` 跳过账户检查，**可能产生实际费用** |
| `scripts/`、`assets/` | 辅助脚本及 Android/Frida 资源 |
| `tests/`、`.github/workflows/`、`docs/` | 自动测试、GitHub Actions 与文档 |

## 文档与参与贡献

[英文 README](README.md) · [安装 Wiki](https://github.com/hoangsvit/google-ai/wiki/Install) · [详细指南](docs/DETAILED-GUIDE.md) · [原始步骤说明](docs/ORIGINAL-STEPS.md) · [免责声明](DISCLAIMER.md) · [安全说明](SECURITY.md) · [贡献](CONTRIBUTING.md) · [第三方版权声明](THIRD_PARTY_NOTICES.md)

另请参阅[项目结构](docs/PROJECT.md)、[控制台/CLI 用法](docs/USAGE.md)、[支付安全](docs/SAFETY.md)、[原作者备注](docs/AUTHOR-NOTES.md)及 [AI 代理规则](AGENTS.md)。GitHub Actions 仅测试 Python、PowerShell、Textual 及模拟的 Frida/Billing 行为，**不会执行真实 Google Play 交易**。CI 测试通过并不代表工具一定能在你的设备上运行，也不能证明账户符合优惠条件。

## 致谢

**原作者：**[@gylive](https://github.com/gylive) — [google-ultra](https://github.com/gylive/google-ultra)。**维护者：**[David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev)。原始 MIT 版权声明保留在 `THIRD_PARTY_NOTICES.md`。

[文档主页](docs/README.md) · [历史中文参考指南](docs/i18n/README.zh-CN.md) · [付款安全](docs/SAFETY.md)
