# Simple PowerShell script to verify profile update functionality
# This script tests the profile update endpoint

$BASE_URL = "http://localhost:5001"
$AUTH_ENDPOINT = "/api/v1/auth"

Write-Host "Testing Profile Update Functionality" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# First, perform a demo login to get a token
Write-Host "1. Performing demo login..." -ForegroundColor Yellow

$loginBody = @{
    role = "recruiter"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "${BASE_URL}${AUTH_ENDPOINT}/demo-login" -Method Post -Body $loginBody -ContentType "application/json"
    $accessToken = $loginResponse.data.accessToken
    
    if (-not $accessToken) {
        Write-Host "❌ Failed to get access token" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Successfully got access token" -ForegroundColor Green
} catch {
    Write-Host "❌ Demo login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test profile update
Write-Host ""
Write-Host "2. Testing profile update..." -ForegroundColor Yellow

$updateBody = @{
    firstName = "Updated"
    lastName = "Name"
    company = "New Company"
    preferences = @{
        theme = "dark"
        notifications = $true
    }
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type" = "application/json"
}

try {
    $updateResponse = Invoke-RestMethod -Uri "${BASE_URL}${AUTH_ENDPOINT}/me" -Method Put -Body $updateBody -Headers $headers
    
    Write-Host "✅ Profile updated successfully:" -ForegroundColor Green
    Write-Host "   First Name: $($updateResponse.data.firstName)" -ForegroundColor Cyan
    Write-Host "   Last Name: $($updateResponse.data.lastName)" -ForegroundColor Cyan
    Write-Host "   Company: $($updateResponse.data.company)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Profile update failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Verify the update by fetching user info
Write-Host ""
Write-Host "3. Verifying profile update by fetching user info..." -ForegroundColor Yellow

try {
    $userInfoResponse = Invoke-RestMethod -Uri "${BASE_URL}${AUTH_ENDPOINT}/me" -Method Get -Headers $headers
    
    $currentFirstName = $userInfoResponse.data.firstName
    $currentLastName = $userInfoResponse.data.lastName
    $currentCompany = $userInfoResponse.data.company
    
    if ($currentFirstName -eq "Updated" -and $currentLastName -eq "Name" -and $currentCompany -eq "New Company") {
        Write-Host "✅ Profile update persistence verified:" -ForegroundColor Green
        Write-Host "   First Name: $currentFirstName" -ForegroundColor Cyan
        Write-Host "   Last Name: $currentLastName" -ForegroundColor Cyan
        Write-Host "   Company: $currentCompany" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🎉 All tests passed! Profile update is working correctly." -ForegroundColor Green
    } else {
        Write-Host "❌ Profile update persistence failed" -ForegroundColor Red
        Write-Host "   Expected: Updated Name, New Company" -ForegroundColor Red
        Write-Host "   Got: $currentFirstName $currentLastName, $currentCompany" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Failed to fetch user info: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
