@echo off
setlocal
echo Publishing the prepared experiment snapshot to idltd/bias-check...
git -C "%~dp0publication" push -u origin main
if errorlevel 1 (
  echo.
  echo Push failed. The Git error is shown above.
  pause
  exit /b 1
)
echo.
echo Published: https://github.com/idltd/bias-check
pause
