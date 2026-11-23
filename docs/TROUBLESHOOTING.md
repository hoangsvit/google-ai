# Troubleshooting, results and community support

[Documentation home](README.md) · [Repository README](../README.md) · [Safety](SAFETY.md)

## Troubleshooting and results

| Problem or result | What to check |
| --- | --- |
| **MuMu / ADB not detected** | Install/start MuMu separately, enable root/ADB, verify the correct connected Android instance and authorization. |
| **Frida setup failure** | Review technical details; Frida **16.5.9** must be compatible with the host and device. |
| **No offers / `offer_query_failed`** | Open Google One and Google Play on the target Android instance and run Step 1 again. |
| **Google One or Google Play Store could not be opened** | The read-only offer check tries reopening the app once. If that fails in MuMu, close and reopen MuMu, wait for Android to finish booting, then run **Check Device & Offers** again from Step 1. On other devices, restart Android before running the check again. |
| **MuMu is open but ADB has no device** | When a Windows stage starts with no online ADB device, the toolkit tries the existing local emulator connection routine, then reads the ADB list again. If it still fails, check MuMu ADB debugging and run **Check Device & Offers** again. |
| **Frida connection error during Step 1** | The read-only query reconnects Frida and restarts Google One once for certain transient connection failures. If it still fails, open Debug and check ADB, Frida and Google One on the selected device. Paid checkout is never retried automatically. |
| **Item not available for purchase** | Google Play did not make the item available. Check the signed-in Play account, Play country and Google One availability; this message alone does not identify the cause. |
| **Google One or Play Store missing** | Enable the app in Android settings. Install Google One from Google Play; if Play Store is missing, use an emulator image with Google Play included. |
| **Steps 2–5 are locked** | Connect the Android device and complete **Check Device & Offers** with a verified Play account. The paid stage checks the device and account again; an earlier check does not guarantee the device remains connected. |
| **Account not verified / wrong account** | Inspect the active Google Play profile; do not bypass verification. |
| **Checkout account missing / different** | Compare the checkout email with the selected account. Close checkout, select the intended Play Store and Google One profiles, then repeat Step 1. |
| **Checkout submitted; check Google Play** | The tool attempted to submit checkout; it has **not** verified a successful subscription or extension. |
| **`already_subscribed` / `ineligible`** | Stop; do not retry other checkout stages based on unverified extension claims. |
| **Payment/security error (e.g. OR-REH-04)** | Follow Google Account/Payments security instructions. Do not repeatedly retry. |
| **Unicode output error** | Update the repository; the maintained Windows launcher configures Python UTF-8 output for piped status symbols. |

The disconnected-device popup includes **Retry connection**. While it checks, the button displays **Retrying…** and elapsed seconds. A successful connection closes the popup. If it fails, the popup offers MuMu restart guidance and another retry.

Verify subscription, payment amount, currency and renewal terms under **[Google Play Subscriptions](https://play.google.com/store/account/subscriptions)**. For developer-facing status codes and advanced platform/Frida problems, see [Detailed setup and troubleshooting](DETAILED-GUIDE.md).

**Platform support:** See the [Mac setup and limitations](MACOS-PREVIEW.md) and [Linux setup and USB troubleshooting](LINUX.md). Real Mac/MuMu checkout and Linux end-to-end device validation remain pending.

## Community support and related projects

If you need help installing or using ePlus AI Toolkit, see the [ePlus Telegram support/discussion post](https://t.me/eplus_news/29) to get in touch and exchange troubleshooting tips with the community. You can also [open a GitHub Issue](https://github.com/hoangsvit/google-ai/issues) for reproducible bugs. **Never post passwords, 2FA codes, purchase/offer tokens, full unredacted logs, or payment-card details.** Community support is not an official Google support channel.

**Can't access the Google AI Pro offer?** You may also explore [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub) ([browse or share Muse invite codes](https://muse.eplus.dev/)), another ePlus.DEV community project. Muse invite codes are for a **separate service**, are not a substitute for Google AI Pro subscriptions, and do **not** unlock or guarantee Google AI Pro access. Muse code availability and eligibility may vary.
