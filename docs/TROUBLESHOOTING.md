# Troubleshooting, results and community support

[Documentation home](README.md) · [Repository README](../README.md) · [Safety](SAFETY.md)

## Troubleshooting and results

| Problem or result | What to check |
| --- | --- |
| **MuMu / ADB not detected** | Install/start MuMu separately, enable root/ADB, verify the correct connected Android instance and authorization. |
| **Frida setup failure** | Review technical details; Frida **16.5.9** must be compatible with the host and device. |
| **No offers / `offer_query_failed`** | Open Google One and Google Play on the target Android instance and run Step 1 again. |
| **Account not verified / wrong account** | Inspect the active Google Play profile; do not bypass verification. |
| **Checkout submitted; check Google Play** | The tool attempted to submit checkout; it has **not** verified a successful subscription or extension. |
| **`already_subscribed` / `ineligible`** | Stop; do not retry other checkout stages based on unverified extension claims. |
| **Payment/security error (e.g. OR-REH-04)** | Follow Google Account/Payments security instructions. Do not repeatedly retry. |
| **Unicode output error** | Update the repository; the maintained Windows launcher configures Python UTF-8 output for piped status symbols. |

Verify subscription, payment amount, currency and renewal terms under **[Google Play Subscriptions](https://play.google.com/store/account/subscriptions)**. For developer-facing status codes and advanced platform/Frida problems, see [Detailed setup and troubleshooting](DETAILED-GUIDE.md).

**Platform support:** The repository contains Windows and macOS launchers. Mac host CI does not establish real Android/MuMu compatibility or Google Play payment success; see the [Mac setup and limitations](MACOS-PREVIEW.md).

## Community support and related projects

If you need help installing or using ePlus AI Toolkit, see the [ePlus Telegram support/discussion post](https://t.me/eplus_news/29) to get in touch and exchange troubleshooting tips with the community. You can also [open a GitHub Issue](https://github.com/hoangsvit/google-ai/issues) for reproducible bugs. **Never post passwords, 2FA codes, purchase/offer tokens, full unredacted logs, or payment-card details.** Community support is not an official Google support channel.

**Can't access the Google AI Pro offer?** You may also explore [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub) ([browse or share Muse invite codes](https://muse.eplus.dev/)), another ePlus.DEV community project. Muse invite codes are for a **separate service**, are not a substitute for Google AI Pro subscriptions, and do **not** unlock or guarantee Google AI Pro access. Muse code availability and eligibility may vary.
