@echo off
setlocal
title ePlus AI Toolkit - Portable Diagnostics
powershell.exe -NoLogo -NoProfile -File "%~dp0diagnose.ps1"
set "RESULT=%ERRORLEVEL%"
echo.
if not "%RESULT%"=="0" echo Diagnostics exited with code %RESULT%. Review the message above.
pause
exit /b %RESULT%
