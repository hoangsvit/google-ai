@echo off
setlocal
cd /d "%~dp0..\.."
echo No equivalent alternative extension was verified.
call "%~dp003_List_Available_Free_And_Discounted_Offers.bat"
exit /b %errorlevel%
