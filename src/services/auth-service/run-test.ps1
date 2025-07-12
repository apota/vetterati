Write-Host "Starting Auth Service in Test Mode..." -ForegroundColor Green
Write-Host ""
Write-Host "This will run the auth service with:" -ForegroundColor Yellow
Write-Host "- In-memory database (no PostgreSQL needed)" -ForegroundColor Cyan
Write-Host "- Mock Redis (no Redis needed)" -ForegroundColor Cyan
Write-Host "- Mock email service" -ForegroundColor Cyan
Write-Host "- Simplified configuration" -ForegroundColor Cyan
Write-Host ""

# Navigate to the script directory
Set-Location $PSScriptRoot

Write-Host "Installing/updating packages..." -ForegroundColor Yellow
dotnet restore

Write-Host ""
Write-Host "Starting the test server..." -ForegroundColor Green
Write-Host "The service will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Swagger UI will be available at: http://localhost:5000/swagger" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
Write-Host ""

$env:ASPNETCORE_ENVIRONMENT = "Development"
dotnet run --project AuthService.csproj --urls "http://localhost:5000"
