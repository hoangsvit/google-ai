@echo off
setlocal
where python >nul 2>&1
if errorlevel 1 (
  echo Python not found on PATH.
) else (
  python --version
)
where adb >nul 2>&1
if errorlevel 1 (
  echo ADB not found on PATH.
  exit /b 1
)
adb get-state 2>nul | findstr /x /c:"device" >nul
if errorlevel 1 (
  echo Connect and authorize exactly one Android device in ADB.
  exit /b 2
)
adb shell pm path com.android.vending 2>nul | findstr /b /c:"package:" >nul
if errorlevel 1 (
  echo Google Play Store not detected.
) else (
  echo Google Play Store detected.
)
adb shell pm path com.google.android.apps.subscriptions.red 2>nul | findstr /b /c:"package:" >nul
if errorlevel 1 (
  echo Google One not detected.
) else (
  echo Google One detected.
)
endlocal
