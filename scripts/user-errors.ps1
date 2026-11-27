#Requires -Version 5.1
# Friendly terminal messages. This file never runs ADB or Google Play actions.
function Get-UserIssue {
    param([string]$Code)
    if ([string]::IsNullOrWhiteSpace($Code)) { $Code = "unknown" }
    switch ($Code.ToLowerInvariant()) {
        { $_ -in @("payment_security_blocked", "checkout_security_blocked") } {
            return [pscustomobject]@{
                Title = "Google Play blocked this payment (OR-REH-04)"
                Action = "Check account security and Google Payments alerts. Do not retry paid steps yet."
            }
        }
        "already_subscribed" {
            return [pscustomobject]@{
                Title = "This Google AI Pro plan is already active"
                Action = "No extra months were confirmed. Check the renewal date in Google Play; do not repeat this step."
            }
        }
        "ineligible" {
            return [pscustomobject]@{
                Title = "This account is not eligible for the selected offer"
                Action = "Review the terms in Google Play. -Force cannot make the offer eligible."
            }
        }
        "purchase_unavailable" {
            return [pscustomobject]@{
                Title = "Google Play says this item is unavailable for purchase"
                Action = "Check the Play account, country and Google One availability. Do not repeat checkout blindly."
            }
        }
        "today_price_unverified" {
            return [pscustomobject]@{
                Title = "Could not confirm the amount due today"
                Action = "Review the checkout price on your Android screen. No Subscribe tap was confirmed."
            }
        }
        "trial_duration_unverified" {
            return [pscustomobject]@{
                Title = "Could not confirm the trial length"
                Action = "Review the duration shown by Google Play. The script stopped before confirming."
            }
        }
        "backup_payment_methods_prompt" {
            return [pscustomobject]@{
                Title = "Google Play asks about backup payment methods"
                Action = "Decide on that optional setting in Google Play. It is not subscription confirmation."
            }
        }
        "processing" {
            return [pscustomobject]@{
                Title = "Google Play is still processing"
                Action = "Check subscriptions and payment history before attempting any checkout again."
            }
        }
        "subscribe_button_not_found" {
            return [pscustomobject]@{
                Title = "The checkout button was not found"
                Action = "Check Google Play pricing, subscriptions, and payment history. No Subscribe action or subscription update was verified."
            }
        }
        "offer_not_available" {
            return [pscustomobject]@{
                Title = "The selected offer is not available"
                Action = "Check available offers using -Step 1. Do not assume the trial applies to this account."
            }
        }
        { $_ -in @("offer_query_failed", "offers_unavailable") } {
            return [pscustomobject]@{
                Title = "Could not load Google AI offers"
                Action = "Open Google One and Google Play, check the connection, then run -Step 1."
            }
        }
        "ui_capture_failed" {
            return [pscustomobject]@{
                Title = "Android UI capture failed"
                Action = "Close MuMu and reopen it, or restart the selected Android device. Wait for boot, unlock Android, open Google Play and run Check Device & Offers again from Step 1. Review subscriptions and payment history before retrying any paid step."
            }
        }
        "account_unavailable" {
            return [pscustomobject]@{
                Title = "Could not identify the Google Play account"
                Action = "Open the Play Store profile, then retry or specify -Email with the expected account."
            }
        }
        "account_mismatch" {
            return [pscustomobject]@{
                Title = "Google Play is using a different account"
                Action = "Select the intended account in the Play Store. No checkout was started."
            }
        }
        "device_missing" {
            return [pscustomobject]@{
                Title = "MuMu is not connected"
                Action = "Start MuMu, enable ADB debugging, and retry -Step 0."
            }
        }
        "device_ambiguous" {
            return [pscustomobject]@{
                Title = "More than one Android device is connected"
                Action = "Rerun with -Serial followed by an exact ID from adb devices."
            }
        }
        "app_missing" {
            return [pscustomobject]@{
                Title = "Google Play or Google One is missing"
                Action = "Enable the missing app in Android settings. Install Google One from the Play Store; if Play Store is missing, use a Google Play-enabled emulator image."
            }
        }
        "python_missing" {
            return [pscustomobject]@{
                Title = "Python is not available"
                Action = "Install Python 3.10 or later, reopen PowerShell, and try again."
            }
        }
        "adb_missing" {
            return [pscustomobject]@{
                Title = "Android Debug Bridge (ADB) is unavailable"
                Action = "Run python setup_env.py or install Android SDK platform-tools."
            }
        }
        "runtime_lookup_failed" {
            return [pscustomobject]@{
                Title = "Could not inspect the Android device"
                Action = "Restart Google Play and MuMu if needed, then run -Step 0 -Debug."
            }
        }
        "report_missing" {
            return [pscustomobject]@{
                Title = "The tool did not return a result"
                Action = "Check the local debug log. Verify Google Play before retrying any payment step."
            }
        }
        "add_account_failed" {
            return [pscustomobject]@{
                Title = "Could not add the Google account"
                Action = "Check Android sign-in and the Play Store profile before continuing."
            }
        }
        "add_account_error" {
            return [pscustomobject]@{
                Title = "Google account setup was interrupted"
                Action = "Check Android sign-in prompts and verify the intended Google Play account."
            }
        }
        "payment_method_not_confirmed" {
            return [pscustomobject]@{
                Title = "Could not verify the payment method"
                Action = "Review Google Play payment methods manually. No successful payment was verified."
            }
        }
        "play_account_switch_failed" {
            return [pscustomobject]@{
                Title = "Could not switch Google Play accounts"
                Action = "Select your intended Play Store account and run the offer check again."
            }
        }
        "account_unverified" {
            return [pscustomobject]@{
                Title = "Google Play account was not verified"
                Action = "Open the Play Store profile and verify the account before checkout."
            }
        }
        "wrong_account" {
            return [pscustomobject]@{
                Title = "Google Play is using the wrong account"
                Action = "Switch to the intended account and run Step 1 again."
            }
        }
        "frida_missing" {
            return [pscustomobject]@{
                Title = "Android instrumentation is not ready"
                Action = "Prepare the compatible Frida version and verify the Android connection."
            }
        }
        "billing_module_setup_failed" {
            return [pscustomobject]@{
                Title = "Billing module setup failed"
                Action = "Check authorized Android access and file permissions, then rerun the environment check. Review Google Play before retrying a paid step."
            }
        }
        "mumu_start_failed" {
            return [pscustomobject]@{
                Title = "MuMu startup failed"
                Action = "Check the preceding recovery message, existing instance selection and ADB debugging. Open the intended instance manually if needed."
            }
        }
        "environment_failed" {
            return [pscustomobject]@{
                Title = "Android environment check did not finish"
                Action = "Check ADB, Google One and Frida. Verify Google Play payments before retrying a paid step."
            }
        }
        "confirmation_required" {
            return [pscustomobject]@{
                Title = "Approval is required to continue"
                Action = "Use the on-screen confirmation for each paid step."
            }
        }
        "launch_failed" {
            return [pscustomobject]@{
                Title = "Could not open Google Play checkout"
                Action = "The app did not confirm checkout opened. Check Google One and Google Play, then verify subscriptions and payment history before retrying."
            }
        }
        "billing_flow_error" {
            return [pscustomobject]@{
                Title = "Google Play could not open checkout"
                Action = "Review the Android screen and payment history before trying this step again."
            }
        }
        "billing_launch_error" {
            return [pscustomobject]@{
                Title = "Could not start Google Play checkout"
                Action = "Check Google One and Android diagnostics. Verify payments before another attempt."
            }
        }
        "activity_lookup_failed" {
            return [pscustomobject]@{
                Title = "Could not access the Google One screen"
                Action = "Bring Google One to the foreground and check ADB/Frida in technical details."
            }
        }
        "no_activity" {
            return [pscustomobject]@{
                Title = "Google One is not ready"
                Action = "Open Google One on Android and rerun the device and offer check."
            }
        }
        "app_not_started" {
            return [pscustomobject]@{
                Title = "Google One could not be opened"
                Action = "Close MuMu and reopen it. Wait for Android to finish booting, then run Check Device & Offers again from Step 1."
            }
        }
        "checkout_account_mismatch" {
            return [pscustomobject]@{
                Title = "Checkout is using a different account"
                Action = "Close checkout, select the intended account in Play Store and Google One, then run Check Device & Offers again. Verify earlier purchases in Google Play."
            }
        }
        "checkout_account_unverified" {
            return [pscustomobject]@{
                Title = "Checkout account could not be read"
                Action = "Expand the Google Play checkout account details and verify the email. Close checkout and run Check Device & Offers again before another attempt."
            }
        }
        "play_store_not_started" {
            return [pscustomobject]@{
                Title = "Google Play Store could not be opened"
                Action = "Close MuMu and reopen it. Wait for Android to finish booting, then run Check Device & Offers again from Step 1."
            }
        }
        "subscription_update_unavailable" {
            return [pscustomobject]@{
                Title = "Could not prepare the subscription change"
                Action = "Review the existing Google Play subscription before another paid attempt."
            }
        }
        "checkout_not_visible" {
            return [pscustomobject]@{
                Title = "Could not see the Google Play checkout screen"
                Action = "Inspect the Android screen and payment history before retrying."
            }
        }
        "price_unverified" {
            return [pscustomobject]@{
                Title = "Could not verify the checkout price"
                Action = "Check today's amount and the renewal price in Google Play."
            }
        }
        "research_review_only" {
            return [pscustomobject]@{
                Title = "Research step requires official app review"
                Action = "Direct research checkout is unavailable. Verify offer availability and full terms in the official app."
            }
        }
        "manual_confirmation_required" {
            return [pscustomobject]@{
                Title = "Manual confirmation required in Google Play"
                Action = "Automatic Subscribe is disabled. Review the terms and confirm on Android. Verify the subscription before starting another step."
            }
        }
        "checkout_not_confirmed" {
            return [pscustomobject]@{
                Title = "The purchase was not confirmed"
                Action = "Check Google Play Subscriptions before retrying. No extension is verified."
            }
        }
        { $_ -in @("checkout_not_visible", "price_unverified", "unknown") } {
            return [pscustomobject]@{
                Title = "Could not confirm the checkout"
                Action = "Check the Google Play screen and subscription history before trying again."
            }
        }
        default {
            return [pscustomobject]@{
                Title = "Could not complete this step"
                Action = "Check the Android screen and local debug log before retrying."
            }
        }
    }
}

function Get-FailureCode {
    param([string]$ErrorMessage)
    if ($ErrorMessage -like "MuMu startup failed*") { return "mumu_start_failed" }
    if ($ErrorMessage -eq "Android UI capture failed") { return "ui_capture_failed" }
    if ($ErrorMessage -eq "Billing module setup failed") { return "billing_module_setup_failed" }
    if ($ErrorMessage -match '(?i)Python not found') { return "python_missing" }
    if ($ErrorMessage -match '(?i)adb\.exe was not found|ADB device discovery failed') { return "adb_missing" }
    if ($ErrorMessage -match '(?i)No online ADB devices|selected serial.*not online') { return "device_missing" }
    if ($ErrorMessage -match '(?i)Cannot select a single Android device|Invalid device number') { return "device_ambiguous" }
    if ($ErrorMessage -match '(?i)Android package missing|Android package.*unavailable') { return "app_missing" }
    if ($ErrorMessage -match '(?i)Play account mismatch|Play Store account changed') { return "account_mismatch" }
    if ($ErrorMessage -match '(?i)Cannot identify the active Google Play account|No valid email|Invalid Play Store account') { return "account_unavailable" }
    if ($ErrorMessage -match '(?i)(?:Offer query did not complete|Could not refresh the offer list for Step [2-5]): (app_not_started|play_store_not_started)\s*$') { return $Matches[1].ToLowerInvariant() }
    if ($ErrorMessage -match '(?i)Offer query did not complete|Could not refresh the offer list') { return "offer_query_failed" }
    if ($ErrorMessage -match '(?i)No report produced') { return "report_missing" }
    if ($ErrorMessage -match '(?i)Runtime lookup failed|No machine-readable runtime result') { return "runtime_lookup_failed" }
    return "unknown"
}

function Show-UserIssue {
    param(
        [string]$Code,
        [string]$Details = "",
        [bool]$DebugMode = $false
    )
    $issue = Get-UserIssue -Code $Code
    # Structured marker is for the TUI parser, never direct CLI users.
    if ($env:EPLUS_TUI -eq "1" -and $Code -match '^[a-z_]+$') {
        Write-Host ("EPLUS_ISSUE:{0}" -f $Code)
    }
    Write-Host ""
    Write-Host ("  ! {0}" -f $issue.Title) -ForegroundColor Yellow
    Write-Host ("    Next: {0}" -f $issue.Action) -ForegroundColor Gray
    if ($DebugMode) {
        Write-Host ("    Code: {0}" -f $Code) -ForegroundColor DarkGray
        if ($Details) { Write-Host ("    Details: {0}" -f $Details) -ForegroundColor DarkGray }
    }
}
