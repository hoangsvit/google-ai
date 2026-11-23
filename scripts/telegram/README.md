# ePlus AI Toolkit — Private Telegram Bot

This is an **operator interface to the existing toolkit**, not a replacement for an Android worker. It can run on Windows/macOS/Linux alongside a connected Android device or on an already compatible cloud VM. It does not create an emulator.

## Commands

| Command | Behavior |
| --- | --- |
| /start /help | Show commands and warnings |
| /status | Uptime, ADB state, number of devices |
| /device /check | Non-purchasing ADB, Frida, Play Store and Google One diagnostics |
| /steps | List Steps 0–5 and checkout restrictions |
| /offers | Explain the optional offer-listing command |
| /offers confirm | Trigger list-only Step 1 on one device if explicitly enabled by server owner |

**No Telegram-based checkout:** Steps 2–5 are not supported by the bot. No credentials, payment details, account identifiers, billing tokens, full reports or unredacted output are sent over Telegram. Only the IDs in the allowlist, in their private chats, may send commands. Group or channel messages are ignored.

## Setup

1. Open Telegram and privately message the official @BotFather. Send /newbot and store the returned bot token securely.
2. Open a private chat with your newly created bot and send /start.
3. Find your numeric Telegram user ID. Before starting the bot, read the official Telegram Bot API getUpdates response and extract message.from.id for your own message, or use a trusted Telegram ID lookup. Do not share raw getUpdates responses or your token.
4. Run with Python 3.10+ from the repository root.

Linux/macOS:

~~~bash
cd google-ai
read -rs -p 'Bot token: ' TELEGRAM_BOT_TOKEN; echo
export TELEGRAM_BOT_TOKEN
export TELEGRAM_ALLOWED_USER_IDS="123456789"  # Change to your own ID
python3 telegram_bot.py
~~~

Windows PowerShell:

~~~powershell
cd google-ai
$env:TELEGRAM_BOT_TOKEN = Read-Host "Bot token"
$env:TELEGRAM_ALLOWED_USER_IDS = "123456789"
python telegram_bot.py
~~~

The bot uses official Telegram getUpdates long polling, so **only one running instance** per token is supported. If that token already has a configured webhook, the bot refuses to start; switch away from webhook mode deliberately before using polling. No publicly accessible incoming port is required. Official documentation: https://core.telegram.org/bots/api

## Optional offer listing

Disabled by default. Explicitly set the following on the trusted bot host and restart:

~~~bash
export TELEGRAM_ALLOW_OFFER_CHECKS=1
python3 telegram_bot.py
~~~

In a permitted private chat, send /offers confirm. The bot will execute **only** the existing list-only engine, equivalent to:

~~~bash
python3 ultra0.py --list --account current@device --no-add --no-switch --serial "<connected-serial>"
~~~

Only one online Android device is accepted. The check may prepare ADB root, install/repair Frida and change Android network/app state. It does **not request payment**, but it can have local Android side effects. The bot returns only a sanitized report status, not any account data, actual offers or checkout details. Do not use the same device or report directory simultaneously from the TUI and Telegram bot. Inspect the Android screen after every check.

## Cloud deployment

Prerequisite: a compatible VM with the toolkit already installed and an authorized Android device/emulator. The experimental GCE emulator scripts are being developed separately in PR #80 and do not guarantee Google Play + root + Frida support. Running the Telegram bot does not solve those compatibility limitations.

For a Linux VM with systemd:

1. Create a **dedicated, non-root** account with access to the repo and only its authorized Android device. Confirm ADB works as this user (a root-only ADB connection is insufficient).
2. Put TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USER_IDS and optional TELEGRAM_ALLOW_OFFER_CHECKS=1 into /etc/eplus-ai-telegram.env, owned by root with permission 0600.
3. Copy scripts/telegram/eplus-ai-telegram.service.example to /etc/systemd/system/eplus-ai-telegram.service and adapt the service user, Python path and repo directory.
4. Run: sudo systemctl daemon-reload
5. Run: sudo systemctl enable --now eplus-ai-telegram
6. Check: sudo systemctl status eplus-ai-telegram

The VM needs outbound HTTPS to api.telegram.org. Do not open ADB, Frida, HTTP or WebRTC ports to the Internet for this bot. Cloud Shell is not a reliable production daemon host.

## Safety & limitations

- No arbitrary shell commands, account credentials, passwords, 2FA or card inputs through Telegram.
- No remote checkout, subscription extension or forced retries.
- Diagnostic replies omit device serial, file paths, account names and unredacted logs.
- Long polling must not run in parallel with a webhook or another polling instance.
- This is a **single-operator management bot**; a shared multi-user cloud platform needs worker/session isolation, authorization and per-user auditing first.
- A list-only report does not prove free subscription eligibility or activation.
- If Android/Google Play/Frida fail on a cloud emulator, stop and diagnose compatibility; do not bypass account integrity or payment-security protections.

See SECURITY.md and the toolkit's original README for payment warnings and supported platforms.
