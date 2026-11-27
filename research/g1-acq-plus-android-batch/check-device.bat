@echo off
setlocal
cd /d "%~dp0..\.."
where python >nul 2>&1
if errorlevel 1 (
  echo Python not found on PATH.
  exit /b 1
)
python -c "from device_diagnostics import inspect_connection; d=inspect_connection(); print(d.headline); print(d.guidance); raise SystemExit(0 if d.status == 'connected' else 2)"
exit /b %errorlevel%
