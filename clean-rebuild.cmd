@echo off
setlocal

REM One-command clean/rebuild/install for Windows CMD.
REM Default: create/use .venv and do full dependency install.

set "VENV_PATH=.venv"
set "PY_SPEC="

py -3.11 -c "import sys" >nul 2>&1
if %errorlevel%==0 set "PY_SPEC=-3.11"

if not defined PY_SPEC (
  py -3.10 -c "import sys" >nul 2>&1
  if %errorlevel%==0 set "PY_SPEC=-3.10"
)

if not defined PY_SPEC (
  echo Python 3.10+ not found via py launcher.
  py -0p
  exit /b 1
)

if not exist %VENV_PATH%\Scripts\python.exe (
  py %PY_SPEC% -m venv %VENV_PATH%
)

%VENV_PATH%\Scripts\python.exe scripts\clean_rebuild.py --repo . --venv %VENV_PATH% --with-deps
if errorlevel 1 exit /b %errorlevel%

echo.
echo Done. Activate with: %VENV_PATH%\Scripts\activate
endlocal
