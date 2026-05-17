@echo off
setlocal

cd /d "%~dp0"

if exist "C:\Program Files\nodejs\node.exe" (
  set "PATH=C:\Program Files\nodejs;%PATH%"
)

set "NPM_CMD=npm.cmd"
if exist "C:\Program Files\nodejs\npm.cmd" (
  set "NPM_CMD=C:\Program Files\nodejs\npm.cmd"
)

if /i "%NPM_CMD%"=="npm.cmd" (
  where npm.cmd >nul 2>nul
  if errorlevel 1 (
    echo npm was not found on this machine.
    echo Install Node.js 20 or newer, then run Start-OCC-Demo.bat again.
    pause
    exit /b 1
  )
) else if not exist "%NPM_CMD%" (
  echo npm was not found on this machine.
  echo Install Node.js 20 or newer, then run Start-OCC-Demo.bat again.
  pause
  exit /b 1
)

echo Starting frontend on http://127.0.0.1:5173
cd /d "%~dp0frontend"
call "%NPM_CMD%" run dev -- --host 127.0.0.1 --port 5173

echo.
echo Frontend window closed.
pause
