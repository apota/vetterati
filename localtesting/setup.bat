@echo off
echo Setting up local development environment...

echo Creating Docker network...
docker network create ats-local 2>nul

echo.
echo Development environment setup complete!
echo.
echo Next steps:
echo 1. Start infrastructure: powershell -ExecutionPolicy Bypass -File .\scripts\start-infrastructure.ps1
echo 2. Start frontend dev: powershell -ExecutionPolicy Bypass -File .\scripts\start-frontend-dev.ps1
echo 3. Start service dev: powershell -ExecutionPolicy Bypass -File .\scripts\start-service-dev.ps1 -ServiceName "resume-service"
echo 4. Check status: powershell -ExecutionPolicy Bypass -File .\scripts\status.ps1
