@echo off
echo Testing Auth Service Registration Endpoint
echo.

set SERVER_URL=http://localhost:5000
set ENDPOINT=%SERVER_URL%/api/v1/auth/register

echo Testing server health...
curl -s %SERVER_URL%/health

echo.
echo.
echo Testing registration endpoint...
echo Endpoint: %ENDPOINT%
echo.

curl -X POST %ENDPOINT% ^
  -H "Content-Type: application/json" ^
  -d "{\"firstName\":\"John\",\"lastName\":\"Doe\",\"email\":\"john.doe@example.com\",\"password\":\"password123\",\"role\":\"recruiter\",\"company\":\"Test Company\"}" ^
  -v

echo.
echo.
echo Testing with the test-register endpoint (manual JSON parsing)...
curl -X POST %SERVER_URL%/api/v1/auth/test-register ^
  -H "Content-Type: application/json" ^
  -d "{\"firstName\":\"Jane\",\"lastName\":\"Smith\",\"email\":\"jane.smith@example.com\",\"password\":\"password123\",\"role\":\"recruiter\",\"company\":\"Test Company\"}" ^
  -v

echo.
echo.
echo Test completed!
pause
