# Vetterati - Modern Applicant Tracking System

[![CI/CD Pipeline](https://github.com/vetterati/ats/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/vetterati/ats/actions/workflows/ci-cd.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Overview

Vetterati is a cloud-native, modular Applicant Tracking System (ATS) designed to streamline and automate the hiring process. Built with modern microservices architecture, it leverages AI for intelligent candidate matching using the Analytic Hierarchy Process (AHP), provides robust analytics, and supports scalable workflow automation.

## Target Audience

  Current popular ATS solutions such as Workday - SUCK!, especially for applicants. It's 2025
  we should not be forcing applicants to re-enter data they have already provided in their resume.
  Plus the filtering/matching algorithms are very "inaccurate" in all the commercial ATS apps.

## ✨ Key Features

- **🔐 Modern Authentication**: JWT-based authentication with role-based access control
- **📄 Intelligent Resume Processing**: AI-powered resume parsing supporting TXT, PDF, and Word formats
- **🎯 AHP-Based Candidate Matching**: Advanced candidate scoring using Analytic Hierarchy Process
- **⚡ Real-time Workflow Management**: Automated interview scheduling and workflow state management
- **📊 Advanced Analytics**: Comprehensive hiring metrics, diversity reports, and predictive analytics
- **☁️ Cloud-Native Architecture**: Microservices deployed on AWS with Docker and Terraform
- **🎨 Modern React Frontend**: Responsive UI built with Material-UI and TypeScript

## 🏗️ Architecture

### Microservices
- **API Gateway** (C# .NET 8): Reverse proxy, rate limiting, routing
- **Authentication Service** (C# .NET 8): JWT authentication, user management
- **Resume Service** (Python FastAPI): Resume upload, parsing, search via Elasticsearch
- **AHP Engine** (C# .NET 8): Mathematical candidate scoring using AHP methodology
- **Workflow Service** (Python FastAPI): Interview scheduling, state management
- **Analytics Service** (Python FastAPI): Metrics, reporting, predictive analytics
- **Frontend** (React TypeScript): Modern responsive web interface

### Technology Stack
- **Backend**: C# .NET 8, Python 3.11, FastAPI
- **Frontend**: React 18, TypeScript, Material-UI
- **Databases**: PostgreSQL (RDBMS), DynamoDB (NoSQL), Elasticsearch (Search)
- **Caching**: Redis
- **Message Queue**: RabbitMQ
- **Infrastructure**: Docker, AWS ECS, Terraform
- **CI/CD**: GitHub Actions, AWS ECR

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Git
- Node.js 18+ (for frontend development)
- .NET 8 SDK (for .NET services development)
- Python 3.11+ (for Python services development)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/vetterati/ats.git
   cd ats
   ```

2. **Start all services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Initialize the database**
   ```bash
   # Database will be automatically initialized on first run
   # Check logs: docker-compose logs postgres
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:5000
   - Analytics Service: http://localhost:8003

### Service URLs (Local Development)
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:5000
- **Auth Service**: http://localhost:5001
- **Resume Service**: http://localhost:8001
- **AHP Service**: http://localhost:5002
- **Workflow Service**: http://localhost:8002
- **Analytics Service**: http://localhost:8003

### Database Access
- **PostgreSQL**: localhost:5432 (user: ats_user, password: ats_password, db: vetterati_ats)
- **Redis**: localhost:6379
- **Elasticsearch**: http://localhost:9200
- **RabbitMQ Management**: http://localhost:15672 (user: ats_user, password: ats_password)

## 📁 Project Structure

```
vetterati/
├── .github/workflows/          # CI/CD pipeline configurations
├── infrastructure/terraform/   # AWS infrastructure as code
├── scripts/                   # Database initialization scripts
├── src/
│   ├── frontend/              # React TypeScript frontend
│   ├── services/              # Microservices
│   │   ├── api-gateway/       # C# API Gateway (YARP)
│   │   ├── auth-service/      # C# Authentication service
│   │   ├── resume-service/    # Python resume management
│   │   ├── ahp-service/       # C# AHP scoring engine
│   │   ├── workflow-service/  # Python workflow management
│   │   └── analytics-service/ # Python analytics & reporting
│   └── shared/                # Shared libraries
│       ├── dotnet/           # .NET shared models
│       └── python/           # Python shared utilities
├── tests/                     # Unit and integration tests
├── docker-compose.yml         # Local development environment
└── README.md
```

## 🧪 Testing

### Run All Tests
```bash
# .NET Tests
dotnet test

# Python Tests
cd tests
python -m pytest -v

# Frontend Tests
cd src/frontend
npm test
```

### Integration Tests
```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
npm run test:integration
```

## 🚀 Deployment

### AWS Deployment with Terraform

1. **Configure AWS credentials**
   ```bash
   aws configure
   ```

2. **Deploy infrastructure**
   ```bash
   cd infrastructure/terraform
   terraform init
   terraform plan -var="db_password=your_secure_password"
   terraform apply
   ```

3. **Deploy services**
   ```bash
   # CI/CD pipeline automatically deploys on main branch push
   # Or manually deploy using AWS CLI/ECS
   ```

### Environment Variables

#### Production Environment
Create a `.env` file or set environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/vetterati_ats
REDIS_URL=redis://redis-host:6379

# Authentication
JWT_SECRET=your-jwt-secret
JWT_EXPIRY_MINUTES=60

# AWS Services
AWS_REGION=us-west-2
S3_BUCKET=vetterati-files
ELASTICSEARCH_URL=https://elasticsearch-host:443

# External Services
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
```

## 📊 API Documentation

### Authentication
```bash
# Login
POST /auth/login
{
  "email": "user@example.com",
  "password": "password"
}

# Get user info
GET /auth/user
Authorization: Bearer <token>
```

### Resume Management
```bash
# Upload resume
POST /api/resumes/upload
Content-Type: multipart/form-data

# Search candidates
GET /api/resumes/search?q=python&experience=5
```

### AHP Scoring
```bash
# Score candidate
POST /api/ahp/score
{
  "candidateId": "uuid",
  "jobId": "uuid"
}
```

### Analytics
```bash
# Get dashboard data
GET /api/analytics/dashboard?timeframe=30d

# Generate custom report
POST /api/analytics/reports/custom
{
  "reportType": "hiring_metrics",
  "dateRange": {"start": "2024-01-01", "end": "2024-01-31"}
}
```

## 🔧 Development

### Adding a New Service

1. **Create service directory**
   ```bash
   mkdir src/services/new-service
   cd src/services/new-service
   ```

2. **Add to docker-compose.yml**
   ```yaml
   new-service:
     build:
       context: ./src/services/new-service
     ports:
       - "8004:8000"
     networks:
       - ats-network
   ```

3. **Update API Gateway routing**
   ```json
   {
     "Routes": {
       "NewService": {
         "ClusterId": "new-service",
         "Match": {
           "Path": "/api/new-service/{**catch-all}"
         }
       }
     }
   }
   ```

### Code Style and Standards

- **C#**: Follow .NET coding conventions, use EditorConfig
- **Python**: Follow PEP 8, use Black formatter, type hints required
- **TypeScript**: Follow ESLint rules, Prettier formatting
- **Git**: Conventional commit messages, feature branch workflow

## 🔍 Monitoring and Observability

### Logging
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: ERROR, WARN, INFO, DEBUG
- **Centralized**: CloudWatch Logs in AWS

### Metrics
- **Application Metrics**: Response times, error rates, throughput
- **Business Metrics**: Applications processed, time-to-hire, conversion rates
- **Infrastructure Metrics**: CPU, memory, disk usage

### Health Checks
```bash
# Service health endpoints
GET /health

# Readiness checks
GET /ready

# Metrics endpoint
GET /metrics
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Write tests for new features
- Update documentation
- Follow coding standards
- Ensure CI/CD pipeline passes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [Wiki](https://github.com/vetterati/ats/wiki)
- **Issues**: [GitHub Issues](https://github.com/vetterati/ats/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vetterati/ats/discussions)

## 🙏 Acknowledgments

- **MathNet.Numerics**: For AHP mathematical computations
- **FastAPI**: For high-performance Python APIs
- **Material-UI**: For modern React components
- **YARP**: For .NET reverse proxy functionality

---

**Built with ❤️ by the Vetterati Team**
  - **Level 1**: Overall candidate fit (goal)
  - **Level 2**: Major criteria categories (Experience, Education, Cultural Fit, Technical Skills)
  - **Level 3**: Specific attributes (years of experience, education prestige, company types, etc.)
- **Candidate Match Result**: Stores detailed scoring breakdown including:
  - Individual attribute scores and weights
  - AHP-calculated composite scores for each ideal candidate profile
  - Explanation vectors showing attribute contribution to final scores
- **AHP Calculation Engine**: Mathematical framework for:
  - Eigenvalue calculations for priority derivation
  - Consistency index and ratio computations
  - Sensitivity analysis for weight adjustments

## AHP-Based Scoring Formula Examples

### Example 1: Senior Software Engineer Position with AHP Weighting

**AHP Hierarchy:**
```
Goal: Best Senior Software Engineer
├── Technical Experience (40% weight via AHP)
│   ├── Years of Programming (60%)
│   ├── Relevant Tech Stack (30%)
│   └── Architecture Experience (10%)
├── Leadership & Growth (30% weight via AHP)
│   ├── Team Management (50%)
│   ├── Mentoring Experience (30%)
│   └── Career Progression (20%)
├── Cultural Fit (20% weight via AHP)
│   ├── Company Size Preference (40%)
│   ├── Work Style Compatibility (35%)
│   └── Values Alignment (25%)
└── Education & Certifications (10% weight via AHP)
    ├── Degree Level (70%)
    └── Professional Certifications (30%)
```

**Candidate Scoring:**
```
Ideal Candidate A (Tech Lead Type): Weight = 100
- Technical Experience: 85% match × 40% weight = 34 points
- Leadership & Growth: 90% match × 30% weight = 27 points  
- Cultural Fit: 75% match × 20% weight = 15 points
- Education: 80% match × 10% weight = 8 points
Total AHP Score: 84 points → Final Score = 84

Ideal Candidate B (IC Expert Type): Weight = 70
- Technical Experience: 95% match × 40% weight = 38 points
- Leadership & Growth: 40% match × 30% weight = 12 points
- Cultural Fit: 85% match × 20% weight = 17 points  
- Education: 90% match × 10% weight = 9 points
Total AHP Score: 76 points → Final Score = 53.2 (76 × 0.7)
```

### Example 2: Career Pattern Analysis
```
Big Fish/Little Pond vs Little Fish/Big Pond Assessment:
- Candidate from startup (big fish): Leadership weight +20%, scope weight +15%
- Candidate from FAANG (little fish): Process weight +25%, scale weight +30%
AHP automatically adjusts attribute weights based on career pattern classification.
```

### 4. Interview & Workflow Management
- **Interview Scheduling**: Integrate with calendar systems (e.g., Google Calendar, Outlook) to schedule interviews with shortlisted candidates.
- **Workflow Automation**: Track and automate candidate progress through customizable hiring stages (e.g., application, screening, interview, offer, hire).
- **Notifications**: Automated email and in-app notifications for candidates and hiring team at each workflow stage.

### 5. Analytics & Reporting
- **Hiring Analytics**: Provide dashboards and reports on key hiring metrics (e.g., time-to-hire, source effectiveness, diversity, pipeline health).
- **AHP Model Performance**: Track effectiveness of different AHP hierarchies and attribute weightings across successful hires.
- **Scoring Analytics**: 
  - Correlation analysis between AHP scores and actual job performance
  - Attribute importance analysis showing which criteria predict success
  - AHP model validation through hire outcome tracking
- **Career Pattern Analytics**: Report on hiring success rates for different candidate archetypes (big fish/little pond classifications).
- **Decision Consistency Metrics**: Monitor consistency ratios across different recruiters and hiring managers to ensure reliable decision-making.
- **Ideal Candidate Performance**: Report on which ideal candidate archetypes and AHP models are most effective for different roles and departments.
- **Custom AHP Reports**: Generate reports showing:
  - Detailed AHP calculations and weight derivations
  - Sensitivity analysis results for key hiring decisions
  - Comparative analysis of candidates across multiple criteria
- **Compliance Reporting**: Support reporting for legal and regulatory compliance (e.g., EEOC, GDPR) with audit trails of AHP-based decisions.

## Technical Requirements

### 1. Ideal Candidate Management System
- **Profile Creation Interface**: Intuitive UI for creating and editing multiple ideal candidate profiles per job opening.
- **AHP Hierarchy Builder**: Visual interface for constructing decision hierarchies and defining criteria relationships.
- **Pairwise Comparison Tool**: User-friendly matrix interface for conducting AHP pairwise comparisons between attributes.
- **Weight Assignment**: 
  - Slider or numeric input for assigning weights (1-100) to each ideal candidate profile
  - Automatic weight derivation from AHP pairwise comparison matrices
  - Real-time consistency ratio calculation and validation
- **Profile Templates**: Ability to save and reuse ideal candidate profiles and AHP hierarchies across similar job openings.
- **Attribute Library**: Predefined library of common attributes with suggested AHP weightings for different role types.

### 2. AI Matching Engine with AHP Integration
- **Multi-Profile Matching**: Capability to match each candidate against multiple ideal profiles simultaneously using AHP-derived weights.
- **AHP Calculation Engine**: 
  - Eigenvalue/eigenvector computation for priority derivation
  - Consistency index and consistency ratio calculations
  - Sensitivity analysis for weight perturbations
- **Explainable AI Scoring**: Implementation of AHP-guided scoring system with detailed attribute contribution analysis.
- **Career Pattern Recognition**: AI algorithms to classify candidates into career archetypes (big fish/little pond, etc.) and adjust weights accordingly.
- **Match Explanation Engine**: Provide detailed breakdown showing:
  - Individual attribute scores and their AHP-derived weights
  - Contribution of each criterion to final composite score
  - Comparison against ideal candidate profiles with justification

### 3. Candidate Ranking & Filtering
- **AHP-Based Score Display**: Show detailed scoring breakdown including:
  - Individual attribute scores with AHP-derived weights
  - Composite scores for each ideal candidate profile
  - Overall ranking based on weighted composite scores
- **Multi-Criteria Sorting**: Sort by AHP composite score, individual ideal candidate matches, specific attributes, application date, or custom criteria.
- **Advanced AHP Filters**: 
  - Filter by AHP score ranges and attribute-specific thresholds
  - Filter by career pattern classifications (startup vs. corporate experience)
  - Filter by specific attribute combinations (e.g., high technical + high leadership)
- **Interactive Score Visualization**: 
  - AHP hierarchy trees showing weight distributions
  - Radar charts comparing candidates across multiple attributes
  - Sensitivity analysis charts showing impact of weight changes
  - Candidate clustering based on AHP-derived similarity measures

## Non-Functional Requirements

- **Scalability**: System should support growth in users, candidates, and job postings.
- **Reliability**: High availability and robust error handling.
- **Performance**: Fast search, filtering, and AI matching for large candidate pools.
- **Integrations**: APIs for integration with HRIS, job boards, and third-party tools.
- **Usability**: Intuitive, accessible UI for all user roles.
- **Audit Logging**: Track all key actions for security and compliance.

## Future Enhancements (Optional)
- **Mobile App**: Native or responsive mobile experience with AHP decision support tools.
- **Video Interviewing**: Built-in or integrated video interview platform with AHP-guided interview questions.
- **Offer Management**: Automated offer letter generation and e-signature with AHP-justified compensation recommendations.
- **Onboarding Integration**: Seamless handoff to onboarding systems with AHP profile data for personalized onboarding paths.
- **Advanced AHP Features**:
  - **Group Decision Making**: AHP aggregation methods for multiple stakeholder input
  - **Fuzzy AHP**: Handle uncertainty and imprecision in judgments
  - **Dynamic AHP**: Real-time weight adjustment based on changing market conditions
  - **AHP Learning**: Machine learning to suggest optimal AHP structures based on historical success
- **Predictive Analytics**: 
  - Predict candidate success probability using AHP scores and historical performance data
  - Forecast hiring outcomes based on AHP model configurations
- **AI-Powered AHP Optimization**: 
  - Automatically suggest optimal AHP hierarchies and weights based on successful hires
  - Continuous learning to refine attribute importance and ideal candidate profiles
- **Behavioral Analytics**: Integration with assessment tools to validate AHP-predicted cultural fit and performance.

---

This requirements document serves as the foundation for the design and implementation of the ATS. Further technical specifications and architecture diagrams will be developed in subsequent phases.
