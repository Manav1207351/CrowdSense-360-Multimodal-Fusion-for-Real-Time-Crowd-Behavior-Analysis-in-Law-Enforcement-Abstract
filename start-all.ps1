# CrowdSense 360 - Start All Services
# Run this script to start both backend and frontend

Write-Host "🚀 Starting CrowdSense 360..." -ForegroundColor Green
Write-Host ""

# Start Flask Backend in new window
Write-Host "📡 Starting Flask Backend on port 5000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python src/app.py"

# Wait a moment for backend to initialize
Start-Sleep -Seconds 3

# Start Frontend in new window
Write-Host "🎨 Starting Frontend on port 5173..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host ""
Write-Host "✅ Services starting..." -ForegroundColor Green
Write-Host "   Backend:  http://localhost:5000" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 Opening browser in 5 seconds..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Open browser
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "All services started! Close the PowerShell windows to stop." -ForegroundColor Green
