@echo off
setlocal
cd /d "%~dp0..\.."
call "%~dp0..\..\research\g1-acq-plus-android-batch\check-device.bat"
exit /b %errorlevel%
