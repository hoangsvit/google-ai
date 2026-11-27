@echo off
setlocal
cd /d "%~dp0..\.."
echo Offer reference: Pro 5TB - claimed 12-month free offer
echo Unverified; available only if displayed for your account in Google One.
call "%~dp003_List_Available_Free_And_Discounted_Offers.bat"
exit /b %errorlevel%
