# Auth Service

The Vetterati Authentication Service handles user authentication, registration, and authorization.

## Features

- User registration and email/password login
- JWT token generation and refresh
- Password reset functionality
- Rate limiting protection
- Role-based access control
- Demo login for testing

## Demo Login Feature

For quick testing and development, the auth service provides predefined demo users with different roles.

### Available Demo Users

| Role | Name | Email | Description |
|------|------|-------|-------------|
| `admin` | Admin User | admin@vetterati.com | Full system administrator with all permissions |
| `recruiter` | Jane Recruiter | recruiter@company.com | Recruiter who can manage candidates and jobs |
| `hiring-manager` | John Manager | manager@company.com | Hiring manager who can review candidates and make decisions |
| `candidate` | Alice Candidate | candidate@email.com | Job candidate applying for positions |
| `interviewer` | Bob Interviewer | interviewer@company.com | Technical interviewer who conducts interviews |
| `hr` | Carol HR | hr@company.com | HR representative with recruiting capabilities |

### Usage

#### Demo Login
```bash
POST /api/v1/auth/demo-login
Content-Type: application/json

{
  "role": "admin"
}
```

Response:
```json
{
  "data": {
    "accessToken": "eyJ...",
    "refreshToken": "abc123...",
    "expiresIn": 3600,
    "tokenType": "Bearer",
    "user": {
      "id": "...",
      "email": "admin@vetterati.com",
      "name": "Admin User",
      "roles": ["admin", "recruiter"]
    }
  }
}
```

#### Get Demo Users List
```bash
GET /api/v1/auth/demo-users
```

### Regular Authentication

The service also supports standard authentication methods:

- **Registration**: `POST /api/v1/auth/register`
- **Email Login**: `POST /api/v1/auth/email-login`
- **SSO Login**: `POST /api/v1/auth/login`
- **Token Refresh**: `POST /api/v1/auth/refresh`
- **Logout**: `POST /api/v1/auth/logout`
- **Password Reset**: `POST /api/v1/auth/forgot-password`

## Development

```bash
# Build the service
dotnet build

# Run the service
dotnet run

# Run with watch mode
dotnet watch run
```

The service will be available at `https://localhost:7001` (or the configured port).

## Environment Variables

- `ASPNETCORE_ENVIRONMENT`: Development, Staging, or Production
- `ConnectionStrings__DefaultConnection`: Database connection string
- `ConnectionStrings__Redis`: Redis connection string
- `JWT__SecretKey`: JWT signing key
- `JWT__Issuer`: JWT issuer
- `JWT__Audience`: JWT audience

## Notes

- Demo users are automatically created on first use
- Demo users persist in the database like regular users
- The demo login feature should only be used in development/testing environments
- For production, ensure demo endpoints are disabled or protected
