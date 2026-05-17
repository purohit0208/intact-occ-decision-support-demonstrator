@echo off
setlocal

cd /d "%~dp0"

echo Starting INTACT OCC Decision Support Demonstrator...
echo.
echo A backend window and a frontend window will open.
echo Please keep both windows open during the demonstration.
echo.

start "OCC Demo Backend" "%~dp0Run-OCC-Backend.bat"
start "OCC Demo Frontend" "%~dp0Run-OCC-Frontend.bat"

echo Waiting for the frontend to become available...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$deadline=(Get-Date).AddSeconds(45); do { try { $r=Invoke-WebRequest 'http://127.0.0.1:5173' -UseBasicParsing; if($r.StatusCode -ge 200){ Start-Process 'http://127.0.0.1:5173'; exit 0 } } catch {}; Start-Sleep -Seconds 2 } while((Get-Date) -lt $deadline); Start-Process 'http://127.0.0.1:5173'"

echo.
echo The browser should now open at http://127.0.0.1:5173
echo If it does not open automatically, open that address manually.
echo.
pause
