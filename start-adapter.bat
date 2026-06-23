@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
echo Starting Codex Switch Adapter...
echo Press Ctrl+C to stop.
echo.
python -m codex_switch.adapter
pause
