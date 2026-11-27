@echo off
setlocal
cd /d "%~dp0..\.."
call "%~dp000_Environment_Self_Check.bat"
exit /b %errorlevel%
