# Google AI Ultra 20x: US$19.99/month for 3 months

The reviewed third-party ZIP claims a Google AI Ultra 20x (30 TB) promotional plan with **US$19.99/month for three months** (three separate charges, US$59.97 total), followed by **US$199.99/month** starting in month four. The candidate Google Play product ID is `g1.ai.ultra.3months_ip_90p.acq`. This is a **third-party claim**: listing it does not prove Google offers it to the active account, in the active region, or at the stated terms.

## Two distinct plan groups

| Group | Steps | Charge type | Account requirement |
| --- | --- | --- | --- |
| **Google AI Pro — free trial, up to 24 months (reported)** | **2–5** | Claimed US$0 trial phases; possible separate temporary card holds. Not guaranteed. | Pro trial/extension conditions, checked by Google Play |
| **Google AI Ultra — paid introductory offer** | **6 only** | Claimed **US$19.99/month x 3**, then **US$199.99/month** | **Clean account** — according to the source, never previously used a Google One / AI free trial or introductory promotion |

The paid Ultra option **is not part of the Pro 24-month strategy**. The toolkit does not auto-detect historical trial use. For Ultra, it requires the user to **self-attest** that the Play account is clean before opening checkout; Google Play alone decides eligibility.

## Added: independent Ultra Step 6

The original Pro steps 0–5 are unchanged. Step **6 — Ultra 20x, US$19.99/month x 3** is separate; it is **not** part of the Pro 12+6+6-month sequence and does not stack a purchase token.

On **Windows**, choose Step 6 in the Textual dashboard (Advanced > One step only), or run:

```powershell
.\run-all.ps1 -Step 6 -Email account@example.com
```

On **macOS**, choose Step 6 in the same dashboard or, after preparing the environment, run:

```sh
python3 macos_runner.py --step 6 --confirmed --clean-account-confirmed
```

For a **read-only** query that cannot open checkout, run:

```sh
python ultra0.py --inspect-sku g1.ai.ultra.3months_ip_90p.acq
```

The optional paid step checks one exact SKU and the following offer metadata **before opening checkout**:

- First monthly phase: **USD 19.99**, exactly **3** billing cycles.
- Next monthly phase: **USD 199.99**, in the same currency.
- Offer must match uniquely. Different products, currencies, price amounts, phases or an ambiguous set of offers stop before checkout.

The paid Google Play screen is **manual-only**: the application does not tap **Subscribe** for the Ultra offer. Recheck today's amount, all first-three-month charges, renewal price, next renewal date, cancellation terms and correct Google Play account **on the actual Google Play screen**. A billing flow opening successfully does not prove any subscription was activated.

## Android environment

This offer does **not require MuMu 12 or Android 12** as a special plan rule. Use the supported Android device/emulator setup you already have with working **ADB, root, Frida**, **Google Play Store** and **Google One**. Device/ROM/Frida compatibility still varies. Do not silently force-install a particular Android image or emulator just for this plan.

The archive's described Ultra workflow **requires a clean account** that has never used any Google One / AI trial or introductory promotion. The toolkit therefore requires an explicit **self-declaration**, via the Ultra-only dashboard checkbox, the Windows Step 6 CLI prompt, or `--clean-account-confirmed` for direct Python/macOS paid Ultra execution. The toolkit **cannot verify that history**. It is an author-supplied condition, not proof of Google's current eligibility rules; Google Play makes the final decision. Do not use `--force` to skip account verification or bypass eligibility checks. The new Ultra mode refuses `--force`, stacking and old-token flags, and requires the current Play account to be verified.

## Source and verification

The ZIP's Ultra 30 TB 90%-off batch script used `--allow-paid` and `--force` together. It also implied subscription success from incomplete UI signals. **Those unsafe behaviors were not copied.** This implementation keeps checkout approval manual and does not claim to activate or extend service.

Only the requested US$19.99 plan is added. Other promotion SKUs from the ZIP were deliberately excluded.

The repository's offline tests can verify argument validation, exact product/pricing selection, manual-only paid checkout and staged workflow behavior. They cannot prove the offer exists for a real account or that a live transaction succeeds. Do not treat a green CI run as confirmation of Google Play billing.
