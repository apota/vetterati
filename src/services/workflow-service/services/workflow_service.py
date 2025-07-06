from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import logging

from models import CandidateWorkflow, WorkflowTemplate, WorkflowState, InterviewStep
from schemas import (
    CandidateWorkflowCreate, 
    CandidateWorkflowUpdate,
    CandidateWorkflowResponse,
    WorkflowTemplateCreate,
    WorkflowTemplateResponse,
    WorkflowAnalyticsResponse
)

logger = logging.getLogger(__name__)

class WorkflowService:
    """Service for managing candidate workflows"""
    
    async def create_workflow(
        self, 
        db: AsyncSession, 
        workflow_data: CandidateWorkflowCreate
    ) -> CandidateWorkflow:
        """Create a new candidate workflow"""
        try:
            # Check if workflow already exists for this candidate and job
            existing = await db.execute(
                select(CandidateWorkflow).where(
                    CandidateWorkflow.candidate_id == uuid.UUID(workflow_data.candidate_id),
                    CandidateWorkflow.job_id == uuid.UUID(workflow_data.job_id)
                )
            )
            
            if existing.scalar_one_or_none():
                raise ValueError("Workflow already exists for this candidate and job")
            
            # Create workflow
            workflow = CandidateWorkflow(
                candidate_id=uuid.UUID(workflow_data.candidate_id),
                job_id=uuid.UUID(workflow_data.job_id),
                template_id=uuid.UUID(workflow_data.template_id) if workflow_data.template_id else None,
                current_state=workflow_data.current_state,
                workflow_data=workflow_data.workflow_data,
                status=workflow_data.status.value,
                state_history=[{
                    "state": workflow_data.current_state,
                    "entered_at": datetime.utcnow().isoformat(),
                    "action": "workflow_created"
                }]
            )
            
            db.add(workflow)
            await db.commit()
            await db.refresh(workflow)
            
            # Create initial state record
            initial_state = WorkflowState(
                workflow_id=workflow.id,
                state_name=workflow_data.current_state,
                state_data={"initial": True},
                triggered_by=uuid.UUID(workflow_data.candidate_id)  # Simplified
            )
            
            db.add(initial_state)
            await db.commit()
            
            logger.info(f"Created workflow {workflow.id} for candidate {workflow_data.candidate_id}")
            return workflow
            
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            await db.rollback()
            raise
    
    async def get_workflow(self, db: AsyncSession, workflow_id: str) -> Optional[CandidateWorkflow]:
        """Get workflow by ID"""
        result = await db.execute(
            select(CandidateWorkflow)
            .options(selectinload(CandidateWorkflow.interview_steps))
            .where(CandidateWorkflow.id == uuid.UUID(workflow_id))
        )
        return result.scalar_one_or_none()
    
    async def list_workflows(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        candidate_id: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> List[CandidateWorkflow]:
        """List workflows with filtering"""
        query = select(CandidateWorkflow)
        
        if status:
            query = query.where(CandidateWorkflow.status == status)
        if candidate_id:
            query = query.where(CandidateWorkflow.candidate_id == uuid.UUID(candidate_id))
        if job_id:
            query = query.where(CandidateWorkflow.job_id == uuid.UUID(job_id))
        
        query = query.offset(skip).limit(limit).order_by(CandidateWorkflow.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_workflow(
        self, 
        db: AsyncSession, 
        workflow_id: str,
        workflow_data: CandidateWorkflowUpdate
    ) -> Optional[CandidateWorkflow]:
        """Update workflow"""
        try:
            workflow = await self.get_workflow(db, workflow_id)
            if not workflow:
                return None
            
            # Update fields
            if workflow_data.current_state:
                # Add to state history
                if not workflow.state_history:
                    workflow.state_history = []
                
                workflow.state_history.append({
                    "state": workflow_data.current_state,
                    "previous_state": workflow.current_state,
                    "entered_at": datetime.utcnow().isoformat(),
                    "action": "state_updated"
                })
                
                workflow.previous_state = workflow.current_state
                workflow.current_state = workflow_data.current_state
            
            if workflow_data.workflow_data:
                workflow.workflow_data = {**(workflow.workflow_data or {}), **workflow_data.workflow_data}
            
            if workflow_data.status:
                workflow.status = workflow_data.status.value
                
                if workflow_data.status.value == "completed":
                    workflow.completed_at = datetime.utcnow()
                    workflow.progress_percentage = 100.0
            
            if workflow_data.estimated_completion:
                workflow.estimated_completion = workflow_data.estimated_completion
            
            workflow.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(workflow)
            
            logger.info(f"Updated workflow {workflow_id}")
            return workflow
            
        except Exception as e:
            logger.error(f"Error updating workflow: {e}")
            await db.rollback()
            raise
    
    async def delete_workflow(self, db: AsyncSession, workflow_id: str) -> bool:
        """Delete workflow"""
        try:
            result = await db.execute(
                delete(CandidateWorkflow).where(CandidateWorkflow.id == uuid.UUID(workflow_id))
            )
            await db.commit()
            
            success = result.rowcount > 0
            if success:
                logger.info(f"Deleted workflow {workflow_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error deleting workflow: {e}")
            await db.rollback()
            raise
    
    # Template management
    async def create_template(
        self, 
        db: AsyncSession, 
        template_data: WorkflowTemplateCreate
    ) -> WorkflowTemplate:
        """Create workflow template"""
        try:
            template = WorkflowTemplate(
                name=template_data.name,
                description=template_data.description,
                department=template_data.department,
                job_level=template_data.job_level,
                states=template_data.states,
                transitions=template_data.transitions,
                default_timeouts=template_data.default_timeouts,
                is_active=template_data.is_active,
                created_by=uuid.UUID(template_data.created_by)
            )
            
            db.add(template)
            await db.commit()
            await db.refresh(template)
            
            logger.info(f"Created workflow template {template.id}")
            return template
            
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            await db.rollback()
            raise
    
    async def get_template(self, db: AsyncSession, template_id: str) -> Optional[WorkflowTemplate]:
        """Get template by ID"""
        result = await db.execute(
            select(WorkflowTemplate).where(WorkflowTemplate.id == uuid.UUID(template_id))
        )
        return result.scalar_one_or_none()
    
    async def list_templates(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[WorkflowTemplate]:
        """List workflow templates"""
        result = await db.execute(
            select(WorkflowTemplate)
            .where(WorkflowTemplate.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(WorkflowTemplate.name)
        )
        return result.scalars().all()
    
    # Analytics
    async def get_analytics(
        self, 
        db: AsyncSession,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> WorkflowAnalyticsResponse:
        """Get workflow analytics"""
        try:
            # Base query
            query = select(CandidateWorkflow)
            
            # Apply filters
            if start_date:
                start_dt = datetime.fromisoformat(start_date)
                query = query.where(CandidateWorkflow.created_at >= start_dt)
            
            if end_date:
                end_dt = datetime.fromisoformat(end_date)
                query = query.where(CandidateWorkflow.created_at <= end_dt)
            
            if job_id:
                query = query.where(CandidateWorkflow.job_id == uuid.UUID(job_id))
            
            # Get workflows
            result = await db.execute(query)
            workflows = result.scalars().all()
            
            # Calculate metrics
            total_workflows = len(workflows)
            active_workflows = len([w for w in workflows if w.status == "active"])
            completed_workflows = len([w for w in workflows if w.status == "completed"])
            
            # Calculate average completion time
            completed = [w for w in workflows if w.completed_at and w.started_at]
            if completed:
                completion_times = [
                    (w.completed_at - w.started_at).days 
                    for w in completed
                ]
                avg_completion_time = sum(completion_times) / len(completion_times)
            else:
                avg_completion_time = 0.0
            
            # State distribution
            state_dist = {}
            for workflow in workflows:
                state = workflow.current_state
                state_dist[state] = state_dist.get(state, 0) + 1
            
            # Interview completion rate
            total_interviews = await db.execute(
                select(func.count(InterviewStep.id))
                .join(CandidateWorkflow)
                .where(CandidateWorkflow.id.in_([w.id for w in workflows]))
            )
            total_interviews = total_interviews.scalar() or 0
            
            completed_interviews = await db.execute(
                select(func.count(InterviewStep.id))
                .join(CandidateWorkflow)
                .where(
                    CandidateWorkflow.id.in_([w.id for w in workflows]),
                    InterviewStep.status == "completed"
                )
            )
            completed_interviews = completed_interviews.scalar() or 0
            
            interview_completion_rate = (
                completed_interviews / total_interviews * 100 
                if total_interviews > 0 else 0
            )
            
            return WorkflowAnalyticsResponse(
                total_workflows=total_workflows,
                active_workflows=active_workflows,
                completed_workflows=completed_workflows,
                average_completion_time_days=avg_completion_time,
                state_distribution=state_dist,
                interview_completion_rate=interview_completion_rate,
                bottleneck_states=[],  # TODO: Implement bottleneck analysis
                performance_metrics={
                    "conversion_rate": completed_workflows / total_workflows * 100 if total_workflows > 0 else 0,
                    "active_rate": active_workflows / total_workflows * 100 if total_workflows > 0 else 0
                },
                time_period={
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            raise
