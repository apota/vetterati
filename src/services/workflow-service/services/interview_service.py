from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import logging

from models import InterviewStep, CandidateWorkflow
from schemas import InterviewStepCreate, InterviewStepUpdate, InterviewStepResponse

logger = logging.getLogger(__name__)

class InterviewService:
    """Service for managing interview steps"""
    
    async def create_interview(
        self, 
        db: AsyncSession, 
        interview_data: InterviewStepCreate
    ) -> InterviewStep:
        """Create a new interview step"""
        try:
            interview = InterviewStep(
                workflow_id=uuid.UUID(interview_data.workflow_id),
                interview_type=interview_data.interview_type.value,
                round_number=interview_data.round_number,
                title=interview_data.title,
                description=interview_data.description,
                interviewer_ids=interview_data.interviewer_ids,
                additional_participants=interview_data.additional_participants,
                interview_questions=interview_data.interview_questions,
                evaluation_criteria=interview_data.evaluation_criteria
            )
            
            db.add(interview)
            await db.commit()
            await db.refresh(interview)
            
            logger.info(f"Created interview {interview.id} for workflow {interview_data.workflow_id}")
            return interview
            
        except Exception as e:
            logger.error(f"Error creating interview: {e}")
            await db.rollback()
            raise
    
    async def get_interview(self, db: AsyncSession, interview_id: str) -> Optional[InterviewStep]:
        """Get interview by ID"""
        result = await db.execute(
            select(InterviewStep).where(InterviewStep.id == uuid.UUID(interview_id))
        )
        return result.scalar_one_or_none()
    
    async def list_workflow_interviews(
        self, 
        db: AsyncSession, 
        workflow_id: str
    ) -> List[InterviewStep]:
        """List interviews for a workflow"""
        result = await db.execute(
            select(InterviewStep)
            .where(InterviewStep.workflow_id == uuid.UUID(workflow_id))
            .order_by(InterviewStep.round_number, InterviewStep.created_at)
        )
        return result.scalars().all()
    
    async def update_interview(
        self, 
        db: AsyncSession, 
        interview_id: str,
        interview_data: InterviewStepUpdate
    ) -> Optional[InterviewStep]:
        """Update interview step"""
        try:
            interview = await self.get_interview(db, interview_id)
            if not interview:
                return None
            
            # Update fields
            if interview_data.scheduled_start:
                interview.scheduled_start = interview_data.scheduled_start
            if interview_data.scheduled_end:
                interview.scheduled_end = interview_data.scheduled_end
            if interview_data.meeting_url:
                interview.meeting_url = interview_data.meeting_url
            if interview_data.meeting_id:
                interview.meeting_id = interview_data.meeting_id
            if interview_data.meeting_password:
                interview.meeting_password = interview_data.meeting_password
            if interview_data.location:
                interview.location = interview_data.location
            if interview_data.status:
                interview.status = interview_data.status.value
            if interview_data.feedback:
                interview.feedback = interview_data.feedback
            if interview_data.scores:
                interview.scores = interview_data.scores
            if interview_data.notes:
                interview.notes = interview_data.notes
            
            interview.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(interview)
            
            logger.info(f"Updated interview {interview_id}")
            return interview
            
        except Exception as e:
            logger.error(f"Error updating interview: {e}")
            await db.rollback()
            raise
    
    async def schedule_interview(
        self, 
        db: AsyncSession, 
        interview_id: str,
        scheduling_data: Dict[str, Any]
    ) -> bool:
        """Schedule an interview"""
        try:
            interview = await self.get_interview(db, interview_id)
            if not interview:
                return False
            
            # Update scheduling information
            interview.scheduled_start = datetime.fromisoformat(scheduling_data.get("start_time"))
            interview.scheduled_end = datetime.fromisoformat(scheduling_data.get("end_time"))
            interview.meeting_url = scheduling_data.get("meeting_url")
            interview.meeting_id = scheduling_data.get("meeting_id")
            interview.meeting_password = scheduling_data.get("meeting_password")
            interview.location = scheduling_data.get("location")
            interview.status = "scheduled"
            
            # Update interviewer list if provided
            if "interviewer_ids" in scheduling_data:
                interview.interviewer_ids = scheduling_data["interviewer_ids"]
            
            interview.updated_at = datetime.utcnow()
            
            await db.commit()
            
            logger.info(f"Scheduled interview {interview_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling interview: {e}")
            await db.rollback()
            raise
    
    async def start_interview(self, db: AsyncSession, interview_id: str) -> bool:
        """Start an interview"""
        try:
            interview = await self.get_interview(db, interview_id)
            if not interview:
                return False
            
            interview.actual_start = datetime.utcnow()
            interview.status = "in_progress"
            interview.updated_at = datetime.utcnow()
            
            await db.commit()
            
            logger.info(f"Started interview {interview_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting interview: {e}")
            await db.rollback()
            raise
    
    async def complete_interview(
        self, 
        db: AsyncSession, 
        interview_id: str,
        feedback: List[Dict[str, Any]],
        scores: Dict[str, Any]
    ) -> bool:
        """Complete an interview with feedback and scores"""
        try:
            interview = await self.get_interview(db, interview_id)
            if not interview:
                return False
            
            interview.actual_end = datetime.utcnow()
            interview.status = "completed"
            interview.feedback = feedback
            interview.scores = scores
            interview.updated_at = datetime.utcnow()
            
            await db.commit()
            
            logger.info(f"Completed interview {interview_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error completing interview: {e}")
            await db.rollback()
            raise
    
    async def cancel_interview(
        self, 
        db: AsyncSession, 
        interview_id: str,
        reason: str
    ) -> bool:
        """Cancel an interview"""
        try:
            interview = await self.get_interview(db, interview_id)
            if not interview:
                return False
            
            interview.status = "cancelled"
            interview.notes = f"Cancelled: {reason}"
            interview.updated_at = datetime.utcnow()
            
            await db.commit()
            
            logger.info(f"Cancelled interview {interview_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling interview: {e}")
            await db.rollback()
            raise
    
    async def get_upcoming_interviews(
        self, 
        db: AsyncSession,
        hours_ahead: int = 24
    ) -> List[InterviewStep]:
        """Get interviews scheduled in the next N hours"""
        cutoff_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=hours_ahead)
        
        result = await db.execute(
            select(InterviewStep)
            .where(
                InterviewStep.status == "scheduled",
                InterviewStep.scheduled_start <= cutoff_time,
                InterviewStep.scheduled_start >= datetime.utcnow()
            )
            .order_by(InterviewStep.scheduled_start)
        )
        return result.scalars().all()
    
    async def get_interviewer_schedule(
        self, 
        db: AsyncSession,
        interviewer_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[InterviewStep]:
        """Get an interviewer's schedule for a date range"""
        result = await db.execute(
            select(InterviewStep)
            .where(
                InterviewStep.interviewer_ids.contains([interviewer_id]),
                InterviewStep.scheduled_start >= start_date,
                InterviewStep.scheduled_start <= end_date,
                InterviewStep.status.in_(["scheduled", "in_progress"])
            )
            .order_by(InterviewStep.scheduled_start)
        )
        return result.scalars().all()
