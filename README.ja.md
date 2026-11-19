# ePlus AI Toolkit — 日本語

[English](README.md) · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · **日本語** · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md)

Android・ADB・Frida・Google Play を使って Google AI Pro のオファーを確認する非公式ターミナルツールです。Windows が安定版、macOS ではステップ 0–5 を備えた開発版を `dev` で提供しています。

![ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **実際の請求が発生する可能性があります。** ステップ **2–5** は Google Play の決済画面を開き、Subscribe を自動操作することがあります。オファー表示や初回価格 0 は、無料・有効化・延長成功の証拠ではありません。実際のアカウント、当日の料金、更新後の価格と日付を確認してください。環境確認で Android/Frida/ネットワーク設定も変更される場合があります。

## Quick start

**Windows：**[MuMuPlayer](https://www.mumuplayer.com/download/) を別途導入し、ADB/root と Google Play/Google One を準備して PowerShell を実行：

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

**macOS 開発版：**Python 3.10+、ADB、root 対応 Android が必要です。実機 Mac/MuMu での決済動作は未検証です：

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
git switch dev
sh run-macos.sh
```

## Documentation

[日本語の詳細ガイド](docs/i18n/README.ja.md) · [ドキュメント一覧](docs/README.md) · [セットアップ](docs/INSTALLATION.md) · [Mac ガイド](docs/MACOS-PREVIEW.md) · [決済の注意事項](docs/SAFETY.md)

[リリース](https://github.com/hoangsvit/google-ai/releases) · [問題を報告](https://github.com/hoangsvit/google-ai/issues) · [貢献する](CONTRIBUTING.md) · [セキュリティ](SECURITY.md) · [免責事項](DISCLAIMER.md)

Original: [gylive/google-ultra](https://github.com/gylive/google-ultra). Maintainer: [@hoangsvit](https://github.com/hoangsvit) · [ePlus.DEV](https://eplus.dev). Not affiliated with Google or MuMuPlayer.
