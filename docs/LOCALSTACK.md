# LocalStack Integration

This project uses LocalStack to emulate AWS services locally for development. LocalStack provides a fully functional local AWS cloud stack that runs in a Docker container.

## Services Emulated

- **S3**: Object storage for resume files and documents
- **DynamoDB**: NoSQL database for analytics and caching
- **SNS**: Simple Notification Service for event messaging
- **SQS**: Simple Queue Service for message queuing
- **Lambda**: Serverless function execution
- **IAM**: Identity and Access Management

## Getting Started

### Prerequisites

1. Docker and Docker Compose installed
2. AWS CLI installed (optional, for manual testing)

### Starting LocalStack

LocalStack will automatically start when you run the docker-compose stack:

```bash
docker-compose up -d localstack
```

### Verifying LocalStack

Check if LocalStack is running:

```bash
curl http://localhost:4566/health
```

### Accessing LocalStack Services

All AWS services are accessible via the LocalStack endpoint:
- **Endpoint**: http://localhost:4566
- **Region**: us-east-1
- **Access Key**: test
- **Secret Key**: test

### AWS CLI Configuration

To use AWS CLI with LocalStack:

```bash
aws configure set aws_access_key_id test
aws configure set aws_secret_access_key test
aws configure set default.region us-east-1
aws configure set default.output json
```

Then use with endpoint URL:
```bash
aws --endpoint-url=http://localhost:4566 s3 ls
aws --endpoint-url=http://localhost:4566 dynamodb list-tables
```

### Pre-configured Resources

The following resources are automatically created when LocalStack starts:

#### S3 Buckets
- `vetterati-resumes`: For storing resume files

#### DynamoDB Tables
- `analytics-events`: For storing application analytics
- `user-analytics`: For user behavior analytics

#### SNS Topics
- `vetterati-notifications`: For application notifications

#### SQS Queues
- `vetterati-notifications`: For processing notification messages

### Service Configuration

Services are configured with the following environment variables:

```yaml
environment:
  - AWS_ENDPOINT_URL=http://localstack:4566
  - AWS_DEFAULT_REGION=us-east-1
  - AWS_ACCESS_KEY_ID=test
  - AWS_SECRET_ACCESS_KEY=test
```

### Manual Initialization

If you need to manually initialize AWS resources, run:

```bash
# On Windows (PowerShell)
.\scripts\localstack\init-aws-resources.ps1

# On Linux/Mac
chmod +x scripts/localstack/init-aws-resources.sh
./scripts/localstack/init-aws-resources.sh
```

### Development Tips

1. **LocalStack Dashboard**: Visit http://localhost:4566 to see the LocalStack dashboard
2. **Persistence**: Data is stored in `./tmp/localstack` directory
3. **Logs**: View LocalStack logs with `docker-compose logs localstack`
4. **Reset**: To reset all data, stop LocalStack and delete the `./tmp/localstack` directory

### Troubleshooting

#### LocalStack not starting
- Check Docker is running
- Ensure ports 4566 and 4510-4559 are not in use
- Check logs: `docker-compose logs localstack`

#### Services can't connect to LocalStack
- Verify LocalStack is healthy: `curl http://localhost:4566/health`
- Check network connectivity between containers
- Verify environment variables are set correctly

#### AWS CLI issues
- Install AWS CLI v2
- Ensure correct endpoint URL is used
- Check credentials are set to 'test'

### Production Considerations

When deploying to production:

1. Replace LocalStack endpoints with real AWS service endpoints
2. Use proper AWS credentials and IAM roles
3. Configure appropriate security groups and VPCs
4. Set up proper backup and monitoring

### Resources

- [LocalStack Documentation](https://docs.localstack.cloud/)
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
