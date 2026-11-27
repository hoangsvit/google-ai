@echo off
setlocal
cd /d "%~dp0..\.."
echo Step 7: official app offer review. No automatic checkout.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\..\run-all.ps1" -Step 7
set RESULT=%errorlevel%
pause
exit /b %RESULT%
