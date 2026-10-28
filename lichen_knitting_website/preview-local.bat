@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "PORT=8000"
set "PY="

where py >nul 2>nul && set "PY=py"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY where python3 >nul 2>nul && set "PY=python3"

if not defined PY (
  echo.
  echo [!] Python was not found on this computer.
  echo     You can still preview the site by double-clicking index.html,
  echo     but the language switch may be blocked by the browser on file:// .
  echo.
  echo     To install Python: https://www.python.org/downloads/
  echo.
  pause
  exit /b 1
)

echo.
echo   Jimo Lichen Knitting Factory - local preview
echo   -------------------------------------------
echo   http://127.0.0.1:%PORT%/index.html
echo   http://127.0.0.1:%PORT%/index.html?lang=en   (English)
echo.
echo   Press Ctrl+C to stop the server.
echo.

start "" "http://127.0.0.1:%PORT%/index.html"
%PY% -m http.server %PORT% --bind 127.0.0.1
pause