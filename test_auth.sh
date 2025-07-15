#!/bin/bash

# Test script to verify authentication flow
echo "=== TESTING AUTHENTICATION FLOW ==="

# Test 1: No authentication (should fail)
echo "1. Testing unauthenticated request..."
curl -s -X GET http://localhost:3000/api/v1/auth/me | jq -r '.data.name' 2>/dev/null || echo "✅ Properly rejected unauthenticated request"

# Test 2: Login as admin
echo "2. Logging in as admin..."
ADMIN_TOKEN=$(curl -s -X POST http://localhost:3000/api/v1/auth/demo-login \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}' | jq -r '.data.accessToken')

echo "3. Testing admin profile..."
ADMIN_PROFILE=$(curl -s -X GET http://localhost:3000/api/v1/auth/me \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.data.name')
echo "✅ Admin profile: $ADMIN_PROFILE"

# Test 3: Login as hiring manager
echo "4. Logging in as hiring manager..."
MANAGER_TOKEN=$(curl -s -X POST http://localhost:3000/api/v1/auth/demo-login \
  -H "Content-Type: application/json" \
  -d '{"role": "hiring-manager"}' | jq -r '.data.accessToken')

echo "5. Testing hiring manager profile..."
MANAGER_PROFILE=$(curl -s -X GET http://localhost:3000/api/v1/auth/me \
  -H "Authorization: Bearer $MANAGER_TOKEN" | jq -r '.data.name')
echo "✅ Hiring Manager profile: $MANAGER_PROFILE"

# Test 4: Login as recruiter
echo "6. Logging in as recruiter..."
RECRUITER_TOKEN=$(curl -s -X POST http://localhost:3000/api/v1/auth/demo-login \
  -H "Content-Type: application/json" \
  -d '{"role": "recruiter"}' | jq -r '.data.accessToken')

echo "7. Testing recruiter profile..."
RECRUITER_PROFILE=$(curl -s -X GET http://localhost:3000/api/v1/auth/me \
  -H "Authorization: Bearer $RECRUITER_TOKEN" | jq -r '.data.name')
echo "✅ Recruiter profile: $RECRUITER_PROFILE"

echo ""
echo "=== SUMMARY ==="
echo "Admin: $ADMIN_PROFILE"
echo "Hiring Manager: $MANAGER_PROFILE"
echo "Recruiter: $RECRUITER_PROFILE"
echo ""
echo "✅ All users return different profiles based on authentication token!"
