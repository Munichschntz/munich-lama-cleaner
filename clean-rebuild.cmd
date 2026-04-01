@echo off
setlocal

REM One-command clean/rebuild/install for Windows CMD.
REM Default: create/use .venv311 and do full dependency install.

if not exist .venv311\Scripts\python.exe (
  py -3.11 -m venv .venv311
)

.venv311\Scripts\python.exe scripts\clean_rebuild.py --repo . --venv .venv311 --with-deps
if errorlevel 1 exit /b %errorlevel%

echo.
echo Done. Activate with: .venv311\Scripts\activate
endlocal
