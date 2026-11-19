# ePlus AI Toolkit — 日本語

[English](README.md) · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · **日本語** · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md)

Android・ADB・Frida・Google Play を使って Google AI Pro のオファーを確認する非公式ターミナルツールです。Windows が安定版、macOS ではステップ 0–5 を備えた開発版を `dev` で提供しています。

![ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **実際の請求が発生する可能性があります。** ステップ **2–5** は Google Play の決済画面を開き、Subscribe を自動操作することがあります。オファー表示や初回価格 0 は、無料・有効化・延長成功の証拠ではありません。実際のアカウント、当日の料金、更新後の価格と日付を確認してください。環境確認で Android/Frida/ネットワーク設定も変更される場合があります。

## Windows のインストール

1. **Python 3.10+**、**Git**、PowerShell 5.1+、[Windows 版 MuMuPlayer](https://www.mumuplayer.com/download/) をインストールします。
2. Android インスタンスで **root/ADB デバッグ**を有効にし、**Google Play Store** と **Google One** にログインします。
3. **PowerShell** を開いて実行：

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

## macOS のインストール

1. **Python 3.10+**、**Git** と **Android SDK Platform-Tools (ADB)** を導入します。Homebrew があれば `brew install android-platform-tools`。
2. root 対応で Google Play Store/Google One が使える Android デバイスか互換エミュレーターを用意します。Mac の **MuMuPlayer Pro は Apple Silicon 向け**です。Intel Mac は別の Android 環境が必要です。
3. **Terminal** を開いて実行：

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
sh run-macos.sh
```

Mac のランチャーは `.venv` に Python 依存関係を導入します。ステップ 0–5 は実装済みですが、**実機 Mac/MuMu での決済は未検証**です。[Mac の導入手順](docs/MACOS-PREVIEW.md)をご覧ください。

## 初回起動（両 OS 共通）

**Check Device & Offers** でオファーを確認（Step 1、決済なし）。Step 0 は ADB/Frida/Android 設定を変更する場合があります。**Steps 2–5 は実際に請求される可能性があります**。Google Play の条件を必ず確認してください。

## ドキュメント

[日本語の詳細ガイド](docs/i18n/README.ja.md) · [ドキュメント一覧](docs/README.md) · [セットアップ](docs/INSTALLATION.md) · [Mac ガイド](docs/MACOS-PREVIEW.md) · [決済の注意事項](docs/SAFETY.md)

[リリース](https://github.com/hoangsvit/google-ai/releases) · [問題を報告](https://github.com/hoangsvit/google-ai/issues) · [貢献する](CONTRIBUTING.md) · [セキュリティ](SECURITY.md) · [免責事項](DISCLAIMER.md)

Original: [gylive/google-ultra](https://github.com/gylive/google-ultra). Maintainer: [@hoangsvit](https://github.com/hoangsvit) · [ePlus.DEV](https://eplus.dev). Not affiliated with Google or MuMuPlayer.
