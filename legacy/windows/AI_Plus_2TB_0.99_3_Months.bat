@echo off
setlocal
cd /d "%~dp0..\.."
echo Step 11: official app offer review. No automatic checkout.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\..\run-all.ps1" -Step 11
set RESULT=%errorlevel%
pause
exit /b %RESULT%
