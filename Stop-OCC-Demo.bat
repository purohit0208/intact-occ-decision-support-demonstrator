@echo off
setlocal

echo Closing local OCC demo processes on ports 8000 and 5173...

for %%P in (8000 5173) do (
  for /f "tokens=5" %%I in ('netstat -ano ^| findstr LISTENING ^| findstr :%%P') do (
    taskkill /PID %%I /F >nul 2>nul
  )
)

echo Done.
pause
