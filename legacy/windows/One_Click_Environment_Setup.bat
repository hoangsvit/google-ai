@echo off
setlocal
cd /d "%~dp0..\.."
echo This launcher checks prerequisites without installing or modifying software.
echo Install Python and Android Platform Tools from their official sources if missing.
call "%~dp000_Environment_Self_Check.bat"
exit /b %errorlevel%
