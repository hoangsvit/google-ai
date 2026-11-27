@echo off
setlocal
cd /d "%~dp0..\.."
echo Step 14: runs through the toolkit billing engine via run-all.ps1. Exact-offer checkout opens only on a match; Subscribe is manual in Google Play.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\..\run-all.ps1" -Step 14
set RESULT=%errorlevel%
pause
exit /b %RESULT%
