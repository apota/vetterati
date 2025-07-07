#!/bin/bash

# Wait for LocalStack to be ready
echo "Waiting for LocalStack to be ready..."
until curl -s http://localhost:4566/health | grep -q "running"; do
    echo "LocalStack is not ready yet, waiting..."
    sleep 2
done

echo "LocalStack is ready, initializing AWS resources..."

# Set AWS credentials and region for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
export AWS_ENDPOINT_URL=http://localhost:4566

# Create S3 bucket for resume storage
echo "Creating S3 bucket for resumes..."
aws --endpoint-url=http://localhost:4566 s3 mb s3://vetterati-resumes
aws --endpoint-url=http://localhost:4566 s3api put-bucket-cors --bucket vetterati-resumes --cors-configuration '{
    "CORSRules": [
        {
            "AllowedHeaders": ["*"],
            "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
            "AllowedOrigins": ["*"],
            "ExposeHeaders": ["ETag"]
        }
    ]
}'

# Create DynamoDB tables
echo "Creating DynamoDB tables..."

# Analytics events table
aws --endpoint-url=http://localhost:4566 dynamodb create-table \
    --table-name analytics-events \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
        AttributeName=timestamp,AttributeType=N \
    --key-schema \
        AttributeName=id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5

# User analytics table
aws --endpoint-url=http://localhost:4566 dynamodb create-table \
    --table-name user-analytics \
    --attribute-definitions \
        AttributeName=userId,AttributeType=S \
        AttributeName=date,AttributeType=S \
    --key-schema \
        AttributeName=userId,KeyType=HASH \
        AttributeName=date,KeyType=RANGE \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5

# Create SNS topic for notifications
echo "Creating SNS topic..."
aws --endpoint-url=http://localhost:4566 sns create-topic --name vetterati-notifications

# Create SQS queue for notifications
echo "Creating SQS queue..."
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name vetterati-notifications

# Create Lambda function for processing (placeholder)
echo "Creating Lambda function..."
zip -j /tmp/function.zip << 'EOF'
exports.handler = async (event) => {
    console.log('Event:', JSON.stringify(event, null, 2));
    return {
        statusCode: 200,
        body: JSON.stringify('Hello from Lambda!')
    };
};
EOF

aws --endpoint-url=http://localhost:4566 lambda create-function \
    --function-name vetterati-processor \
    --runtime nodejs18.x \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --handler index.handler \
    --zip-file fileb:///tmp/function.zip

echo "AWS resources initialized successfully!"
