@echo off
cd /d "%~dp0"
set FLASK_APP=main

if exist "%ProgramFiles%\nodejs\node.exe" set "PATH=%ProgramFiles%\nodejs;%PATH%"
if exist "%LocalAppData%\Programs\nodejs\node.exe" set "PATH=%LocalAppData%\Programs\nodejs;%PATH%"

echo [potyk-io] Installing backend deps (requirements.txt) ...
if not exist ".venv\Scripts\python.exe" python -m venv .venv
".venv\Scripts\python.exe" -m pip install -q --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :fail

echo [potyk-io] Installing frontend deps (potyk-io-front) ...
pushd potyk-io-front
call npm ci
if errorlevel 1 (
    popd
    goto :fail
)
popd

echo [potyk-io] Starting potyk-io-front on :5173 ...
start "potyk-io-front" cmd /k "cd /d "%~dp0potyk-io-front" && npm run dev -- --host 127.0.0.1 --port 5173"

start "" cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:5173/v2/fin"

echo [potyk-io] Starting Flask on :5000 ...
".venv\Scripts\flask.exe" run --debug
if errorlevel 1 pause
exit /b 0

:fail
echo [potyk-io] Dependency install FAILED, not starting.
pause
exit /b 1
