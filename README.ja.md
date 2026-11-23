# ePlus AI Toolkit — 日本語

<!-- Source README.md git-blob: 4f68b0ea54146c62a96a97b322a6c8cab816547e -->

[English](README.md) · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · **日本語** · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md)


> **原文：** [英語版 README](README.md)。この日本語版では、操作方法と注意点を分かりやすく説明しています。コマンドや技術的な条件は原文に合わせていますが、記載と実際の動作が異なる場合はコードと英語版をご確認ください。

**ePlus AI Toolkit** は、Android 端末上の Google One / Google Play で表示される Google AI Pro の特典を確認するためのツールです。**Windows** では PowerShell、**macOS** では Terminal（zsh/bash）から起動します。画面操作用の Textual UI とコマンドライン操作には、共通の Python・ADB・Frida エンジンを使用しています。

![ePlus AI Toolkit の画面](images/terminal-ui-overview.png)

> [!CAUTION]
> **非公式ツールです。実際の料金が発生する可能性があります。** **Step 2〜5** は Google Play の実際の購入画面を開き、条件によって **Subscribe（定期購入）** を自動タップする場合があります。オファーの表示、初回料金 0、またはチェックアウト送信の表示は、**対象資格・無料提供・契約成立・更新成功の証拠ではありません**。実行前に Google Play でアカウント、今日の請求額、更新料金、次回請求日を確認してください。停止操作は送信済みの取引を取り消しません。

> [!NOTE]
> **必要な利用可能残高の目安は最低 3 米ドルです。3 米ドルの一括決済ではなく、1 米ドルずつ計 3 回の取引です。** 報告されている **24 か月**の例では、Step 2（最初の 12 か月）、Step 3（+6 か月）、Step 4（さらに +6 か月）で、それぞれ**カード確認または決済として 1 米ドルの取引**が発生します。合計は **3 × US$1 = US$3** です。ただし、1 米ドルが確定請求ではなく一時的な仮承認の場合もあり、金額は銀行・アカウント・Google Play の条件によって異なることがあります。**最低 3 米ドルはこの報告例の目安であり、固定手数料や 24 か月の利用保証ではありません。** 仮承認によって利用可能残高が減り、解除には銀行により通常 **1～14 営業日**かかります。各ステップの後に Google Play で取引状態と更新日を確認してください。任意の Step 5 は**この 3 回に含みません**。[Google Play の公式説明](https://support.google.com/googleplay/answer/6224192?hl=en)。

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

## Linux — インストールと起動

Ubuntu x86_64 では Git、`venv` と `pip` が使える Python 3.10 以降、Android SDK Platform-Tools を用意します。`adb` を `PATH` に追加するか、実行ファイルを `ADB_PATH` で指定してください。Google Play ストアと Google One が入った root 化済みの Android 端末を USB で接続します。USB デバッグを有効にし、端末のロックを解除して接続を許可します。ADB に `device` と表示される端末が 1 台であることを確認してください。

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
git switch feature
adb devices
sh run-linux.sh
```

`run-linux.sh` を含むバージョンを使用してください。起動スクリプトはダッシュボードを開き、指定バージョンの Textual と Frida 16.5.9 をローカルの `.venv` にインストールします。Ubuntu で仮想環境を作成できない場合は、`python3-venv` または使用中の Python に対応する venv パッケージをインストールしてください。

- `sh run-linux.sh --check` は Step 0 を実行します。Android、Frida、ネットワークの設定が変わる場合があります。
- `sh run-linux.sh --list` は Step 1 を実行して特典を一覧表示します。決済は開始しませんが、Android 環境の準備が行われる場合があります。
- `sh run-linux.sh --step 3` は Step 3 を選択した状態で詳細設定を開きます。`sh run-linux.sh --sequence` は Step 2 からのガイド付き設定を開きます。どちらもステップを自動実行しません。

**Android 16 以降:** 指定バージョンの Frida 16.5.9 は Android 16 に対応していないため、Linux の起動スクリプトは端末のセットアップを開始せずに停止します。USB 接続は **Diagnose Android connection** で確認できます。

**Steps 2–5 では、Google Play で実際に請求が発生することがあります。** 各ステップで個別に承認し、現在の Play アカウントと、直前の照会で対象と完全に一致する特典の初回期間の価格が 0 であることを確認する必要があります。次のステップに進む前に、Google Play で登録状況と更新日を確認してください。Linux の決済は模擬テストで検証しており、実機での一連の動作確認は未完了です。 [Linux の設定、USB のトラブル対処と検証](docs/LINUX.md).


## 3. ダッシュボードの使い方

ステップの実行中は、**Check Device & Offers**、**Run**、実行モードやステップの切り替えを一時的に無効にし、複数の処理が同時に始まらないようにします。Step 0 ではローカル設定が変更される場合があります。Step 1 は購入を開始しませんが、事前準備で ADB / Frida の設定が変わることがあります。次に進む前に Google Play で結果を確認してください。**Stop や Exit では、送信済みの決済を取り消せません。**


**Check Device & Offers** を押すと **Step 1 — Available offers** が実行され、オファーを照会します。**購入処理は開始しません**。**Live Status** と **Show technical details** で進行状況を確認します。ログ更新が 30 秒ない場合の警告は、フリーズの確定ではありません。

画面が待機中は、既存の ADB 接続を約5秒ごとに確認します。ADB または Android 端末が見つからない場合は、対処方法をポップアップで案内します。確認は自動的に続き、端末の状態が更新されますが、再接続だけで決済ステップは解除されません。ステップ実行中や別のダイアログ表示中は監視を一時停止します。バックグラウンドでのインストールや端末への接続は行いませんが、`adb devices` により PC 上の ADB サーバーが起動する場合があります。

Windows で **Check Device & Offers** を実行すると ADB を探し、必要に応じて公式の Android SDK Platform-Tools のダウンロードを試みます。ダウンロードやインストールに失敗した場合は **Show technical details** を確認してください。macOS では Mac 向けの手順で Platform-Tools をインストールします。MuMu は別途インストールして起動し、root と ADB デバッグを有効にして、Google Play と Google One にログインしてください。

新しい Step 1 の確認でオファーが取得され、Play アカウントが確認できた場合に限り、Step 2–5 が解除されます。12か月オファー `12months-eft` の初回期間が 0 の場合は、完了ポップアップとメイン画面に **Continue to Step 2** が表示されます。それ以外の場合はオファー一覧を確認してください。このボタンは別の確認画面を開くだけで、適用資格や最終料金を保証するものではありません。決済リクエスト後は Google Play で契約、更新日、実際の料金を確認してから **Verified in Google Play → Next** を選んでください。以降の各ステップでも個別の確認が必要です。再確認、決済ステップの失敗、端末の変更により、決済ステップが再びロックされる場合があります。

**Choose another step** のモード：

初期設定では選択したステップだけを実行します。ガイド付きの連続実行モードは **Choose another step** 内のステップ一覧の最後にある **More run options…** を選ぶと表示されます。

| モード | 動作 |
| --- | --- |
| **Stop after this step** | 選択した Step 0〜5 だけを実行 |
| **Offer the next step** | 選択した Step 2〜5 から確認付きのフローを開始 |
| **Start at Step 2** | Step 2 から確認付きフローを開始。Step 5 は任意 |

| Step | 内容 | リスク |
| --- | --- | --- |
| **0 — Environment** | Android / ADB / Frida の診断・準備 | 購入は行わないが環境設定を変更し得る |
| **1 — Available offers** | Google Play のオファー照会 | 購入は行わないが事前準備は環境を変更し得る |
| **2 — Pro 12 months** | オリジナルの 12 か月オファー処理 | **課金の可能性** |
| **3 — Pro +6 months** | オリジナルの契約更新処理 | **課金の可能性** |
| **4 — Pro +6 months (second)** | 追加の契約更新処理 | **課金の可能性** |
| **5 — Optional +6 months** | 任意の追加更新処理 | **課金の可能性** |

**報告されている 24 か月の例（Google Play での確認が必要）：**

| Step | 適用された場合の累計期間 | 個別の取引 |
| --- | --- | --- |
| **2 — Pro 12 months** | 最初の **12 か月** | **1 米ドル**（1 回目） |
| **3 — Pro +6 months** | 合計 **18 か月** | **1 米ドル**（2 回目） |
| **4 — Pro +6 months (second)** | 合計 **24 か月** | **1 米ドル**（3 回目） |
| **Step 4 までの合計** | 確認できた場合 **24 か月** | **3 × US$1 = US$3**。3 米ドルの一括決済ではありません |

**任意の Step 5 はこの 3 回に含まれません。** 表示期間やカードの仮承認だけでは更新成功を確認できません。各 Step の後に Google Play の契約と更新日を確認してください。

月数は**従来のステップ名**であり、延長を保証するものではありません。既に契約がある場合、**Step 2 を再実行しないでください**。

TUI では**購入ステップごとに明示的な承認**が必要です。チェックアウトを送信した旨が表示されても、[Google Play の定期購入](https://play.google.com/store/account/subscriptions)で現在の契約、料金、更新日を確認してください。実際に変更を確認した場合のみ **Verified in Google Play → Next** を選びます。ツール単体では契約成立を証明できません。

**Stop / Exit：**Step 0〜1 の Stop はローカル処理の中止を要求します。Step 2〜5 の **Stop after this step** は後続ステップを止めますが、**処理中の決済を強制終了しません**。決済中の **Q / Exit** は現在の処理終了後に終了します。**D** は詳細ログ、**R** は選択中のモード実行です。

### 端末情報、アカウント、履歴

Device 欄には、取得できた Android のバージョン、SDK、ABI、ADB 接続情報が表示されます。マウスを重ねると詳細を確認できます。Account 欄の横にある **Choose account** は Android にログイン済みのアカウントを一覧表示します。Play Store と Google One の両方で目的のアカウントを選び、Step 1 を再実行してください。Play Store が使用中のプロフィールのメールアドレスを明示している場合、その情報で識別します。

操作欄は内容に合わせた高さになり、残りを **Live Status** が使用します。最新の処理状況が先頭に表示されます。**Show technical details** のログは新しい行まで自動スクロールします。メインボタンと **Run this step** には実行中のステップと経過秒数が表示されます。Windows では、特典確認中の環境チェックが完了すると Step 0 にチェックが付きます。新しい確認結果が不足している場合は、緑色の **Check Device & Offers — Step 1** が表示されます。

**Recent history** は開始、結果、**Verified in Google Play → Next** の操作を `logs/stage-history/` に保存します。起動時には最新の保存履歴が表示され、アカウントを選ぶとそのアカウントの履歴になります。**↺** は以前に実行を試みたステップです。履歴だけでは契約成立を確認できず、支払い操作も有効になりません。再起動後やアカウント変更後には Step 1 を再実行してください。履歴保存機能の追加前の実行は復元できません。

接続切れの画面には **Retry connection** があり、処理中は **Retrying…** と経過秒数を表示します。**Got it** で閉じられます。Windows ではローカルのエミュレーターへの再接続を試みます。ステップ開始時に ADB 端末が見つからない場合も同様です。参照処理でアプリが起動しない場合は一度だけ再起動を試みます。失敗した場合は MuMu を閉じて開き直し、Android の起動完了後に Step 1 を再実行してください。特典照会前には Google One を再起動します。Play Store が既に利用可能なら、そのまま使用します。**Reload toolkit** は処理待機中の画面をローカルのコードで再起動し、新しいセッションを開始します。

**Subscribe** を自動で押す前に、支払い画面のメールアドレス、本日の合計がゼロであること、試用期間が予定どおりであることを確認します。要求した特典も一致する必要があります。メールがない場合や異なる場合は自動操作を止め、手動確認を求めます。支払いステップごとに個別の承認が必要です。送信後は Google Play で契約、更新日、請求を確認してください。3 回のカード確認に関する案内は支払い承認画面に表示されます。

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
