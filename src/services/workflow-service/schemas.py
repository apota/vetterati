from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class WorkflowStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class InterviewType(str, Enum):
    PHONE = "phone"
    VIDEO = "video"
    ONSITE = "onsite"
    PANEL = "panel"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"

class InterviewStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"

# Base schemas
class WorkflowTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    department: Optional[str] = None
    job_level: Optional[str] = None
    states: List[Dict[str, Any]] = []
    transitions: Dict[str, Any] = {}
    default_timeouts: Dict[str, int] = {}
    is_active: bool = True

class WorkflowTemplateCreate(WorkflowTemplateBase):
    created_by: str

class WorkflowTemplateResponse(WorkflowTemplateBase):
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CandidateWorkflowBase(BaseModel):
    candidate_id: str
    job_id: str
    template_id: Optional[str] = None
    current_state: str = "applied"
    workflow_data: Dict[str, Any] = {}
    status: WorkflowStatus = WorkflowStatus.ACTIVE

class CandidateWorkflowCreate(CandidateWorkflowBase):
    pass

class CandidateWorkflowUpdate(BaseModel):
    current_state: Optional[str] = None
    workflow_data: Optional[Dict[str, Any]] = None
    status: Optional[WorkflowStatus] = None
    estimated_completion: Optional[datetime] = None

class CandidateWorkflowResponse(CandidateWorkflowBase):
    id: str
    previous_state: Optional[str] = None
    state_history: List[Dict[str, Any]] = []
    progress_percentage: float = 0.0
    estimated_completion: Optional[datetime] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InterviewStepBase(BaseModel):
    workflow_id: str
    interview_type: InterviewType
    round_number: int = 1
    title: Optional[str] = None
    description: Optional[str] = None
    interviewer_ids: List[str] = []
    additional_participants: List[Dict[str, Any]] = []
    interview_questions: List[Dict[str, Any]] = []
    evaluation_criteria: List[Dict[str, Any]] = []

class InterviewStepCreate(InterviewStepBase):
    pass

class InterviewStepUpdate(BaseModel):
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    meeting_url: Optional[str] = None
    meeting_id: Optional[str] = None
    meeting_password: Optional[str] = None
    location: Optional[str] = None
    status: Optional[InterviewStatus] = None
    feedback: Optional[List[Dict[str, Any]]] = None
    scores: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class InterviewStepResponse(InterviewStepBase):
    id: str
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    meeting_url: Optional[str] = None
    meeting_id: Optional[str] = None
    location: Optional[str] = None
    feedback: List[Dict[str, Any]] = []
    scores: Dict[str, Any] = {}
    status: InterviewStatus = InterviewStatus.PENDING
    notes: Optional[str] = None
    attachments: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WorkflowStateTransitionRequest(BaseModel):
    action: str
    metadata: Dict[str, Any] = {}
    notes: Optional[str] = None
    triggered_by: Optional[str] = None

class WorkflowAnalyticsResponse(BaseModel):
    total_workflows: int
    active_workflows: int
    completed_workflows: int
    average_completion_time_days: float
    state_distribution: Dict[str, int]
    interview_completion_rate: float
    bottleneck_states: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    time_period: Dict[str, Any]

class NotificationRequest(BaseModel):
    workflow_id: str
    notification_type: str
    recipient_type: str
    recipient_id: str
    subject: str
    message: str
    channel: NotificationChannel = NotificationChannel.EMAIL
    scheduled_for: Optional[datetime] = None
    template_name: Optional[str] = None
    metadata: Dict[str, Any] = {}

class InterviewSchedulingRequest(BaseModel):
    interview_id: str
    scheduled_start: datetime
    scheduled_end: datetime
    interviewer_ids: List[str]
    meeting_type: str = "video"  # video, phone, onsite
    location: Optional[str] = None
    send_notifications: bool = True
    calendar_integration: bool = True

class BulkWorkflowActionRequest(BaseModel):
    workflow_ids: List[str]
    action: str
    metadata: Dict[str, Any] = {}
    notes: Optional[str] = None

class WorkflowMetrics(BaseModel):
    workflow_id: str
    candidate_id: str
    job_id: str
    current_state: str
    days_in_current_state: int
    total_days_in_workflow: int
    progress_percentage: float
    next_deadline: Optional[datetime] = None
    risk_score: float  # Risk of workflow stalling or candidate dropping out

class WorkflowReportRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    job_ids: Optional[List[str]] = None
    departments: Optional[List[str]] = None
    workflow_states: Optional[List[str]] = None
    include_candidate_details: bool = False
    include_interview_feedback: bool = False
    format: str = "json"  # json, csv, pdf
