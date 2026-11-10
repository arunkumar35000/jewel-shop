# AURA Luxury Gold Jewellery Shopping Platform Launcher
Set-Location -Path $PSScriptRoot

Write-Host "=========================================================================" -ForegroundColor Gold
Write-Host "                  AURA GOLD JEWELLERY SHOPPING PLATFORM" -ForegroundColor Yellow
Write-Host "=========================================================================" -ForegroundColor Gold
Write-Host ""

$PyExe = "python"
if (Test-Path "$PSScriptRoot\venv\Scripts\python.exe") {
    $PyExe = "$PSScriptRoot\venv\Scripts\python.exe"
} elseif (Test-Path "C:\Users\ASUS\AppData\Local\Programs\Python\Python37\python.exe") {
    $PyExe = "C:\Users\ASUS\AppData\Local\Programs\Python\Python37\python.exe"
}

Write-Host "Using Python: $PyExe" -ForegroundColor DarkYellow
Write-Host "Starting Django Development Server on http://127.0.0.1:8000/ ..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Demo Credentials:" -ForegroundColor Green
Write-Host "  - Admin Portal:     Username: admin    / Password: Admin@123" -ForegroundColor White
Write-Host "  - Customer Account: Username: customer / Password: Customer@123" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in this console window to stop the server anytime." -ForegroundColor Gray
Write-Host "=========================================================================" -ForegroundColor Gold
Write-Host ""

& $PyExe manage.py runserver 127.0.0.1:8000
