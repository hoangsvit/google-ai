# ePlus AI Toolkit — 日本語

<!-- Source README.md git-blob: daf5a76837f9cefab213a3faf18f71653641888a -->

[English](README.md) · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · **日本語** · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md)


> **原文：** [英語版 README](README.md)。この日本語版では、操作方法と注意点を分かりやすく説明しています。コマンドや技術的な条件は原文に合わせていますが、記載と実際の動作が異なる場合はコードと英語版をご確認ください。

**ePlus AI Toolkit** は、Android 端末上の Google One / Google Play で表示される Google AI Pro の特典を確認するためのツールです。**Windows** では PowerShell、**macOS** では Terminal（zsh/bash）から起動します。画面操作用の Textual UI とコマンドライン操作には、共通の Python・ADB・Frida エンジンを使用しています。

![ePlus AI Toolkit の画面](https://github.com/user-attachments/assets/fc27278f-7833-4484-9770-33e46bf10005)

> [!CAUTION]
> **非公式ツールです。実際の料金が発生する可能性があります。** **Step 2〜5** は Google Play の実際の購入画面を開き、条件によって **Subscribe（定期購入）** を自動タップする場合があります。オファーの表示、初回料金 0、またはチェックアウト送信の表示は、**対象資格・無料提供・契約成立・更新成功の証拠ではありません**。実行前に Google Play でアカウント、今日の請求額、更新料金、次回請求日を確認してください。停止操作は送信済みの取引を取り消しません。

> [!NOTE]
> **Google Play の購入金額が 0 米ドルでも、カード確認のため一時的に利用可能残高が減る場合があります。** **約 3 米ドル**（金額は異なる場合あり）の**仮承認・一時保留**が明細に表示されることがあります。**3 米ドルは一例であり、Google の固定手数料や確定したサブスクリプション料金ではありません。** Google によると、仮承認は購入料金ではなく、銀行により通常 **1～14 営業日**で解除されます。確定請求として計上された場合、または 14 営業日を超えて保留が続く場合は、カード発行会社と Google Payments に確認してください。[Google Play の公式説明](https://support.google.com/googleplay/answer/6224192?hl=en)。

## 免責事項

本プロジェクトは **Google・Google One・Google Play・NetEase・MuMuPlayer と提携・後援・承認関係にない独立した非公式ソフトウェア**です。ソフトウェアは**現状有姿**で提供され、オファーの適用、契約結果や互換性を保証しません。所有または使用権限のある端末・アカウントでのみ使用し、適用法令およびサービス規約を遵守してください。[免責事項全文（英語）](DISCLAIMER.md)と[セキュリティ注意事項](SECURITY.md)を参照してください。

## 1. 利用前の準備

**お使いの OS に合わせて準備してください。** macOS に PowerShell をインストールする必要はありません。

| 項目 | Windows | macOS |
| --- | --- | --- |
| ターミナル | **PowerShell 5.1 以降** | 標準の **Terminal**（zsh / bash） |
| Python | **3.10 以降**（`python` コマンド） | **3.10 以降**（`python3` コマンド）。起動時に `.venv` を作成 |
| Git | Git for Windows | Xcode Command Line Tools または Homebrew などで導入 |
| Android 環境 | root と ADB を有効にした端末・エミュレーター。**Windows 版 MuMuPlayer** を使う手順を用意 | root 化した端末・互換エミュレーター。**Mac 版 MuMuPlayer Pro** は Apple Silicon 向けで、Intel Mac には対応していません |
| Android アプリ | 使用するアカウントでログインした Google Play Store と Google One | 接続先の Android に同じアプリが必要 |
| ADB | 必要に応じて Android SDK Platform-Tools を検索・ダウンロード | 別途インストール。例：`brew install android-platform-tools`。`adb devices` で接続を確認 |
| Frida | **16.5.9**。Windows 用のセットアップ処理で準備可能 | `.venv` に **16.5.9** を導入。Android 側との互換性を確認 |
| 起動コマンド | `.\run-all.ps1` | `sh run-macos.sh` または `ePlus-AI-Toolkit.command` |

どちらの OS でも、**使用権限があり、正しく設定された Android 環境**が必要です。macOS 向けのコードには Steps 0–5 が実装されていますが、**実際の Mac / MuMuPlayer での決済動作は検証されていません**。[Windows 向け手順](docs/INSTALLATION.md)と[macOS 向け手順](docs/MACOS-PREVIEW.md)もご覧ください。

### Windows で必要なもの

- **PowerShell 5.1 以降**と **Python 3.10 以降**が動く Windows。
- 別途インストールした MuMuPlayer。Android インスタンスで root と ADB を有効にしてください。
- Google Play Store と Google One。特典を確認したい Google アカウントでログインしてください。
- 接続可能な ADB と、Android に対応した **Frida 16.5.9**。必要に応じてツールが準備を補助しますが、**MuMuPlayer 自体はインストールしません**。

### 手順 1 — MuMuPlayer をインストールする

[MuMuPlayer の公式サイト（NetEase）](https://www.mumuplayer.com/download/)から Windows 版を入手してください。非公式の配布サイトは避けてください。

起動後、Android インスタンスの root と ADB デバッグを有効にします。Google Play Store と Google One が使えることを確認し、対象のアカウントでログインしてください。

画像付きの説明は [GitHub Wiki のインストールガイド](https://github.com/hoangsvit/google-ai/wiki/Install)にもあります。

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

状態は `device` である必要があります。`offline` や `unauthorized` の場合は設定を確認してください。[詳細トラブルシューティング](docs/DETAILED-GUIDE.md)。

### 最新版で動かない場合は、公開済みのリリースを試す

最新のソースコードの実行でエラーが起きたら、[GitHub Releases](https://github.com/hoangsvit/google-ai/releases) の**公開済みリリース**を試せます。リリースノートを読み、Windows 向けの添付ファイルがあればダウンロードしてください。GitHub が自動生成する **Source code (zip)** しかない場合は ZIP をダウンロードして展開し、展開先で PowerShell を開いて次を実行します。

```powershell
.\run-all.ps1
```

**Source code (zip) はビルド済み `.exe` やインストーラーではありません。** 現在の作業フォルダーを上書きせず、**別のフォルダー**に保存してください。古いリリースには最近の修正が含まれない場合があります。Windows、Python、MuMuPlayer、ADB/Frida および決済に関する注意事項は変わりません。解決しない場合は[トラブルシューティング](docs/DETAILED-GUIDE.md)や [Issues](https://github.com/hoangsvit/google-ai/issues) を参照してください。

## macOS — インストールと起動

macOS では **Git**、**Python 3.10+**、**Android SDK Platform-Tools (ADB)** をインストールします（Homebrew: `brew install android-platform-tools`）。root 対応で Google Play Store と Google One が利用できる Android 端末または互換エミュレーターが必要です。Mac の **MuMuPlayer Pro は Apple Silicon 向け**で、Intel Mac は別の Android 環境が必要です。

**Terminal** で実行：

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
adb devices
sh run-macos.sh
```

`sh run-macos.sh` は **ステップ 0–5** を含む Textual 画面を開きます。`--check` は環境を確認し設定を変更する場合があり、`--list` はオファー照会のみです。`--step 2` は画面の初期選択だけで、**自動決済しません**。ステップ 2–5 は実際に請求される可能性があり、毎回確認が必要です。**Mac/MuMu 実機での決済は未検証です。** [Mac 詳細ガイド](docs/MACOS-PREVIEW.md) を参照。

## 3. ダッシュボードの使い方

ステップの実行中は、**Check Device & Offers**、**Run**、実行モードやステップの切り替えを一時的に無効にし、複数の処理が同時に始まらないようにします。Step 0 ではローカル設定が変更される場合があります。Step 1 は購入を開始しませんが、事前準備で ADB / Frida の設定が変わることがあります。次に進む前に Google Play で結果を確認してください。**Stop や Exit では、送信済みの決済を取り消せません。**


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

## 4. PowerShell コマンド（上級者向け）

**Windows 専用のコマンドです。** Mac では PowerShell を使わず、`run-macos.sh` と[macOS 向けガイド](docs/MACOS-PREVIEW.md)に従ってください。起動時に引数を指定すると、Textual 画面ではなく CLI モードが実行されます。

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

ログは `logs/`、レポートは `ultra0-report/` に保存されます。**アカウント情報、トークン、決済情報を含む生データを共有しないでください。** CI では静的テストや模擬環境での検証のみを行い、実際の購入が成功するかどうかは確認していません。

## コミュニティサポートと関連プロジェクト

ePlus AI Toolkit のインストールや使用に問題があれば、[ePlus の Telegram サポート・交流投稿](https://t.me/eplus_news/29)で相談したり、トラブルシューティング情報を交換したりできます。再現可能な不具合は [GitHub Issue](https://github.com/hoangsvit/google-ai/issues) で報告してください。**パスワード、OTP/2FA コード、オファー・購入トークン、個人情報を含むログ、カード情報を公開しないでください。** Google の公式サポートではありません。

**Google AI Pro の特典に参加できない場合：**別の ePlus.DEV プロジェクト [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub) で [Muse の招待コードを探す／共有する](https://muse.eplus.dev/) こともできます。**Muse は別サービス**であり、その招待コードは **Google AI Pro のサブスクリプションの代わりにならず、利用権を付与しません**。コードの有効性や地域・アカウント条件は保証されません。

## リポジトリの構成

これまでの手順との互換性を保つため、起動スクリプトと主要な Python モジュールはリポジトリのルートに配置しています。Windows では `run-all.ps1`、Mac では `run-macos.sh` を使ってください。

| ファイル・フォルダー | 内容 |
| --- | --- |
| `run-all.ps1` | Windows 用。Textual ダッシュボードと CLI を起動 |
| `run-macos.sh`、`ePlus-AI-Toolkit.command`、`macos_runner.py` | Mac 用。Steps 0–5 の起動・制御を担当。実機での決済は未検証 |
| `tui.py`、`tui_core.py`、`ultra0.py`、`setup_env.py`、`device_selector.py`、`query_sku.py` | 現在使用している Python の処理と補助ツール |
| [`tools/windows/`](tools/windows/README.md) | 必要な場合に使う Windows の手動セットアップ |
| [`legacy/windows/`](legacy/windows/README.md) | 以前の .bat ファイル。一部は `--force` でアカウント確認を省略するため、**実際の課金につながる可能性**があります |
| `scripts/`、`assets/` | 補助スクリプトと Android / Frida 用ファイル |
| `tests/`、`.github/workflows/`、`docs/` | テスト、GitHub Actions、ドキュメント |

## ドキュメントと開発への参加

[英語版 README](README.md) · [Install Wiki](https://github.com/hoangsvit/google-ai/wiki/Install) · [詳細ガイド](docs/DETAILED-GUIDE.md) · [原作者のステップ](docs/ORIGINAL-STEPS.md) · [免責事項](DISCLAIMER.md) · [セキュリティ](SECURITY.md) · [貢献](CONTRIBUTING.md) · [著作権表示](THIRD_PARTY_NOTICES.md)

[プロジェクト構成](docs/PROJECT.md)、[ダッシュボード／CLI](docs/USAGE.md)、[決済の安全](docs/SAFETY.md)、[作者のメモ](docs/AUTHOR-NOTES.md)、[AI エージェント規約](AGENTS.md)も参照してください。GitHub Actions は Python、PowerShell、Textual、模擬 Frida/Billing を検証しますが、**実際の Google Play 決済は行いません**。CI のテストに成功しても、実機で動作することやアカウントの利用資格は保証されません。

## クレジット

**原作者：**[@gylive](https://github.com/gylive) — [google-ultra](https://github.com/gylive/google-ultra)。**メンテナー：**[David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev)。元の MIT 著作権表示は `THIRD_PARTY_NOTICES.md` に保持しています。

[ドキュメント一覧](docs/README.md) · [旧版の日本語参考資料](docs/i18n/README.ja.md) · [決済の注意事項](docs/SAFETY.md)
