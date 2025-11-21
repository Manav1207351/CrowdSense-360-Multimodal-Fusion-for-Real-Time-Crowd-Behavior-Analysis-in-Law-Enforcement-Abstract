# CrowdSense 360 - Start Backend Server
Write-Host "🚀 Starting CrowdSense 360 Backend..." -ForegroundColor Green
Write-Host "📍 Using your trained models:" -ForegroundColor Cyan
Write-Host "   - Crowd: detectors/models/crowd_yolo6/weights/best.pt" -ForegroundColor Yellow
Write-Host "   - Fight: detectors/models/fight_yolo/weights/best.pt" -ForegroundColor Yellow
Write-Host "   - Weapon: detectors/models/weapon_yolo2/weights/weapon_yolo.pt" -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 Backend will run on: http://localhost:8080" -ForegroundColor Green
Write-Host "📡 API Endpoint: POST http://localhost:8080/api/detect" -ForegroundColor Green
Write-Host ""

Set-Location a:\src\src
python app.py
