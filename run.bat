@echo off
title TRACE-X Tactical Command Center
echo ========================================================
echo   TRACE-X | Multi-Camera ANPR Trajectory Tracking
echo   Smart India Hackathon Prototype (SIH26127)
echo ========================================================
echo.
echo   [+] Dashboard: http://127.0.0.1:8000
echo   [+] API Docs:  http://127.0.0.1:8000/docs
echo.
echo Press CTRL+C to stop the server.
echo.
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
pause
