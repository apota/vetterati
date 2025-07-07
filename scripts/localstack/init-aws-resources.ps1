# PowerShell script to initialize LocalStack AWS resources
Write-Host "Waiting for LocalStack to be ready..."

# Wait for LocalStack to be ready
do {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:4566/health" -Method GET -TimeoutSec 5
        if ($response -match "running") {
            Write-Host "LocalStack is ready!"
            break
        }
    }
    catch {
        Write-Host "LocalStack is not ready yet, waiting..."
        Start-Sleep -Seconds 2
    }
} while ($true)

Write-Host "Initializing AWS resources..."

# Set environment variables for AWS CLI to use LocalStack
$env:AWS_ACCESS_KEY_ID = "test"
$env:AWS_SECRET_ACCESS_KEY = "test"
$env:AWS_DEFAULT_REGION = "us-east-1"
$env:AWS_ENDPOINT_URL = "http://localhost:4566"

# Create S3 bucket for resume storage
Write-Host "Creating S3 bucket for resumes..."
aws --endpoint-url=http://localhost:4566 s3 mb s3://vetterati-resumes

# Create DynamoDB tables
Write-Host "Creating DynamoDB tables..."

# Analytics events table
aws --endpoint-url=http://localhost:4566 dynamodb create-table `
    --table-name analytics-events `
    --attribute-definitions AttributeName=id,AttributeType=S AttributeName=timestamp,AttributeType=N `
    --key-schema AttributeName=id,KeyType=HASH AttributeName=timestamp,KeyType=RANGE `
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# User analytics table
aws --endpoint-url=http://localhost:4566 dynamodb create-table `
    --table-name user-analytics `
    --attribute-definitions AttributeName=userId,AttributeType=S AttributeName=date,AttributeType=S `
    --key-schema AttributeName=userId,KeyType=HASH AttributeName=date,KeyType=RANGE `
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# Create SNS topic for notifications
Write-Host "Creating SNS topic..."
aws --endpoint-url=http://localhost:4566 sns create-topic --name vetterati-notifications

# Create SQS queue for notifications
Write-Host "Creating SQS queue..."
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name vetterati-notifications

Write-Host "AWS resources initialized successfully!"
