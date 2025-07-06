# Notification Service

The Notification Service is a microservice responsible for managing and sending notifications across multiple channels in the Vetterati ATS system.

## Features

- **Multi-channel notifications**: Email, SMS, Push, Slack, Webhooks
- **Template management**: Create, update, and manage notification templates with Jinja2 templating
- **User preferences**: Manage user notification preferences and quiet hours
- **Bulk notifications**: Send notifications to multiple recipients efficiently
- **Queue processing**: Background processing of notifications with retry logic
- **Delivery tracking**: Track delivery status and handle webhook updates
- **Statistics**: Comprehensive notification statistics and reporting

## API Endpoints

### Templates
- `POST /api/v1/templates` - Create notification template
- `GET /api/v1/templates` - List templates
- `GET /api/v1/templates/{id}` - Get template by ID
- `PUT /api/v1/templates/{id}` - Update template
- `DELETE /api/v1/templates/{id}` - Delete template
- `POST /api/v1/templates/{id}/render` - Render template with context

### Notifications
- `POST /api/v1/notifications` - Create single notification
- `POST /api/v1/notifications/bulk` - Create bulk notifications
- `GET /api/v1/notifications` - List notifications with filtering
- `GET /api/v1/notifications/{id}` - Get notification by ID
- `PUT /api/v1/notifications/{id}` - Update notification
- `DELETE /api/v1/notifications/{id}` - Delete notification
- `GET /api/v1/notifications/{id}/logs` - Get notification logs

### User Preferences
- `GET /api/v1/users/{user_id}/preferences` - Get user notification preferences
- `POST /api/v1/users/{user_id}/preferences` - Create user preferences
- `PUT /api/v1/users/{user_id}/preferences` - Update user preferences

### Statistics
- `GET /api/v1/stats` - Get notification statistics

### Queue Management
- `GET /api/v1/queue/pending` - Get pending notifications
- `POST /api/v1/queue/process` - Process pending notifications

### Webhooks
- `POST /api/v1/webhooks/delivery-status` - Handle delivery status updates

## Configuration

The service uses environment variables for configuration:

### Database
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `RABBITMQ_URL`: RabbitMQ connection string

### Email Configuration
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP server port (default: 587)
- `SMTP_USERNAME`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `SMTP_USE_TLS`: Use TLS encryption (default: true)

### SMS Configuration (Twilio)
- `SMS_PROVIDER`: SMS provider (default: twilio)
- `TWILIO_ACCOUNT_SID`: Twilio account SID
- `TWILIO_AUTH_TOKEN`: Twilio auth token
- `TWILIO_FROM_NUMBER`: Twilio phone number

### Slack Configuration
- `SLACK_WEBHOOK_URL`: Slack webhook URL
- `SLACK_BOT_TOKEN`: Slack bot token

### Push Notifications
- `FIREBASE_SERVER_KEY`: Firebase server key for FCM
- `APNS_KEY`: Apple Push Notification Service key

### Webhooks
- `DEFAULT_WEBHOOK_URL`: Default webhook URL

## Sample Templates

The service includes several pre-configured templates:

1. **Application Received** - Confirmation email for candidates
2. **Interview Scheduled** - Interview invitation email
3. **Interview Reminder** - Email reminder 24 hours before interview
4. **Application Status Update** - General status update email
5. **New Application Alert** - Slack alert for recruiters
6. **Interview No-Show** - Slack alert for missed interviews
7. **SMS Interview Reminder** - SMS reminder 2 hours before interview

## Template Variables

Templates use Jinja2 syntax and support the following common variables:

### Candidate Variables
- `candidate_name`: Candidate's full name
- `candidate_email`: Candidate's email address

### Job Variables
- `job_title`: Job position title
- `company_name`: Company name
- `department`: Department name

### Interview Variables
- `interview_date`: Interview date
- `interview_time`: Interview time
- `interview_location`: Interview location
- `meeting_link`: Video meeting link
- `interviewer_names`: Names of interviewers

### Application Variables
- `application_id`: Unique application ID
- `submission_date`: Application submission date
- `status_update`: Current application status

## Database Schema

The service uses the following main tables:

- `notification_templates`: Template definitions
- `notifications`: Individual notification records
- `notification_preferences`: User notification preferences
- `notification_logs`: Audit logs for notifications

## Usage Examples

### Creating a Notification Template

```json
{
  "name": "Welcome Email",
  "description": "Welcome email for new candidates",
  "channel": "email",
  "subject_template": "Welcome {{ candidate_name }}!",
  "body_template": "Dear {{ candidate_name }},\n\nWelcome to {{ company_name }}!",
  "variables": {
    "candidate_name": "string",
    "company_name": "string"
  },
  "tags": ["welcome", "onboarding"]
}
```

### Sending a Single Notification

```json
{
  "template_id": "template-uuid",
  "channel": "email",
  "recipient_email": "candidate@example.com",
  "context_data": {
    "candidate_name": "John Doe",
    "company_name": "Vetterati"
  },
  "priority": "normal"
}
```

### Sending Bulk Notifications

```json
{
  "template_id": "template-uuid",
  "recipients": [
    {
      "recipient_email": "candidate1@example.com",
      "candidate_name": "John Doe"
    },
    {
      "recipient_email": "candidate2@example.com", 
      "candidate_name": "Jane Smith"
    }
  ],
  "context_data": {
    "company_name": "Vetterati"
  }
}
```

## Development

### Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/vetterati_ats"
   export REDIS_URL="redis://localhost:6379"
   ```

3. Run the service:
   ```bash
   python main.py
   ```

### Docker

Build and run with Docker:

```bash
docker build -t notification-service .
docker run -p 8006:8000 notification-service
```

### Testing

The service includes comprehensive API documentation available at `/docs` when running.

## Integration

The Notification Service integrates with:

- **Workflow Service**: Receives workflow triggers for sending notifications
- **Job Service**: Gets job-related data for notifications
- **Candidate Service**: Gets candidate data for notifications
- **Authentication Service**: Validates user permissions

## Error Handling

The service implements robust error handling:

- Automatic retries with exponential backoff
- Dead letter queues for failed notifications
- Comprehensive logging and monitoring
- Graceful degradation when external services are unavailable

## Monitoring

Key metrics to monitor:

- Notification delivery rates by channel
- Processing queue length
- Failed notification rates
- Response times
- Template usage statistics
