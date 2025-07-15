#!/usr/bin/env bash

# Simple test script to verify profile update functionality
# This script tests the profile update endpoint

BASE_URL="http://localhost:5001"
AUTH_ENDPOINT="/api/v1/auth"

echo "Testing Profile Update Functionality"
echo "===================================="

# First, perform a demo login to get a token
echo "1. Performing demo login..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}${AUTH_ENDPOINT}/demo-login" \
  -H "Content-Type: application/json" \
  -d '{"role": "recruiter"}')

echo "Login response: $LOGIN_RESPONSE"

# Extract the access token
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.accessToken')

if [ "$ACCESS_TOKEN" = "null" ] || [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Failed to get access token"
  exit 1
fi

echo "✅ Successfully got access token"

# Test profile update
echo ""
echo "2. Testing profile update..."
UPDATE_RESPONSE=$(curl -s -X PUT "${BASE_URL}${AUTH_ENDPOINT}/me" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "firstName": "Updated",
    "lastName": "Name",
    "company": "New Company",
    "preferences": {
      "theme": "dark",
      "notifications": true
    }
  }')

echo "Update response: $UPDATE_RESPONSE"

# Check if update was successful
if echo "$UPDATE_RESPONSE" | jq -e '.data.firstName' > /dev/null; then
  UPDATED_FIRST_NAME=$(echo $UPDATE_RESPONSE | jq -r '.data.firstName')
  UPDATED_LAST_NAME=$(echo $UPDATE_RESPONSE | jq -r '.data.lastName')
  UPDATED_COMPANY=$(echo $UPDATE_RESPONSE | jq -r '.data.company')
  
  echo "✅ Profile updated successfully:"
  echo "   First Name: $UPDATED_FIRST_NAME"
  echo "   Last Name: $UPDATED_LAST_NAME"
  echo "   Company: $UPDATED_COMPANY"
else
  echo "❌ Profile update failed"
  exit 1
fi

# Verify the update by fetching user info
echo ""
echo "3. Verifying profile update by fetching user info..."
USER_INFO_RESPONSE=$(curl -s -X GET "${BASE_URL}${AUTH_ENDPOINT}/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "User info response: $USER_INFO_RESPONSE"

# Check if the updated values are persisted
if echo "$USER_INFO_RESPONSE" | jq -e '.data.firstName' > /dev/null; then
  CURRENT_FIRST_NAME=$(echo $USER_INFO_RESPONSE | jq -r '.data.firstName')
  CURRENT_LAST_NAME=$(echo $USER_INFO_RESPONSE | jq -r '.data.lastName')
  CURRENT_COMPANY=$(echo $USER_INFO_RESPONSE | jq -r '.data.company')
  
  if [ "$CURRENT_FIRST_NAME" = "Updated" ] && [ "$CURRENT_LAST_NAME" = "Name" ] && [ "$CURRENT_COMPANY" = "New Company" ]; then
    echo "✅ Profile update persistence verified:"
    echo "   First Name: $CURRENT_FIRST_NAME"
    echo "   Last Name: $CURRENT_LAST_NAME"
    echo "   Company: $CURRENT_COMPANY"
    echo ""
    echo "🎉 All tests passed! Profile update is working correctly."
  else
    echo "❌ Profile update persistence failed"
    echo "   Expected: Updated Name, New Company"
    echo "   Got: $CURRENT_FIRST_NAME $CURRENT_LAST_NAME, $CURRENT_COMPANY"
    exit 1
  fi
else
  echo "❌ Failed to fetch user info"
  exit 1
fi
