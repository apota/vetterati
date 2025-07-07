# Test Registration and Login Endpoints
# This script tests the new user registration and email login functionality

$baseUrl = "http://localhost:5000/api/v1/auth"

Write-Host "Testing Vetterati User Registration and Login..." -ForegroundColor Green

# Test data
$testUser = @{
    firstName = "John"
    lastName = "Doe"
    email = "john.doe@example.com"
    password = "SecurePassword123!"
    role = "recruiter"
    company = "Test Company"
}

Write-Host "`n1. Testing User Registration..." -ForegroundColor Yellow

try {
    # Register new user
    $registerResponse = Invoke-RestMethod -Uri "$baseUrl/register" -Method POST -Body ($testUser | ConvertTo-Json) -ContentType "application/json"
    
    Write-Host "✓ Registration successful!" -ForegroundColor Green
    Write-Host "User ID: $($registerResponse.data.user.id)" -ForegroundColor Cyan
    Write-Host "Access Token: $($registerResponse.data.accessToken.Substring(0, 20))..." -ForegroundColor Cyan
    
    $accessToken = $registerResponse.data.accessToken
}
catch {
    Write-Host "✗ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $errorBody = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($errorBody)
        $errorText = $reader.ReadToEnd()
        Write-Host "Error details: $errorText" -ForegroundColor Red
    }
    exit 1
}

Write-Host "`n2. Testing Email Login..." -ForegroundColor Yellow

try {
    $loginData = @{
        email = $testUser.email
        password = $testUser.password
    }
    
    # Login with email/password
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/email-login" -Method POST -Body ($loginData | ConvertTo-Json) -ContentType "application/json"
    
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "User: $($loginResponse.data.user.name)" -ForegroundColor Cyan
    Write-Host "Company: $($loginResponse.data.user.company)" -ForegroundColor Cyan
    Write-Host "Roles: $($loginResponse.data.user.roles -join ', ')" -ForegroundColor Cyan
}
catch {
    Write-Host "✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $errorBody = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($errorBody)
        $errorText = $reader.ReadToEnd()
        Write-Host "Error details: $errorText" -ForegroundColor Red
    }
    exit 1
}

Write-Host "`n3. Testing Get User Info..." -ForegroundColor Yellow

try {
    $headers = @{
        "Authorization" = "Bearer $accessToken"
    }
    
    # Get current user info
    $userResponse = Invoke-RestMethod -Uri "$baseUrl/me" -Method GET -Headers $headers
    
    Write-Host "✓ User info retrieved successfully!" -ForegroundColor Green
    Write-Host "User Email: $($userResponse.data.email)" -ForegroundColor Cyan
    Write-Host "User Name: $($userResponse.data.name)" -ForegroundColor Cyan
    Write-Host "Active: $($userResponse.data.isActive)" -ForegroundColor Cyan
}
catch {
    Write-Host "✗ Get user info failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $errorBody = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($errorBody)
        $errorText = $reader.ReadToEnd()
        Write-Host "Error details: $errorText" -ForegroundColor Red
    }
    exit 1
}

Write-Host "`n4. Testing Duplicate Registration (should fail)..." -ForegroundColor Yellow

try {
    # Try to register same user again
    $duplicateResponse = Invoke-RestMethod -Uri "$baseUrl/register" -Method POST -Body ($testUser | ConvertTo-Json) -ContentType "application/json"
    
    Write-Host "✗ Duplicate registration should have failed!" -ForegroundColor Red
}
catch {
    Write-Host "✓ Duplicate registration correctly rejected!" -ForegroundColor Green
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "Status: 400 Bad Request (as expected)" -ForegroundColor Cyan
    }
}

Write-Host "`n5. Testing Invalid Login (should fail)..." -ForegroundColor Yellow

try {
    $invalidLoginData = @{
        email = $testUser.email
        password = "WrongPassword"
    }
    
    # Try login with wrong password
    $invalidLoginResponse = Invoke-RestMethod -Uri "$baseUrl/email-login" -Method POST -Body ($invalidLoginData | ConvertTo-Json) -ContentType "application/json"
    
    Write-Host "✗ Invalid login should have failed!" -ForegroundColor Red
}
catch {
    Write-Host "✓ Invalid login correctly rejected!" -ForegroundColor Green
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "Status: 401 Unauthorized (as expected)" -ForegroundColor Cyan
    }
}

Write-Host "`n🎉 All tests completed!" -ForegroundColor Green
Write-Host "`nTo test the frontend:" -ForegroundColor Yellow
Write-Host "1. Install frontend dependencies: cd src/frontend && npm install" -ForegroundColor White
Write-Host "2. Start frontend: npm start" -ForegroundColor White
Write-Host "3. Navigate to http://localhost:3000" -ForegroundColor White
Write-Host "4. Click 'Create account here' to test registration" -ForegroundColor White
