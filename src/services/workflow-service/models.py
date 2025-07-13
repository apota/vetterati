from sqlalchemy import Column, String, DateTime, Text, JSON, Boolean, Integer, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from database import Base

class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    department = Column(String(100))
    job_level = Column(String(50))
    
    # Workflow configuration
    states = Column(JSON)  # Array of workflow states
    transitions = Column(JSON)  # State transition rules
    default_timeouts = Column(JSON)  # Default timeouts for each state
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CandidateWorkflow(Base):
    __tablename__ = "candidate_workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), nullable=False)
    job_id = Column(UUID(as_uuid=True), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("workflow_templates.id"))
    
    # Current state
    current_state = Column(String(100), nullable=False, default="applied")
    previous_state = Column(String(100))
    
    # Workflow data
    workflow_data = Column(JSON)  # Dynamic data for the workflow
    state_history = Column(JSON)  # History of state changes
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    estimated_completion = Column(DateTime)
    
    # Status
    status = Column(String(50), default="active")  # active, completed, cancelled, on_hold
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    template = relationship("WorkflowTemplate")
    interview_steps = relationship("InterviewStep", back_populates="workflow")

class InterviewStep(Base):
    __tablename__ = "interview_steps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("candidate_workflows.id"), nullable=False)
    
    # Interview details
    interview_type = Column(String(50), nullable=False)  # phone, video, onsite, panel
    round_number = Column(Integer, default=1)
    title = Column(String(200))
    description = Column(Text)
    
    # Scheduling
    scheduled_start = Column(DateTime)
    scheduled_end = Column(DateTime)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    
    # Participants
    interviewer_ids = Column(JSON)  # Array of interviewer user IDs
    additional_participants = Column(JSON)  # Other participants
    
    # Meeting details
    meeting_url = Column(String(500))
    meeting_id = Column(String(200))
    meeting_password = Column(String(100))
    location = Column(String(500))
    
    # Content and evaluation
    interview_questions = Column(JSON)  # Array of questions
    evaluation_criteria = Column(JSON)  # Evaluation criteria
    feedback = Column(JSON)  # Interviewer feedback
    scores = Column(JSON)  # Interview scores
    
    # Status
    status = Column(String(50), default="pending")  # pending, scheduled, in_progress, completed, cancelled
    
    # Metadata
    notes = Column(Text)
    attachments = Column(JSON)  # File attachments
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workflow = relationship("CandidateWorkflow", back_populates="interview_steps")

class WorkflowState(Base):
    __tablename__ = "workflow_states"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("candidate_workflows.id"), nullable=False)
    
    # State information
    state_name = Column(String(100), nullable=False)
    entered_at = Column(DateTime, default=datetime.utcnow)
    exited_at = Column(DateTime)
    duration_minutes = Column(Integer)
    
    # State data
    state_data = Column(JSON)  # Data specific to this state
    actions_taken = Column(JSON)  # Actions performed in this state
    
    # Automation
    automated_action = Column(String(200))  # Automated action triggered
    automated_at = Column(DateTime)
    
    # Metadata
    triggered_by = Column(UUID(as_uuid=True))  # User who triggered the state change
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkflowNotification(Base):
    __tablename__ = "workflow_notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("candidate_workflows.id"))
    
    # Notification details
    notification_type = Column(String(100), nullable=False)  # state_change, reminder, deadline
    recipient_type = Column(String(50), nullable=False)  # candidate, interviewer, hr, manager
    recipient_id = Column(UUID(as_uuid=True))
    
    # Content
    subject = Column(String(500))
    message = Column(Text)
    template_name = Column(String(200))
    
    # Delivery
    channel = Column(String(50))  # email, sms, push, slack
    delivery_status = Column(String(50), default="pending")  # pending, sent, delivered, failed
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # Scheduling
    scheduled_for = Column(DateTime)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Notification metadata
    notification_metadata = Column(JSON)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
