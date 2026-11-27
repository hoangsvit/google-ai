@echo off
setlocal
cd /d "%~dp0..\.."
echo Step 17: runs through the toolkit billing engine via run-all.ps1. Exact-offer checkout opens only on a match; Subscribe is manual in Google Play.
powershell.exe -NoProfile -File "%~dp0..\..\run-all.ps1" -Step 17
set RESULT=%errorlevel%
pause
exit /b %RESULT%
