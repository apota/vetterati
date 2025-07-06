from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging
from contextlib import asynccontextmanager

from database import get_db, init_db
from models import CandidateWorkflow, InterviewStep, WorkflowTemplate, WorkflowState
from schemas import (
    CandidateWorkflowResponse,
    CandidateWorkflowCreate,
    CandidateWorkflowUpdate,
    InterviewStepResponse,
    InterviewStepCreate,
    WorkflowTemplateResponse,
    WorkflowTemplateCreate,
    WorkflowStateTransitionRequest,
    WorkflowAnalyticsResponse
)
from services.workflow_service import WorkflowService
from services.interview_service import InterviewService
from services.notification_service import NotificationService
from services.state_machine_service import StateMachineService
from config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Workflow Management Service...")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down Workflow Management Service...")

app = FastAPI(
    title="Workflow Management Service",
    description="Candidate workflow and interview management system",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
workflow_service = WorkflowService()
interview_service = InterviewService()
notification_service = NotificationService()
state_machine_service = StateMachineService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "workflow-management"}

# Workflow endpoints
@app.post("/workflows", response_model=CandidateWorkflowResponse)
async def create_workflow(
    workflow_data: CandidateWorkflowCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new candidate workflow"""
    try:
        workflow = await workflow_service.create_workflow(db, workflow_data)
        return workflow
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create workflow")

@app.get("/workflows/{workflow_id}", response_model=CandidateWorkflowResponse)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get workflow by ID"""
    workflow = await workflow_service.get_workflow(db, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@app.get("/workflows", response_model=List[CandidateWorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    candidate_id: Optional[str] = None,
    job_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List workflows with filtering"""
    workflows = await workflow_service.list_workflows(
        db, skip, limit, status, candidate_id, job_id
    )
    return workflows

@app.put("/workflows/{workflow_id}", response_model=CandidateWorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow_data: CandidateWorkflowUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update workflow"""
    try:
        workflow = await workflow_service.update_workflow(db, workflow_id, workflow_data)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow
    except Exception as e:
        logger.error(f"Error updating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update workflow")

@app.post("/workflows/{workflow_id}/transition")
async def transition_workflow_state(
    workflow_id: str,
    transition_request: WorkflowStateTransitionRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Transition workflow to next state"""
    try:
        success = await state_machine_service.transition_state(
            db, workflow_id, transition_request.action, transition_request.metadata
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Invalid state transition")
        
        # Send notifications in background
        background_tasks.add_task(
            notification_service.send_workflow_notification,
            workflow_id,
            transition_request.action
        )
        
        return {"message": "State transition successful"}
    except Exception as e:
        logger.error(f"Error transitioning workflow state: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to transition state")

# Interview endpoints
@app.post("/interviews", response_model=InterviewStepResponse)
async def create_interview(
    interview_data: InterviewStepCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new interview step"""
    try:
        interview = await interview_service.create_interview(db, interview_data)
        return interview
    except Exception as e:
        logger.error(f"Error creating interview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create interview")

@app.get("/interviews/{interview_id}", response_model=InterviewStepResponse)
async def get_interview(
    interview_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get interview by ID"""
    interview = await interview_service.get_interview(db, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

@app.get("/workflows/{workflow_id}/interviews", response_model=List[InterviewStepResponse])
async def list_workflow_interviews(
    workflow_id: str,
    db: AsyncSession = Depends(get_db)
):
    """List interviews for a workflow"""
    interviews = await interview_service.list_workflow_interviews(db, workflow_id)
    return interviews

@app.post("/interviews/{interview_id}/schedule")
async def schedule_interview(
    interview_id: str,
    scheduling_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Schedule an interview"""
    try:
        success = await interview_service.schedule_interview(db, interview_id, scheduling_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to schedule interview")
        
        # Send scheduling notifications in background
        background_tasks.add_task(
            notification_service.send_interview_notification,
            interview_id,
            "scheduled"
        )
        
        return {"message": "Interview scheduled successfully"}
    except Exception as e:
        logger.error(f"Error scheduling interview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to schedule interview")

# Template endpoints
@app.post("/templates", response_model=WorkflowTemplateResponse)
async def create_template(
    template_data: WorkflowTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new workflow template"""
    try:
        template = await workflow_service.create_template(db, template_data)
        return template
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create template")

@app.get("/templates", response_model=List[WorkflowTemplateResponse])
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List workflow templates"""
    templates = await workflow_service.list_templates(db, skip, limit)
    return templates

@app.get("/templates/{template_id}", response_model=WorkflowTemplateResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get template by ID"""
    template = await workflow_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

# Analytics endpoints
@app.get("/analytics/workflows", response_model=WorkflowAnalyticsResponse)
async def get_workflow_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    job_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get workflow analytics"""
    try:
        analytics = await workflow_service.get_analytics(
            db, start_date, end_date, job_id
        )
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
