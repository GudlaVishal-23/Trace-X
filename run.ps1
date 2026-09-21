Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  TRACE-X | Multi-Camera ANPR Trajectory Tracking" -ForegroundColor Green
Write-Host "  Smart India Hackathon Prototype (SIH26127)" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  [+] Dashboard: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "  [+] API Docs:  http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press CTRL+C to stop the server." -ForegroundColor Gray
Write-Host ""

python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
