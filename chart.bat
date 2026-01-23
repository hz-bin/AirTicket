@echo off
setlocal
cd /d "%~dp0"
".venv\Scripts\python.exe" chart.py
endlocal
