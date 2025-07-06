# Interview & Workflow Management Design

## Overview
This document outlines the design for the interview scheduling and workflow management subsystem, including calendar integration, automated workflows, and notification systems.

## Architecture

### Workflow Pipeline
```
Application → Screening → Interview Stages → Decision → Offer → Hire/Reject
```

### Core Components

#### 1. Workflow Engine
- **State Machine**: Configurable hiring pipeline states
- **Rule Engine**: Automated transitions and decision logic
- **Event Driven**: Pub/Sub architecture for workflow events
- **Parallel Paths**: Support for multiple interview tracks

#### 2. Interview Scheduler
- **Calendar Integration**: Google Calendar, Outlook, Office 365
- **Availability Management**: Real-time availability checking
- **Smart Scheduling**: AI-powered optimal time slot selection
- **Room/Resource Booking**: Conference room and equipment reservation

#### 3. Notification Service
- **Multi-Channel**: Email, SMS, in-app, push notifications
- **Template Engine**: Customizable notification templates
- **Scheduling**: Reminder notifications with configurable timing
- **Escalation**: Automated escalation for missed actions

## Data Models

### Workflow Definition
```json
{
  "id": "uuid",
  "name": "Senior Engineer Hiring Process",
  "version": "1.2",
  "jobIds": ["uuid"],
  "isActive": true,
  "stages": [
    {
      "id": "application",
      "name": "Application Review",
      "type": "manual|automated|hybrid",
      "order": 1,
      "config": {
        "autoAdvance": false,
        "requiredActions": ["resume_review", "ats_score_review"],
        "timeoutDays": 3,
        "assignees": ["recruiter"],
        "criteria": {
          "minAHPScore": 70,
          "requiredSkills": ["javascript", "react"]
        }
      },
      "transitions": [
        {
          "toStage": "phone_screen",
          "condition": "approved",
          "autoTrigger": false
        },
        {
          "toStage": "rejected",
          "condition": "rejected",
          "autoTrigger": true
        }
      ]
    },
    {
      "id": "phone_screen",
      "name": "Phone Screening",
      "type": "interview",
      "order": 2,
      "config": {
        "duration": 30,
        "interviewType": "phone",
        "requiredInterviewers": 1,
        "defaultInterviewers": ["recruiter"],
        "questions": ["technical_basics", "culture_fit"],
        "scoringCriteria": ["communication", "technical_knowledge"]
      }
    }
  ],
  "notifications": {
    "stageTransition": true,
    "interviewScheduled": true,
    "reminderTiming": [24, 2] // hours before
  },
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

### Candidate Workflow Instance
```json
{
  "id": "uuid",
  "candidateId": "uuid",
  "jobId": "uuid",
  "workflowDefinitionId": "uuid",
  "currentStage": "phone_screen",
  "status": "in_progress|completed|rejected|withdrawn",
  "startedAt": "timestamp",
  "updatedAt": "timestamp",
  "stageHistory": [
    {
      "stageId": "application",
      "enteredAt": "timestamp",
      "exitedAt": "timestamp",
      "decision": "approved",
      "decisionMaker": "user_id",
      "notes": "Strong technical background",
      "duration": 7200, // seconds
      "artifacts": ["resume_review_id", "ats_score_id"]
    }
  ],
  "metadata": {
    "source": "job_board|referral|direct",
    "priority": "high|medium|low",
    "tags": ["urgent", "diverse_candidate"]
  }
}
```

### Interview Entity
```json
{
  "id": "uuid",
  "candidateWorkflowId": "uuid",
  "candidateId": "uuid",
  "jobId": "uuid",
  "stageId": "technical_interview",
  "title": "Technical Interview - Senior Engineer",
  "description": "Deep dive into technical skills and problem solving",
  "type": "phone|video|onsite|panel",
  "status": "scheduled|in_progress|completed|cancelled|no_show",
  "scheduling": {
    "scheduledStart": "timestamp",
    "scheduledEnd": "timestamp",
    "actualStart": "timestamp",
    "actualEnd": "timestamp",
    "timezone": "America/New_York",
    "location": "Conference Room A / Zoom Link",
    "calendarEventIds": {
      "google": "calendar_event_id",
      "outlook": "outlook_event_id"
    }
  },
  "participants": {
    "interviewers": [
      {
        "userId": "uuid",
        "name": "John Doe",
        "role": "primary|secondary|observer",
        "email": "john@company.com",
        "acceptedAt": "timestamp",
        "status": "accepted|pending|declined"
      }
    ],
    "candidate": {
      "name": "Jane Smith",
      "email": "jane@email.com",
      "phone": "+1234567890",
      "confirmationStatus": "confirmed|pending|declined"
    }
  },
  "content": {
    "interviewGuide": "interview_guide_id",
    "questions": ["question_id_1", "question_id_2"],
    "materials": ["resume.pdf", "portfolio_link"],
    "notes": "Candidate has strong React experience"
  },
  "evaluation": {
    "overallScore": 4.2,
    "dimensionScores": {
      "technical_skills": 4.5,
      "communication": 4.0,
      "culture_fit": 4.0,
      "problem_solving": 4.3
    },
    "recommendation": "strong_hire|hire|no_hire|strong_no_hire",
    "feedback": "Excellent technical depth, good communication",
    "interviewerNotes": ["detailed_notes_id"],
    "completed": true,
    "submittedAt": "timestamp"
  },
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

### Calendar Integration
```json
{
  "id": "uuid",
  "userId": "uuid",
  "provider": "google|outlook|office365",
  "calendarId": "primary",
  "accessToken": "encrypted_token",
  "refreshToken": "encrypted_refresh_token",
  "tokenExpiry": "timestamp",
  "isActive": true,
  "permissions": ["read", "write"],
  "config": {
    "defaultDuration": 60,
    "bufferTime": 15,
    "workingHours": {
      "monday": {"start": "09:00", "end": "17:00"},
      "friday": {"start": "09:00", "end": "17:00"}
    },
    "timezone": "America/New_York",
    "autoDecline": true
  }
}
```

## Workflow Engine Implementation

### State Machine
```python
class WorkflowStateMachine:
    def __init__(self, workflow_definition):
        self.definition = workflow_definition
        self.states = {stage.id: stage for stage in workflow_definition.stages}
        self.transitions = self.build_transition_map()
    
    def advance_stage(self, workflow_instance, decision, user_id):
        """Advance workflow to next stage based on decision"""
        current_stage = self.states[workflow_instance.current_stage]
        
        # Find valid transition
        transition = self.find_transition(current_stage, decision)
        if not transition:
            raise InvalidTransitionError(f"No transition for decision: {decision}")
        
        # Execute stage exit logic
        self.execute_stage_exit(workflow_instance, current_stage, decision, user_id)
        
        # Update workflow instance
        workflow_instance.current_stage = transition.to_stage
        workflow_instance.updated_at = datetime.utcnow()
        
        # Execute stage entry logic
        next_stage = self.states[transition.to_stage]
        self.execute_stage_entry(workflow_instance, next_stage)
        
        # Trigger notifications
        self.trigger_notifications(workflow_instance, transition)
        
        return workflow_instance
    
    def execute_stage_entry(self, workflow_instance, stage):
        """Execute entry logic for new stage"""
        if stage.type == "interview":
            self.schedule_interview(workflow_instance, stage)
        elif stage.config.get("autoAdvance"):
            self.evaluate_auto_advance(workflow_instance, stage)
```

### Automated Rules Engine
```python
class WorkflowRulesEngine:
    def evaluate_stage_criteria(self, candidate, job, stage_config):
        """Evaluate if candidate meets stage advancement criteria"""
        criteria = stage_config.get("criteria", {})
        
        evaluations = []
        
        # AHP Score requirement
        if "minAHPScore" in criteria:
            ahp_score = self.get_candidate_ahp_score(candidate.id, job.id)
            meets_ahp = ahp_score >= criteria["minAHPScore"]
            evaluations.append(("ahp_score", meets_ahp, ahp_score))
        
        # Required skills
        if "requiredSkills" in criteria:
            candidate_skills = set(self.get_candidate_skills(candidate.id))
            required_skills = set(criteria["requiredSkills"])
            meets_skills = required_skills.issubset(candidate_skills)
            evaluations.append(("required_skills", meets_skills, candidate_skills))
        
        # Experience requirements
        if "minYearsExperience" in criteria:
            years_exp = self.get_candidate_experience_years(candidate.id)
            meets_experience = years_exp >= criteria["minYearsExperience"]
            evaluations.append(("experience", meets_experience, years_exp))
        
        return {
            "passes": all(evaluation[1] for evaluation in evaluations),
            "details": evaluations
        }
    
    def evaluate_timeout_actions(self, workflow_instance, stage):
        """Check if stage has timed out and execute timeout actions"""
        timeout_days = stage.config.get("timeoutDays")
        if not timeout_days:
            return
        
        stage_entry_time = self.get_stage_entry_time(workflow_instance, stage.id)
        time_in_stage = datetime.utcnow() - stage_entry_time
        
        if time_in_stage.days >= timeout_days:
            timeout_action = stage.config.get("timeoutAction", "escalate")
            self.execute_timeout_action(workflow_instance, stage, timeout_action)
```

## Interview Scheduling System

### Calendar Integration Service
```python
class CalendarIntegrationService:
    def __init__(self):
        self.providers = {
            "google": GoogleCalendarProvider(),
            "outlook": OutlookCalendarProvider(),
            "office365": Office365CalendarProvider()
        }
    
    def find_available_slots(self, participant_emails, duration, date_range):
        """Find common available time slots for all participants"""
        all_availability = []
        
        for email in participant_emails:
            user_calendar = self.get_user_calendar_config(email)
            provider = self.providers[user_calendar.provider]
            
            availability = provider.get_availability(
                user_calendar.calendar_id,
                date_range.start,
                date_range.end,
                user_calendar.access_token
            )
            all_availability.append(availability)
        
        # Find intersection of all availability
        common_slots = self.find_common_availability(
            all_availability, 
            duration
        )
        
        return self.rank_time_slots(common_slots, participant_emails)
    
    def schedule_interview(self, interview):
        """Create calendar events for all participants"""
        calendar_events = []
        
        for participant in interview.participants.interviewers:
            user_calendar = self.get_user_calendar_config(participant.email)
            provider = self.providers[user_calendar.provider]
            
            event = provider.create_event(
                calendar_id=user_calendar.calendar_id,
                title=interview.title,
                start_time=interview.scheduling.scheduled_start,
                end_time=interview.scheduling.scheduled_end,
                attendees=[p.email for p in interview.participants.all],
                description=self.build_interview_description(interview),
                access_token=user_calendar.access_token
            )
            
            calendar_events.append({
                "provider": user_calendar.provider,
                "event_id": event.id,
                "participant": participant.email
            })
        
        return calendar_events
```

### Smart Scheduling Algorithm
```python
class SmartScheduler:
    def rank_time_slots(self, available_slots, participants):
        """Rank time slots based on optimization criteria"""
        scored_slots = []
        
        for slot in available_slots:
            score = 0
            
            # Prefer slots during working hours
            if self.is_working_hours(slot):
                score += 10
            
            # Avoid early morning or late evening
            if self.is_optimal_time(slot):
                score += 5
            
            # Consider participant preferences
            for participant in participants:
                pref_score = self.get_participant_preference_score(participant, slot)
                score += pref_score
            
            # Avoid back-to-back meetings
            if not self.has_buffer_time(slot, participants):
                score -= 3
            
            scored_slots.append({
                "slot": slot,
                "score": score,
                "reasons": self.get_scoring_reasons(slot, participants)
            })
        
        return sorted(scored_slots, key=lambda x: x["score"], reverse=True)
    
    def suggest_optimal_duration(self, interview_type, role_level):
        """Suggest interview duration based on type and role"""
        duration_matrix = {
            ("phone_screen", "junior"): 30,
            ("phone_screen", "senior"): 45,
            ("technical", "junior"): 60,
            ("technical", "senior"): 90,
            ("panel", "senior"): 120,
            ("cultural_fit", "any"): 45
        }
        
        return duration_matrix.get((interview_type, role_level), 60)
```

## Notification System

### Multi-Channel Notification Service
```python
class NotificationService:
    def __init__(self):
        self.channels = {
            "email": EmailNotificationChannel(),
            "sms": SMSNotificationChannel(),
            "push": PushNotificationChannel(),
            "in_app": InAppNotificationChannel()
        }
        self.template_engine = NotificationTemplateEngine()
    
    def send_workflow_notification(self, event_type, workflow_instance, recipients):
        """Send notifications for workflow events"""
        notification_config = self.get_notification_config(
            workflow_instance.workflow_definition_id,
            event_type
        )
        
        if not notification_config.enabled:
            return
        
        for recipient in recipients:
            user_preferences = self.get_user_notification_preferences(recipient.user_id)
            preferred_channels = self.determine_channels(
                notification_config.channels,
                user_preferences,
                event_type
            )
            
            for channel in preferred_channels:
                message = self.template_engine.render_template(
                    template_id=notification_config.template_id,
                    context={
                        "candidate": workflow_instance.candidate,
                        "job": workflow_instance.job,
                        "stage": workflow_instance.current_stage,
                        "recipient": recipient
                    }
                )
                
                self.channels[channel].send(recipient, message)
    
    def schedule_reminder_notifications(self, interview):
        """Schedule reminder notifications for upcoming interviews"""
        reminder_times = interview.workflow_stage.config.get("reminderTiming", [24, 2])
        
        for hours_before in reminder_times:
            reminder_time = interview.scheduled_start - timedelta(hours=hours_before)
            
            if reminder_time > datetime.utcnow():
                self.schedule_notification(
                    send_at=reminder_time,
                    event_type="interview_reminder",
                    interview=interview,
                    recipients=interview.participants.all
                )
```

### Template Engine
```python
class NotificationTemplateEngine:
    def __init__(self):
        self.jinja_env = Environment(loader=FileSystemLoader("templates"))
    
    def render_template(self, template_id, context):
        """Render notification template with context data"""
        template_config = self.get_template_config(template_id)
        template = self.jinja_env.get_template(template_config.template_file)
        
        rendered_content = template.render(**context)
        
        return {
            "subject": self.render_subject(template_config.subject_template, context),
            "body": rendered_content,
            "format": template_config.format  # html, text, markdown
        }
    
    def get_template_config(self, template_id):
        """Get template configuration from database"""
        return TemplateConfig.query.filter_by(id=template_id).first()
```

## Workflow Analytics

### Performance Metrics
```python
class WorkflowAnalytics:
    def calculate_stage_metrics(self, workflow_definition_id, date_range):
        """Calculate performance metrics for each workflow stage"""
        workflows = self.get_completed_workflows(workflow_definition_id, date_range)
        
        stage_metrics = {}
        
        for stage in workflow_definition.stages:
            stage_data = []
            
            for workflow in workflows:
                stage_history = self.get_stage_history(workflow.id, stage.id)
                if stage_history:
                    stage_data.append({
                        "duration": stage_history.duration,
                        "decision": stage_history.decision,
                        "workflow_id": workflow.id
                    })
            
            stage_metrics[stage.id] = {
                "name": stage.name,
                "total_candidates": len(stage_data),
                "avg_duration": self.calculate_average_duration(stage_data),
                "conversion_rate": self.calculate_conversion_rate(stage_data),
                "bottleneck_score": self.calculate_bottleneck_score(stage_data),
                "decision_distribution": self.calculate_decision_distribution(stage_data)
            }
        
        return stage_metrics
    
    def identify_workflow_bottlenecks(self, workflow_definition_id):
        """Identify stages that are slowing down the hiring process"""
        metrics = self.calculate_stage_metrics(workflow_definition_id)
        
        bottlenecks = []
        
        for stage_id, metrics_data in metrics.items():
            bottleneck_indicators = {
                "long_duration": metrics_data["avg_duration"] > self.get_benchmark_duration(stage_id),
                "low_conversion": metrics_data["conversion_rate"] < 0.5,
                "high_timeout_rate": self.calculate_timeout_rate(stage_id) > 0.1
            }
            
            if any(bottleneck_indicators.values()):
                bottlenecks.append({
                    "stage_id": stage_id,
                    "stage_name": metrics_data["name"],
                    "indicators": bottleneck_indicators,
                    "severity": self.calculate_bottleneck_severity(bottleneck_indicators)
                })
        
        return sorted(bottlenecks, key=lambda x: x["severity"], reverse=True)
```

## API Design

### Workflow Management
```http
POST /api/v1/workflows/definitions
{
  "name": "Senior Engineer Process",
  "stages": [...],
  "notifications": {...}
}

GET /api/v1/workflows/definitions/{id}

PUT /api/v1/workflows/definitions/{id}/stages/{stageId}

POST /api/v1/candidates/{candidateId}/workflows
{
  "job_id": "uuid",
  "workflow_definition_id": "uuid"
}

POST /api/v1/workflows/{workflowId}/advance
{
  "decision": "approved|rejected",
  "notes": "Strong technical background",
  "artifacts": ["review_id"]
}
```

### Interview Scheduling
```http
POST /api/v1/interviews
{
  "candidate_workflow_id": "uuid",
  "stage_id": "technical_interview",
  "type": "video",
  "duration": 90,
  "interviewers": ["user1", "user2"],
  "preferred_times": ["2024-01-15T14:00:00Z", "2024-01-16T10:00:00Z"]
}

GET /api/v1/users/{userId}/availability
Query: start_date, end_date, duration

PUT /api/v1/interviews/{id}/reschedule
{
  "new_start_time": "timestamp",
  "reason": "Interviewer conflict"
}

POST /api/v1/interviews/{id}/evaluation
{
  "overall_score": 4.2,
  "dimension_scores": {...},
  "recommendation": "hire",
  "feedback": "Excellent technical skills"
}
```

### Notifications
```http
GET /api/v1/notifications/preferences/{userId}

PUT /api/v1/notifications/preferences/{userId}
{
  "channels": ["email", "in_app"],
  "interview_reminders": true,
  "workflow_updates": true
}

POST /api/v1/notifications/send
{
  "template_id": "interview_scheduled",
  "recipients": ["user1", "user2"],
  "context": {...}
}
```

### Analytics
```http
GET /api/v1/workflows/analytics/{workflowDefinitionId}
Query: date_range, metrics

GET /api/v1/workflows/analytics/bottlenecks/{workflowDefinitionId}

GET /api/v1/interviews/analytics/utilization
Query: date_range, interviewer_ids
```

## Integration Points

### Calendar Providers
- **Google Calendar API**: OAuth 2.0, real-time notifications
- **Microsoft Graph API**: Outlook/Office 365 integration
- **Exchange Web Services**: On-premise Exchange servers

### Communication Platforms
- **Slack**: Workflow notifications, interview reminders
- **Microsoft Teams**: Calendar integration, notifications
- **Zoom**: Automatic video conference creation
- **WebEx**: Enterprise video conferencing

### HRIS Systems
- **Workday**: Employee data synchronization
- **BambooHR**: Onboarding workflow integration
- **ADP**: Offer management and onboarding
