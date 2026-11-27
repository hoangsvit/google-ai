@echo off
setlocal
cd /d "%~dp0..\.."
where python >nul 2>&1
if errorlevel 1 (
  echo Python not found on PATH.
  exit /b 1
)
python -c "from device_diagnostics import open_google_one_app; s=open_google_one_app(); print(s); raise SystemExit(0 if s == 'opened' else 3)"
if errorlevel 1 (
  echo Open Google One manually on the Android device.
  exit /b 3
)
echo Review offers, eligibility, price and renewal terms in the app.
echo This shortcut does not select a plan or start checkout.
exit /b 0
