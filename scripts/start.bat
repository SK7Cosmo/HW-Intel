@echo off
REM Hardware Intelligence Dashboard — Launcher
REM Starts the FastAPI backend. Frontend is served from the same process.

echo.
echo  ┌─────────────────────────────────────────────────┐
echo  │   Hardware Intelligence Dashboard  v1.0.0       │
echo  │   http://127.0.0.1:7890                         │
echo  └─────────────────────────────────────────────────┘
echo.

cd /d "%~dp0\..\backend"
python -m uvicorn main:app --host 127.0.0.1 --port 7890 --reload

pause
