@echo off
echo Starting Auth Service in Test Mode...
echo.
echo This will run the auth service with:
echo - In-memory database (no PostgreSQL needed)
echo - Mock Redis (no Redis needed)
echo - Mock email service
echo - Simplified configuration
echo.

cd /d "%~dp0"

echo Installing/updating packages...
dotnet restore

echo.
echo Starting the test server...
echo The service will be available at: http://localhost:5000
echo Swagger UI will be available at: http://localhost:5000/swagger
echo.
echo Press Ctrl+C to stop the service
echo.

set ASPNETCORE_ENVIRONMENT=Development
dotnet run --project AuthService.csproj --urls "http://localhost:5000"

pause
