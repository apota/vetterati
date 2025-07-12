Write-Host "Testing Auth Service Registration Endpoint" -ForegroundColor Green
Write-Host ""

$serverUrl = "http://localhost:5000"
$endpoint = "$serverUrl/api/v1/auth/register"

Write-Host "Testing server health..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "$serverUrl/health" -Method Get
    Write-Host "Health check: $($healthResponse | ConvertTo-Json)" -ForegroundColor Cyan
} catch {
    Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure the server is running (use run-test.ps1 first)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Testing registration endpoint..." -ForegroundColor Yellow
Write-Host "Endpoint: $endpoint" -ForegroundColor Cyan
Write-Host ""

$registrationData = @{
    firstName = "John"
    lastName = "Doe"
    email = "john.doe@example.com"
    password = "password123"
    role = "recruiter"
    company = "Test Company"
}

try {
    $response = Invoke-RestMethod -Uri $endpoint -Method Post -Body ($registrationData | ConvertTo-Json) -ContentType "application/json"
    Write-Host "Registration successful!" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Depth 3)" -ForegroundColor Cyan
} catch {
    Write-Host "Registration failed:" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Testing with the test-register endpoint (manual JSON parsing)..." -ForegroundColor Yellow

$testRegistrationData = @{
    firstName = "Jane"
    lastName = "Smith"
    email = "jane.smith@example.com"
    password = "password123"
    role = "recruiter"
    company = "Test Company"
}

try {
    $testResponse = Invoke-RestMethod -Uri "$serverUrl/api/v1/auth/test-register" -Method Post -Body ($testRegistrationData | ConvertTo-Json) -ContentType "application/json"
    Write-Host "Test registration successful!" -ForegroundColor Green
    Write-Host "Response: $($testResponse | ConvertTo-Json -Depth 3)" -ForegroundColor Cyan
} catch {
    Write-Host "Test registration failed:" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Test completed!" -ForegroundColor Green
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
