# ePlus AI Toolkit — 日本語

[← Short overview](../../README.ja.md) · [Documentation home](../README.md) · [English user guide](../USAGE.md)

[English](../../README.md) · [Tiếng Việt](../../README.vi.md) · [简体中文](../../README.zh-CN.md) · **日本語** · [한국어](../../README.ko.md) · [Español](../../README.es.md) · [Français](../../README.fr.md)

**macOS プレビュー：**[Mac 対応版](../../docs/MACOS-PREVIEW.md)はステップ 0–5 を実装しました。決済ステップ 2–5 は実際に請求される可能性があり、各ステップで確認が必要です。Mac/MuMu 実機での決済動作は未検証です。

> **正本：**[英語版 README](../../README.md)。この翻訳は利用方法と注意事項をまとめたものです。差異がある場合は現在のソースコードと英語版を確認してください。

**ePlus AI Toolkit** は、主に **Windows** 向けのターミナルツールです。**PowerShell・Python・ADB・Frida・Android エミュレーター（MuMuPlayer）** を使用し、Google One / Google Play 上の Google AI Pro オファーを調べます。Textual UI と CLI は共通の実行エンジンを使用します。

![ePlus AI Toolkit の画面](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **非公式ツールです。実際の料金が発生する可能性があります。** **Step 2〜5** は Google Play の実際の購入画面を開き、条件によって **Subscribe（定期購入）** を自動タップする場合があります。オファーの表示、初回料金 0、またはチェックアウト送信の表示は、**対象資格・無料提供・契約成立・更新成功の証拠ではありません**。実行前に Google Play でアカウント、今日の請求額、更新料金、次回請求日を確認してください。停止操作は送信済みの取引を取り消しません。

> [!NOTE]
> **Google Play の購入金額が 0 米ドルでも、カード確認のため一時的に利用可能残高が減る場合があります。** **約 3 米ドル**（金額は異なる場合あり）の**仮承認・一時保留**が明細に表示されることがあります。**3 米ドルは一例であり、Google の固定手数料や確定したサブスクリプション料金ではありません。** Google によると、仮承認は購入料金ではなく、銀行により通常 **1～14 営業日**で解除されます。確定請求として計上された場合、または 14 営業日を超えて保留が続く場合は、カード発行会社と Google Payments に確認してください。[Google Play の公式説明](https://support.google.com/googleplay/answer/6224192?hl=en)。

## 免責事項

本プロジェクトは **Google・Google One・Google Play・NetEase・MuMuPlayer と提携・後援・承認関係にない独立した非公式ソフトウェア**です。ソフトウェアは**現状有姿**で提供され、オファーの適用、契約結果や互換性を保証しません。所有または使用権限のある端末・アカウントでのみ使用し、適用法令およびサービス規約を遵守してください。[免責事項全文（英語）](../../DISCLAIMER.md)と[セキュリティ注意事項](../../SECURITY.md)を参照してください。

## 1. 動作環境と MuMuPlayer

- **Windows**、PowerShell **5.1 以上**、Python **3.10 以上**。
- **MuMuPlayer を別途インストール**し、Android インスタンスの root と ADB デバッグを有効にする。
- Android 内に **Google Play Store** と **Google One** を用意し、対象アカウントでログインする。
- ツールは **Android SDK Platform-Tools（ADB）** や **Frida 16.5.9** を検出・準備できますが、**MuMuPlayer 自体はダウンロード／インストールしません**。Frida の互換性は Android バージョンに依存します。

**公式 MuMuPlayer ダウンロード：**[mumuplayer.com/download](https://www.mumuplayer.com/download/) から Windows 版を選んでください。非公式ミラーは避けてください。詳しくは[インストール Wiki](https://github.com/hoangsvit/google-ai/wiki/Install)を参照。

## 2. インストールと起動

PowerShell で次を実行します。

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

既にクローン済みの場合：

```powershell
git pull --ff-only
.\run-all.ps1
```

**引数なし**では Textual ダッシュボードが開き、購入処理は自動開始されません。必要に応じて Textual / ADB / Frida の準備が行われます。通常、事前の `setup_env.py` 実行は不要です。環境設定によりエミュレーター・プロキシ・ネットワーク設定が変更される場合があります。

ADB が PATH にある場合は接続を確認できます。

```powershell
adb devices
```

状態は `device` である必要があります。`offline` や `unauthorized` の場合は設定を確認してください。[詳細トラブルシューティング](../../docs/DETAILED-GUIDE.md)。

### 代替手段：最新版ソースで問題が起きる場合はリリース版を試す

最新のソースコードの実行でエラーが起きたら、[GitHub Releases](https://github.com/hoangsvit/google-ai/releases) の**公開済みリリース**を試せます。リリースノートを読み、Windows 向けの添付ファイルがあればダウンロードしてください。GitHub が自動生成する **Source code (zip)** しかない場合は ZIP をダウンロードして展開し、展開先で PowerShell を開いて次を実行します。

```powershell
.\run-all.ps1
```

**Source code (zip) はビルド済み `.exe` やインストーラーではありません。** 現在の作業フォルダーを上書きせず、**別のフォルダー**に保存してください。古いリリースには最近の修正が含まれない場合があります。Windows、Python、MuMuPlayer、ADB/Frida および決済に関する注意事項は変わりません。解決しない場合は[トラブルシューティング](../../docs/DETAILED-GUIDE.md)や [Issues](https://github.com/hoangsvit/google-ai/issues) を参照してください。

## 3. ダッシュボードの使い方

**Check Device & Offers** を押すと **Step 1 — Available offers** が実行され、オファーを照会します。**購入処理は開始しません**。**Live Status** と **Show technical details** で進行状況を確認します。ログ更新が 30 秒ない場合の警告は、フリーズの確定ではありません。

**Advanced: Run by step** のモード：

| モード | 動作 |
| --- | --- |
| **One step only** | 選択した Step 0〜5 だけを実行 |
| **From selected step** | 選択した Step 2〜5 から確認付きのフローを開始 |
| **All: Steps 2–5** | Step 2 から確認付きフローを開始。Step 5 は任意 |

| Step | 内容 | リスク |
| --- | --- | --- |
| **0 — Environment** | Android / ADB / Frida の診断・準備 | 購入は行わないが環境設定を変更し得る |
| **1 — Available offers** | Google Play のオファー照会 | 購入は行わないが事前準備は環境を変更し得る |
| **2 — Pro 12 months** | オリジナルの 12 か月オファー処理 | **課金の可能性** |
| **3 — Pro +6 months** | オリジナルの契約更新処理 | **課金の可能性** |
| **4 — Pro +6 months (second)** | 追加の契約更新処理 | **課金の可能性** |
| **5 — Optional +6 months** | 任意の追加更新処理 | **課金の可能性** |

月数は**従来のステップ名**であり、延長を保証するものではありません。既に契約がある場合、**Step 2 を再実行しないでください**。

TUI では**購入ステップごとに明示的な承認**が必要です。チェックアウトを送信した旨が表示されても、[Google Play の定期購入](https://play.google.com/store/account/subscriptions)で現在の契約、料金、更新日を確認してください。実際に変更を確認した場合のみ **Verified in Google Play → Next** を選びます。ツール単体では契約成立を証明できません。

**Stop / Exit：**Step 0〜1 の Stop はローカル処理の中止を要求します。Step 2〜5 の **Stop after this step** は後続ステップを止めますが、**処理中の決済を強制終了しません**。決済中の **Q / Exit** は現在の処理終了後に終了します。**D** は詳細ログ、**R** は選択中のモード実行です。

## 4. PowerShell CLI（上級者向け）

**照会・診断（購入処理なし）：**

```powershell
.\run-all.ps1 -Step 1
.\run-all.ps1 -Step 1 -Debug
.\run-all.ps1 -Step 0
.\run-all.ps1 -Cli
```

**次のコマンドは実際の決済を開始する可能性があります：**

```powershell
.\run-all.ps1 -Step 2
.\run-all.ps1 -Step 3
.\run-all.ps1 -Step 4
.\run-all.ps1 -Step 5
```

TUI とは異なり、個別の `-Step 2..5` には **PowerShell 側で追加の承認ダイアログがありません**。条件を確認し、実際の決済を意図する場合にのみ実行してください。

確認付き CLI フロー：

```powershell
.\run-all.ps1 -AllStages
.\run-all.ps1 -AllStages -StartStep 3
```

入力は **1 = Continue（続行）、2 = End run（終了）、0 = Stop（中止）**。各ステップ後、Google Play で自分で結果を確認してください。`-StartStep 3` は以前の延長成功を保証しません。

端末・アカウントの指定：

```powershell
.\run-all.ps1 -Step 1 -Serial emulator-5554
.\run-all.ps1 -AllStages -Email "account@gmail.com"
```

実際の ADB シリアルのみ指定してください。`-Force` はアカウント一致確認を回避するため**推奨しません**。Google のオファー資格や決済制限を回避するものではありません。

## 5. よくある問題と結果

- **MuMu/ADB が見つからない：**エミュレーターの起動、root、ADB 許可、接続を確認。
- **Frida エラー：**ログと **16.5.9** / Android の互換性を確認。
- **オファーがない：**Google One / Play Store を起動し、**Step 1** を再実行。
- **アカウントが異なる：**Play Store のログイン先を確認し、チェックを回避しない。
- **チェックアウト送信表示：**契約成立とは限りません。再試行前に Google Play で確認。
- **セキュリティエラー（例：OR-REH-04）：**課金ステップを止めて正規のアカウント保護手順に従う。

ログは `logs/`、レポートは `ultra0-report/` に保存されます。**アカウント情報、トークン、決済情報を含む生データを共有しないでください。** CI は静的・モックテストのみで、実購入を検証しません。**macOS フル対応は未実装です**。

## コミュニティサポートと関連プロジェクト

ePlus AI Toolkit のインストールや使用に問題があれば、[ePlus の Telegram サポート・交流投稿](https://t.me/eplus_news/29)で相談したり、トラブルシューティング情報を交換したりできます。再現可能な不具合は [GitHub Issue](https://github.com/hoangsvit/google-ai/issues) で報告してください。**パスワード、OTP/2FA コード、オファー・購入トークン、個人情報を含むログ、カード情報を公開しないでください。** Google の公式サポートではありません。

**Google AI Pro の特典に参加できない場合：**別の ePlus.DEV プロジェクト [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub) で [Muse の招待コードを探す／共有する](https://muse.eplus.dev/) こともできます。**Muse は別サービス**であり、その招待コードは **Google AI Pro のサブスクリプションの代わりにならず、利用権を付与しません**。コードの有効性や地域・アカウント条件は保証されません。

## ドキュメントとクレジット

[英語版 README](../../README.md) · [Install Wiki](https://github.com/hoangsvit/google-ai/wiki/Install) · [詳細ガイド](../../docs/DETAILED-GUIDE.md) · [原作者のステップ](../../docs/ORIGINAL-STEPS.md) · [免責事項](../../DISCLAIMER.md) · [セキュリティ](../../SECURITY.md) · [貢献](../../CONTRIBUTING.md) · [著作権表示](../../THIRD_PARTY_NOTICES.md)

**原作者：**[@gylive](https://github.com/gylive) — [google-ultra](https://github.com/gylive/google-ultra)。**メンテナー：**[David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev)。元の MIT 著作権表示は `THIRD_PARTY_NOTICES.md` に保持しています。
