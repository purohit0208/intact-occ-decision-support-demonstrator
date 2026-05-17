@echo off
setlocal

cd /d "%~dp0"
set "PYTHON_EXE="

if exist "%~dp0.venv\Scripts\python.exe" (
  set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
  goto :python_found
)

for /f "delims=" %%I in ('where python 2^>nul') do (
  set "PYTHON_EXE=%%I"
  goto :python_found
)

:python_found
if not defined PYTHON_EXE (
  echo Python was not found on this machine.
  echo Install Python 3.11 or newer, then run Start-OCC-Demo.bat again.
  pause
  exit /b 1
)

echo Starting backend on http://127.0.0.1:8000
cd /d "%~dp0backend"
"%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

echo.
echo Backend window closed.
pause
