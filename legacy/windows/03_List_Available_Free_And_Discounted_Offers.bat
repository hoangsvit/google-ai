@echo off
setlocal
cd /d "%~dp0..\.."
where adb >nul 2>&1
if errorlevel 1 (
  echo ADB not found. Install Android Platform Tools and add them to PATH.
  exit /b 1
)
adb get-state 2>nul | findstr /x /c:"device" >nul
if errorlevel 1 (
  echo Connect and authorize exactly one Android device.
  exit /b 2
)
adb shell am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -p com.google.android.apps.subscriptions.red
if errorlevel 1 (
  echo Open Google One manually on the Android device.
  exit /b 3
)
echo Review offers, eligibility, price and renewal terms in the app.
echo This shortcut does not select a plan or start checkout.
exit /b 0
