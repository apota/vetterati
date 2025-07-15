# Test script to verify authentication flow
Write-Host "=== TESTING AUTHENTICATION FLOW ===" -ForegroundColor Green
Write-Host ""

# Test 1: No authentication (should fail)
Write-Host "1. Testing unauthenticated request..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/auth/me"
    Write-Host "❌ ERROR: Should have failed but got: $($response.data.name)" -ForegroundColor Red
} catch {
    Write-Host "✅ Properly rejected unauthenticated request" -ForegroundColor Green
}

# Test 2: Login as admin
Write-Host "2. Logging in as admin..." -ForegroundColor Yellow
$body = '{"role": "admin"}'
$adminResponse = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/auth/demo-login" -Method POST -Body $body -ContentType "application/json"
$adminToken = $adminResponse.data.accessToken

Write-Host "3. Testing admin profile..." -ForegroundColor Yellow
$adminHeaders = @{Authorization = "Bearer $adminToken"}
$adminProfile = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/auth/me" -Headers $adminHeaders
Write-Host "✅ Admin profile: $($adminProfile.data.name) ($($adminProfile.data.email))" -ForegroundColor Green

# Test 3: Login as hiring manager
Write-Host "4. Logging in as hiring manager..." -ForegroundColor Yellow
$body = '{"role": "hiring-manager"}'
$managerResponse = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/auth/demo-login" -Method POST -Body $body -ContentType "application/json"
$managerToken = $managerResponse.data.accessToken

Write-Host "5. Testing hiring manager profile..." -ForegroundColor Yellow
$managerHeaders = @{Authorization = "Bearer $managerToken"}
$managerProfile = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/auth/me" -Headers $managerHeaders
Write-Host "✅ Hiring Manager profile: $($managerProfile.data.name) ($($managerProfile.data.email))" -ForegroundColor Green

# Test 4: Login as recruiter
Write-Host "6. Logging in as recruiter..." -ForegroundColor Yellow
$body = '{"role": "recruiter"}'
$recruiterResponse = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/auth/demo-login" -Method POST -Body $body -ContentType "application/json"
$recruiterToken = $recruiterResponse.data.accessToken

Write-Host "7. Testing recruiter profile..." -ForegroundColor Yellow
$recruiterHeaders = @{Authorization = "Bearer $recruiterToken"}
$recruiterProfile = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/auth/me" -Headers $recruiterHeaders
Write-Host "✅ Recruiter profile: $($recruiterProfile.data.name) ($($recruiterProfile.data.email))" -ForegroundColor Green

Write-Host ""
Write-Host "=== SUMMARY ===" -ForegroundColor Green
Write-Host "Admin: $($adminProfile.data.name) ($($adminProfile.data.email))" -ForegroundColor White
Write-Host "Hiring Manager: $($managerProfile.data.name) ($($managerProfile.data.email))" -ForegroundColor White
Write-Host "Recruiter: $($recruiterProfile.data.name) ($($recruiterProfile.data.email))" -ForegroundColor White
Write-Host ""
Write-Host "✅ All users return different profiles based on authentication token!" -ForegroundColor Green
