# API Specifications

## Overview
This document provides comprehensive API specifications for the ATS system, including REST endpoints, request/response schemas, authentication, and integration patterns.

## API Design Principles

### RESTful Design
- **Resource-based URLs**: `/api/v1/candidates/{id}` instead of `/api/v1/getCandidate`
- **HTTP Methods**: Proper use of GET, POST, PUT, PATCH, DELETE
- **Status Codes**: Meaningful HTTP status codes for all responses
- **Idempotency**: PUT and PATCH operations are idempotent
- **Stateless**: Each request contains all necessary information

### Versioning Strategy
- **URL Versioning**: `/api/v1/` in the URL path
- **Semantic Versioning**: Major.Minor.Patch (e.g., v1.2.1)
- **Backward Compatibility**: Maintain compatibility within major versions
- **Deprecation Policy**: 6-month notice for breaking changes

### Response Format
```json
{
  "data": {},
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.2.1",
    "request_id": "req_123456789"
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  },
  "links": {
    "self": "/api/v1/candidates?page=1",
    "next": "/api/v1/candidates?page=2",
    "prev": null,
    "first": "/api/v1/candidates?page=1",
    "last": "/api/v1/candidates?page=8"
  }
}
```

## Authentication & Authorization

### Authentication Flow
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "provider": "google|microsoft|okta",
  "code": "authorization_code",
  "redirect_uri": "https://app.ats.com/callback"
}

Response:
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "def50200...",
    "expires_in": 3600,
    "token_type": "Bearer",
    "user": {
      "id": "user_123",
      "email": "user@company.com",
      "name": "John Doe",
      "roles": ["recruiter", "interviewer"]
    }
  }
}
```

### Authorization Headers
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-API-Version: v1
X-Request-ID: req_123456789
Content-Type: application/json
```

### Token Refresh
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "def50200..."
}
```

## Core API Endpoints

### User Management API

#### Get Current User
```http
GET /api/v1/users/me
Authorization: Bearer {token}

Response:
{
  "data": {
    "id": "user_123",
    "email": "user@company.com",
    "name": "John Doe",
    "roles": ["recruiter"],
    "preferences": {
      "timezone": "America/New_York",
      "notifications": {
        "email": true,
        "push": false
      }
    },
    "last_login_at": "2024-01-15T10:30:00Z",
    "created_at": "2023-06-01T09:00:00Z"
  }
}
```

#### Update User Preferences
```http
PATCH /api/v1/users/me/preferences
Content-Type: application/json

{
  "timezone": "America/Los_Angeles",
  "notifications": {
    "email": true,
    "push": true,
    "interview_reminders": true
  }
}
```

#### List Users (Admin Only)
```http
GET /api/v1/users
Query Parameters:
  - page: integer (default: 1)
  - per_page: integer (default: 20, max: 100)
  - role: string (filter by role)
  - active: boolean (filter by active status)
  - search: string (search name/email)

Response:
{
  "data": [
    {
      "id": "user_123",
      "name": "John Doe",
      "email": "john@company.com",
      "roles": ["recruiter"],
      "is_active": true,
      "last_login_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {...}
}
```

### Job Management API

#### Create Job Posting
```http
POST /api/v1/jobs
Content-Type: application/json

{
  "title": "Senior Software Engineer",
  "description": "We are looking for a senior software engineer...",
  "department": "Engineering",
  "location": "San Francisco, CA",
  "employment_type": "full_time",
  "job_level": "senior",
  "requirements": {
    "education": "bachelor",
    "experience_years": 5,
    "required_skills": ["javascript", "react", "node.js"],
    "preferred_skills": ["typescript", "aws"]
  },
  "benefits": {
    "salary_range": {
      "min": 120000,
      "max": 180000,
      "currency": "USD"
    },
    "equity": true,
    "health_insurance": true,
    "retirement_plan": true
  }
}

Response:
{
  "data": {
    "id": "job_123",
    "title": "Senior Software Engineer",
    "status": "draft",
    "created_by": "user_123",
    "created_at": "2024-01-15T10:30:00Z",
    ...
  }
}
```

#### Get Job Details
```http
GET /api/v1/jobs/{job_id}

Response:
{
  "data": {
    "id": "job_123",
    "title": "Senior Software Engineer",
    "description": "We are looking for...",
    "status": "active",
    "created_by": "user_123",
    "posted_at": "2024-01-15T14:00:00Z",
    "applications_count": 25,
    "ahp_hierarchies": [
      {
        "id": "ahp_123",
        "name": "Senior Engineer Hierarchy",
        "is_active": true
      }
    ],
    "ideal_profiles": [
      {
        "id": "profile_123",
        "name": "Tech Lead Archetype",
        "weight": 100
      }
    ]
  }
}
```

#### List Jobs
```http
GET /api/v1/jobs
Query Parameters:
  - page: integer
  - per_page: integer
  - status: string (active|draft|closed)
  - department: string
  - location: string
  - created_by: uuid
  - search: string

Response:
{
  "data": [
    {
      "id": "job_123",
      "title": "Senior Software Engineer",
      "department": "Engineering",
      "status": "active",
      "applications_count": 25,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {...}
}
```

### Candidate Management API

#### Create Candidate Profile
```http
POST /api/v1/candidates
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@email.com",
  "phone": "+1-555-123-4567",
  "location": {
    "city": "San Francisco",
    "state": "CA",
    "country": "US",
    "coordinates": {
      "lat": 37.7749,
      "lng": -122.4194
    }
  },
  "linkedin_url": "https://linkedin.com/in/janesmith",
  "portfolio_url": "https://janesmith.dev",
  "experience": [
    {
      "company": "Tech Corp",
      "position": "Software Engineer",
      "start_date": "2022-01-01",
      "end_date": "2024-01-01",
      "description": "Developed web applications using React and Node.js",
      "skills": ["javascript", "react", "node.js"],
      "achievements": ["Increased performance by 40%", "Led team of 3 developers"]
    }
  ],
  "education": [
    {
      "institution": "University of California, Berkeley",
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "start_date": "2018-08-01",
      "end_date": "2022-05-01",
      "gpa": 3.8
    }
  ],
  "skills": {
    "technical": [
      {
        "name": "javascript",
        "level": "expert",
        "years_experience": 4
      },
      {
        "name": "react",
        "level": "advanced",
        "years_experience": 3
      }
    ],
    "soft": ["leadership", "communication", "problem_solving"]
  }
}

Response:
{
  "data": {
    "id": "candidate_123",
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@email.com",
    "career_metrics": {
      "total_years_experience": 4,
      "average_tenure": 24,
      "career_progression": "linear"
    },
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Search Candidates
```http
GET /api/v1/candidates/search
Query Parameters:
  - q: string (full-text search)
  - skills: comma-separated skills
  - location: string
  - experience_min: integer (minimum years)
  - experience_max: integer (maximum years)
  - education_level: string
  - company: string (previous company)
  - page: integer
  - per_page: integer
  - sort_by: string (relevance|created_at|name)
  - sort_order: string (asc|desc)

Example:
GET /api/v1/candidates/search?q=react&skills=javascript,node.js&experience_min=3&location=San Francisco

Response:
{
  "data": [
    {
      "id": "candidate_123",
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane.smith@email.com",
      "location": {
        "city": "San Francisco",
        "state": "CA"
      },
      "experience_summary": {
        "total_years": 4,
        "current_position": "Software Engineer at Tech Corp",
        "key_skills": ["javascript", "react", "node.js"]
      },
      "match_score": 0.85,
      "highlight": {
        "skills": ["<em>react</em>", "<em>javascript</em>"],
        "experience": ["Developed web applications using <em>React</em>"]
      }
    }
  ],
  "pagination": {...},
  "facets": {
    "skills": {
      "javascript": 156,
      "react": 98,
      "python": 87
    },
    "experience_levels": {
      "1-3": 45,
      "3-5": 78,
      "5+": 123
    }
  }
}
```

### Resume Management API

#### Upload Resume
```http
POST /api/v1/resumes/upload
Content-Type: multipart/form-data

Form Data:
  - file: (binary file)
  - candidate_id: uuid (optional, for existing candidates)
  - job_id: uuid (optional, for job applications)
  - source: string (web|email|integration)

Response:
{
  "data": {
    "id": "resume_123",
    "candidate_id": "candidate_123",
    "filename": "jane_smith_resume.pdf",
    "file_size": 245760,
    "upload_source": "web",
    "processing_status": "queued",
    "upload_url": "https://cdn.ats.com/resumes/resume_123.pdf",
    "uploaded_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Get Resume Processing Status
```http
GET /api/v1/resumes/{resume_id}/status

Response:
{
  "data": {
    "id": "resume_123",
    "processing_status": "completed",
    "parsing_confidence": 0.92,
    "processing_time": 2.3,
    "extracted_data": {
      "contact_info": {
        "email": "jane.smith@email.com",
        "phone": "+1-555-123-4567"
      },
      "skills_found": ["javascript", "react", "node.js"],
      "experience_count": 3,
      "education_count": 1
    },
    "quality_score": 0.89,
    "issues": []
  }
}
```

#### Bulk Resume Import
```http
POST /api/v1/resumes/bulk-import
Content-Type: application/json

{
  "job_id": "job_123",
  "source": "job_board_integration",
  "resumes": [
    {
      "url": "https://external.com/resume1.pdf",
      "candidate_info": {
        "email": "candidate1@email.com",
        "name": "John Doe"
      }
    },
    {
      "url": "https://external.com/resume2.pdf",
      "candidate_info": {
        "email": "candidate2@email.com",
        "name": "Jane Doe"
      }
    }
  ]
}

Response:
{
  "data": {
    "batch_id": "batch_123",
    "total_resumes": 2,
    "status": "processing",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### AHP Management API

#### Create AHP Hierarchy
```http
POST /api/v1/jobs/{job_id}/ahp-hierarchies
Content-Type: application/json

{
  "name": "Senior Engineer Evaluation",
  "description": "AHP hierarchy for evaluating senior software engineers",
  "hierarchy": {
    "goal": {
      "name": "Best Senior Software Engineer",
      "criteria": [
        {
          "id": "technical_experience",
          "name": "Technical Experience",
          "weight": 0.4,
          "subcriteria": [
            {
              "id": "programming_years",
              "name": "Years of Programming",
              "weight": 0.6,
              "type": "numeric",
              "range": {"min": 0, "max": 15}
            },
            {
              "id": "tech_stack",
              "name": "Technology Stack Match",
              "weight": 0.4,
              "type": "categorical",
              "values": ["exact", "similar", "transferable"]
            }
          ]
        },
        {
          "id": "leadership",
          "name": "Leadership Experience",
          "weight": 0.3,
          "type": "numeric",
          "range": {"min": 0, "max": 10}
        }
      ]
    }
  },
  "pairwise_matrices": {
    "root": [
      [1, 2, 3],
      [0.5, 1, 2],
      [0.33, 0.5, 1]
    ],
    "technical_experience": [
      [1, 1.5],
      [0.67, 1]
    ]
  }
}

Response:
{
  "data": {
    "id": "ahp_123",
    "job_id": "job_123",
    "name": "Senior Engineer Evaluation",
    "consistency_ratios": {
      "root": 0.037,
      "technical_experience": 0.0
    },
    "is_valid": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Update AHP Weights
```http
PUT /api/v1/ahp-hierarchies/{hierarchy_id}/weights
Content-Type: application/json

{
  "pairwise_matrices": {
    "root": [
      [1, 2.5, 3],
      [0.4, 1, 2],
      [0.33, 0.5, 1]
    ]
  }
}

Response:
{
  "data": {
    "hierarchy_id": "ahp_123",
    "updated_weights": {
      "technical_experience": 0.45,
      "leadership": 0.35,
      "culture_fit": 0.20
    },
    "consistency_ratios": {
      "root": 0.041
    },
    "is_valid": true,
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

### Candidate Scoring API

#### Score Candidate Against Job
```http
POST /api/v1/candidates/{candidate_id}/score
Content-Type: application/json

{
  "job_id": "job_123",
  "ahp_hierarchy_id": "ahp_123",
  "force_recalculate": false
}

Response:
{
  "data": {
    "candidate_id": "candidate_123",
    "job_id": "job_123",
    "overall_score": 84.5,
    "profile_matches": [
      {
        "ideal_profile_id": "profile_123",
        "profile_name": "Tech Lead Archetype",
        "raw_score": 84.5,
        "weighted_score": 84.5,
        "profile_weight": 100
      }
    ],
    "attribute_scores": [
      {
        "criteria_id": "technical_experience",
        "criteria_name": "Technical Experience",
        "score": 88,
        "weight": 0.4,
        "contribution": 35.2,
        "subcriteria": [
          {
            "id": "programming_years",
            "name": "Years of Programming",
            "candidate_value": 6,
            "ideal_value": 8,
            "score": 85,
            "weight": 0.6
          }
        ]
      }
    ],
    "explanation": {
      "strengths": ["Strong technical background", "Good leadership potential"],
      "weaknesses": ["Limited enterprise experience"],
      "recommendations": ["Consider for senior technical roles"],
      "confidence_level": 0.87
    },
    "calculated_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Get Job Candidate Rankings
```http
GET /api/v1/jobs/{job_id}/candidate-rankings
Query Parameters:
  - min_score: number (minimum AHP score)
  - ideal_profile_id: uuid (filter by specific ideal profile)
  - sort_by: string (overall_score|profile_match|application_date)
  - sort_order: string (asc|desc)
  - page: integer
  - per_page: integer

Response:
{
  "data": [
    {
      "candidate_id": "candidate_123",
      "candidate_name": "Jane Smith",
      "overall_score": 84.5,
      "top_profile_match": {
        "profile_name": "Tech Lead Archetype",
        "score": 84.5
      },
      "application_date": "2024-01-10T09:00:00Z",
      "current_stage": "phone_screen",
      "resume_url": "https://cdn.ats.com/resumes/resume_123.pdf"
    }
  ],
  "pagination": {...},
  "summary": {
    "total_candidates": 156,
    "avg_score": 67.2,
    "score_distribution": {
      "90-100": 12,
      "80-89": 34,
      "70-79": 56,
      "60-69": 38,
      "below_60": 16
    }
  }
}
```

### Interview Management API

#### Schedule Interview
```http
POST /api/v1/interviews
Content-Type: application/json

{
  "candidate_id": "candidate_123",
  "job_id": "job_123",
  "workflow_stage_id": "technical_interview",
  "title": "Technical Interview",
  "type": "video",
  "duration_minutes": 90,
  "scheduled_start": "2024-01-20T14:00:00Z",
  "location": "https://zoom.us/j/123456789",
  "interviewers": [
    {
      "user_id": "user_456",
      "role": "primary"
    },
    {
      "user_id": "user_789",
      "role": "secondary"
    }
  ],
  "interview_guide_id": "guide_123",
  "notes": "Focus on React and system design"
}

Response:
{
  "data": {
    "id": "interview_123",
    "candidate_id": "candidate_123",
    "job_id": "job_123",
    "title": "Technical Interview",
    "status": "scheduled",
    "scheduled_start": "2024-01-20T14:00:00Z",
    "scheduled_end": "2024-01-20T15:30:00Z",
    "calendar_events": [
      {
        "provider": "google",
        "event_id": "cal_event_123",
        "participant": "interviewer@company.com"
      }
    ],
    "zoom_link": "https://zoom.us/j/123456789",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Submit Interview Evaluation
```http
POST /api/v1/interviews/{interview_id}/evaluation
Content-Type: application/json

{
  "overall_score": 4.2,
  "dimension_scores": {
    "technical_skills": 4.5,
    "communication": 4.0,
    "problem_solving": 4.3,
    "culture_fit": 4.0
  },
  "recommendation": "hire",
  "feedback": "Strong technical skills, excellent problem-solving approach. Good communication and would fit well with the team culture.",
  "question_responses": [
    {
      "question_id": "q1",
      "question": "Explain React component lifecycle",
      "response_quality": 4,
      "notes": "Comprehensive understanding of hooks and class components"
    }
  ],
  "follow_up_questions": [
    "System design question about scaling",
    "Behavioral question about conflict resolution"
  ],
  "duration_minutes": 85
}

Response:
{
  "data": {
    "interview_id": "interview_123",
    "evaluation_id": "eval_123",
    "overall_score": 4.2,
    "recommendation": "hire",
    "submitted_by": "user_456",
    "submitted_at": "2024-01-20T15:45:00Z",
    "next_stage_recommendation": "final_interview"
  }
}
```

### Workflow Management API

#### Advance Candidate Workflow
```http
POST /api/v1/workflows/{workflow_id}/advance
Content-Type: application/json

{
  "decision": "approved",
  "notes": "Strong candidate, moving to technical interview",
  "next_stage": "technical_interview",
  "artifacts": ["interview_eval_123", "resume_review_456"]
}

Response:
{
  "data": {
    "workflow_id": "workflow_123",
    "candidate_id": "candidate_123",
    "previous_stage": "phone_screen",
    "current_stage": "technical_interview",
    "decision": "approved",
    "decision_maker": "user_456",
    "updated_at": "2024-01-15T10:30:00Z",
    "automated_actions": [
      "interview_scheduled",
      "notification_sent"
    ]
  }
}
```

#### Get Workflow Status
```http
GET /api/v1/workflows/{workflow_id}

Response:
{
  "data": {
    "id": "workflow_123",
    "candidate_id": "candidate_123",
    "job_id": "job_123",
    "current_stage": "technical_interview",
    "status": "in_progress",
    "started_at": "2024-01-10T09:00:00Z",
    "stage_history": [
      {
        "stage_id": "application",
        "entered_at": "2024-01-10T09:00:00Z",
        "exited_at": "2024-01-12T15:30:00Z",
        "decision": "approved",
        "duration_hours": 54.5,
        "decision_maker": "user_456"
      },
      {
        "stage_id": "phone_screen",
        "entered_at": "2024-01-12T15:30:00Z",
        "exited_at": "2024-01-15T10:30:00Z",
        "decision": "approved",
        "duration_hours": 67.0,
        "decision_maker": "user_789"
      }
    ],
    "next_actions": [
      {
        "action": "schedule_interview",
        "due_date": "2024-01-17T17:00:00Z",
        "assignee": "user_456"
      }
    ]
  }
}
```

### Analytics API

#### Get Hiring Metrics
```http
GET /api/v1/analytics/hiring-metrics
Query Parameters:
  - start_date: ISO date
  - end_date: ISO date
  - department: string
  - job_ids: comma-separated UUIDs
  - group_by: string (daily|weekly|monthly)

Response:
{
  "data": {
    "period": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    },
    "metrics": {
      "applications_received": 450,
      "candidates_screened": 180,
      "interviews_conducted": 85,
      "offers_made": 12,
      "hires_completed": 8,
      "time_to_hire": {
        "avg_days": 28.5,
        "median_days": 25,
        "p90_days": 45
      },
      "conversion_rates": {
        "application_to_screen": 0.40,
        "screen_to_interview": 0.47,
        "interview_to_offer": 0.14,
        "offer_to_hire": 0.67
      },
      "cost_per_hire": 3250.00
    },
    "trends": [
      {
        "date": "2024-01-01",
        "applications": 15,
        "hires": 0
      }
    ]
  }
}
```

#### Get AHP Performance Analytics
```http
GET /api/v1/analytics/ahp-performance/{hierarchy_id}
Query Parameters:
  - period_start: ISO date
  - period_end: ISO date

Response:
{
  "data": {
    "hierarchy_id": "ahp_123",
    "period": {
      "start": "2024-01-01",
      "end": "2024-01-31"
    },
    "performance_metrics": {
      "total_candidates_scored": 156,
      "hires_made": 8,
      "prediction_accuracy": 0.73,
      "ranking_accuracy": 0.81,
      "top_10_precision": 0.89
    },
    "attribute_analysis": {
      "technical_experience": {
        "ahp_weight": 0.40,
        "actual_importance": 0.35,
        "correlation_with_success": 0.68
      },
      "leadership_experience": {
        "ahp_weight": 0.30,
        "actual_importance": 0.38,
        "correlation_with_success": 0.72
      }
    },
    "recommendations": [
      {
        "type": "weight_adjustment",
        "attribute": "technical_experience",
        "current_weight": 0.40,
        "suggested_weight": 0.35,
        "confidence": 0.82
      }
    ]
  }
}
```

### Notification API

#### Send Notification
```http
POST /api/v1/notifications/send
Content-Type: application/json

{
  "template_id": "interview_scheduled",
  "recipients": [
    {
      "user_id": "user_123",
      "channels": ["email", "push"]
    }
  ],
  "context": {
    "candidate_name": "Jane Smith",
    "interview_date": "2024-01-20T14:00:00Z",
    "interview_type": "Technical Interview",
    "zoom_link": "https://zoom.us/j/123456789"
  },
  "priority": "normal",
  "send_at": "2024-01-19T09:00:00Z"
}

Response:
{
  "data": {
    "notification_id": "notif_123",
    "status": "queued",
    "scheduled_for": "2024-01-19T09:00:00Z",
    "recipients_count": 1,
    "estimated_delivery": "2024-01-19T09:05:00Z"
  }
}
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more fields contain invalid data",
    "details": [
      {
        "field": "email",
        "code": "INVALID_FORMAT",
        "message": "Email address is not in valid format"
      }
    ],
    "request_id": "req_123456789",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Common Error Codes
```http
400 Bad Request - VALIDATION_ERROR
401 Unauthorized - AUTHENTICATION_REQUIRED
403 Forbidden - INSUFFICIENT_PERMISSIONS
404 Not Found - RESOURCE_NOT_FOUND
409 Conflict - RESOURCE_CONFLICT
422 Unprocessable Entity - BUSINESS_RULE_VIOLATION
429 Too Many Requests - RATE_LIMIT_EXCEEDED
500 Internal Server Error - INTERNAL_ERROR
503 Service Unavailable - SERVICE_UNAVAILABLE
```

## Rate Limiting

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642262400
X-RateLimit-Window: 3600
```

### Rate Limit Tiers
```yaml
Public Endpoints: 100 requests/hour per IP
Authenticated Users: 1000 requests/hour per user
Premium Users: 5000 requests/hour per user
Admin Users: 10000 requests/hour per user
```

## Webhooks

### Webhook Configuration
```http
POST /api/v1/webhooks
Content-Type: application/json

{
  "url": "https://your-app.com/webhooks/ats",
  "events": [
    "candidate.scored",
    "interview.completed",
    "workflow.advanced",
    "hire.completed"
  ],
  "secret": "webhook_secret_key",
  "active": true
}
```

### Webhook Payload Example
```json
{
  "id": "webhook_123",
  "event": "candidate.scored",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "candidate_id": "candidate_123",
    "job_id": "job_123",
    "score": 84.5,
    "profile_matches": [...]
  },
  "signature": "sha256=..."
}
```

## API Testing

### Postman Collection Structure
```json
{
  "info": {
    "name": "ATS API",
    "version": "1.0.0"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{access_token}}"
      }
    ]
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://api.ats.com"
    }
  ]
}
```

### Test Scenarios
```yaml
Authentication Tests:
  - Valid login with different providers
  - Token refresh functionality
  - Invalid credentials handling
  - Rate limiting on auth endpoints

CRUD Operations:
  - Create, read, update, delete for all resources
  - Input validation testing
  - Permission-based access testing
  - Pagination and filtering

Business Logic Tests:
  - AHP score calculations
  - Workflow state transitions
  - Interview scheduling logic
  - Analytics calculations

Integration Tests:
  - Calendar integrations
  - File upload and processing
  - Email notifications
  - Webhook delivery
```

This comprehensive API specification provides a complete reference for implementing and integrating with the ATS system, ensuring consistent, reliable, and well-documented endpoints for all functionality.
