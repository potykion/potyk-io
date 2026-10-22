@echo off
cd /d "%~dp0"
set FLASK_APP=main
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"
".venv\Scripts\flask.exe" run --debug
if errorlevel 1 pause
