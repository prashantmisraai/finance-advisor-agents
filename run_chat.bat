@echo off
setlocal

set "BUNDLED=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%BUNDLED%" (
    "%BUNDLED%" main.py --chat --month 2026-05
    exit /b %errorlevel%
)

set "BUNDLED=C:\Users\91974\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%BUNDLED%" (
    "%BUNDLED%" main.py --chat --month 2026-05
    exit /b %errorlevel%
)

python -c "print('ok')" >nul 2>nul
if %errorlevel%==0 (
    python main.py --chat --month 2026-05
    exit /b %errorlevel%
)

py -c "print('ok')" >nul 2>nul
if %errorlevel%==0 (
    py main.py --chat --month 2026-05
    exit /b %errorlevel%
)

echo Python was not found. Install Python 3.11+ or run this from Codex where the bundled runtime exists.
exit /b 1
